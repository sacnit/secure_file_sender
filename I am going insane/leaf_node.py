# leaf_node.py
# Implements the Leaf peer logic.

import socket
import ssl
import threading
import logging
import time
import json

from crypto_utils import (
    generate_rsa_key_pair, serialize_key, deserialize_public_key,
    generate_self_signed_cert, derive_port_from_public_key, create_ssl_context
)
from network_utils import send_message, receive_message
from config import DEFAULT_HOST, BUFFER_SIZE

logger = logging.getLogger(__name__)

class LeafNode:
    def __init__(self, ultrapeer_host, ultrapeer_port, node_host=DEFAULT_HOST):
        self.node_host = node_host # Host IP for listening for P2P
        self.ultrapeer_address = (ultrapeer_host, ultrapeer_port)
        
        self.private_key, self.public_key = generate_rsa_key_pair()
        self.public_key_pem = serialize_key(self.public_key, is_private=False)
        self.private_key_pem = serialize_key(self.private_key) # For SSL context

        self.derived_p2p_port = derive_port_from_public_key(self.public_key_pem)
        logger.info(f"Leaf: My Public Key: {self.public_key_pem[:30]}...")
        logger.info(f"Leaf: My P2P Listening Port (derived): {self.derived_p2p_port}")

        self.cert_pem = generate_self_signed_cert(self.node_host, self.private_key, self.public_key)
        
        self.ultrapeer_socket = None
        self.is_registered = False
        self.shutdown_event = threading.Event()

        # For incoming P2P connections
        self.p2p_server_socket = None
        self.active_p2p_connections = {} # pub_key_pem_hash -> socket

    def _connect_to_ultrapeer(self):
        """Establishes SSL connection to the Ultrapeer."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_ssl_context = create_ssl_context(is_server=False)
            self.ultrapeer_socket = client_ssl_context.wrap_socket(sock, server_hostname=self.ultrapeer_address[0])
            self.ultrapeer_socket.connect(self.ultrapeer_address)
            logger.info(f"Leaf: Connected to Ultrapeer {self.ultrapeer_address}")
            return True
        except Exception as e:
            logger.error(f"Leaf: Failed to connect to Ultrapeer {self.ultrapeer_address}: {e}")
            self.ultrapeer_socket = None
            return False

    def _register_with_ultrapeer(self):
        """Sends registration message to Ultrapeer."""
        if not self.ultrapeer_socket:
            logger.error("Leaf: Not connected to Ultrapeer, cannot register.")
            return False
        
        message = {
            "type": "REGISTER_LEAF",
            "public_key_pem": self.public_key_pem,
            # The Ultrapeer will get IP from socket, Leaf provides its derived P2P port
            "p2p_port": self.derived_p2p_port 
        }
        if send_message(self.ultrapeer_socket, message):
            response = receive_message(self.ultrapeer_socket)
            if response and response.get("type") == "REGISTER_ACK":
                if response.get("status") == "success":
                    self.is_registered = True
                    logger.info("Leaf: Successfully registered with Ultrapeer.")
                    return True
                else:
                    logger.error(f"Leaf: Registration failed: {response.get('reason')}")
            else:
                logger.error("Leaf: Invalid or no response from Ultrapeer during registration.")
        else:
            logger.error("Leaf: Failed to send registration message.")
        
        # If registration fails, disconnect
        self._disconnect_from_ultrapeer()
        return False

    def _disconnect_from_ultrapeer(self):
        if self.ultrapeer_socket:
            try:
                # Notify Ultrapeer about leaving (optional, graceful shutdown)
                # message = {"type": "LEAF_LEAVING", "public_key_pem": self.public_key_pem}
                # send_message(self.ultrapeer_socket, message)
                self.ultrapeer_socket.close()
            except Exception as e:
                logger.error(f"Leaf: Error closing Ultrapeer socket: {e}")
            finally:
                self.ultrapeer_socket = None
                self.is_registered = False
                logger.info("Leaf: Disconnected from Ultrapeer.")
                
    def _start_p2p_listening(self):
        """Starts listening for P2P connections from other Leafs."""
        try:
            self.p2p_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.p2p_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            server_ssl_context = create_ssl_context(is_server=True, cert_pem=self.cert_pem, key_pem=self.private_key_pem)
            
            self.p2p_server_socket.bind((self.node_host, self.derived_p2p_port))
            self.p2p_server_socket.listen(5)
            logger.info(f"Leaf: Listening for P2P connections on {self.node_host}:{self.derived_p2p_port}")

            while not self.shutdown_event.is_set():
                try:
                    self.p2p_server_socket.settimeout(1.0) # Timeout to check shutdown_event
                    conn, addr = self.p2p_server_socket.accept()
                    ssl_conn = server_ssl_context.wrap_socket(conn, server_side=True)
                    logger.info(f"Leaf: Accepted P2P connection from {addr}")
                    
                    # Handle P2P connection in a new thread
                    # For now, just log it. A real app would handle messages.
                    p2p_thread = threading.Thread(target=self._handle_p2p_client, args=(ssl_conn, addr), daemon=True)
                    p2p_thread.start()
                except socket.timeout:
                    continue # Loop to check shutdown_event
                except Exception as e:
                    if not self.shutdown_event.is_set(): # Avoid error if shutting down
                        logger.error(f"Leaf: Error accepting P2P connection: {e}")
                    break # Exit listening loop on other errors
        except Exception as e:
            logger.error(f"Leaf: Could not start P2P listener: {e}")
        finally:
            if self.p2p_server_socket:
                self.p2p_server_socket.close()
            logger.info("Leaf: P2P listener stopped.")

    def _handle_p2p_client(self, p2p_sock, addr):
        """Handles an incoming P2P connection from another Leaf."""
        logger.info(f"Leaf: P2P session started with {addr}")
        try:
            # Example: receive a message and echo it back
            while not self.shutdown_event.is_set():
                message = receive_message(p2p_sock)
                if message is None: # Connection closed or error
                    logger.info(f"Leaf: P2P connection with {addr} closed by peer or error.")
                    break
                
                logger.info(f"Leaf: Received P2P message from {addr}: {message}")
                
                # Simple echo for testing
                if message.get("type") == "PING":
                    send_message(p2p_sock, {"type": "PONG", "data": message.get("data")})
                elif message.get("type") == "CHAT":
                    print(f"[P2P Chat from {addr}]: {message.get('text')}")

        except Exception as e:
            logger.error(f"Leaf: Error in P2P session with {addr}: {e}")
        finally:
            try:
                p2p_sock.close()
            except: pass
            logger.info(f"Leaf: P2P session ended with {addr}")

    def query_peer(self, target_public_key_pem):
        """Queries the Ultrapeer for a target Leaf's connection info."""
        if not self.is_registered or not self.ultrapeer_socket:
            logger.error("Leaf: Not registered or connected to Ultrapeer. Cannot query.")
            return None

        message = {
            "type": "QUERY_LEAF",
            "target_public_key_pem": target_public_key_pem
        }
        if send_message(self.ultrapeer_socket, message):
            response = receive_message(self.ultrapeer_socket)
            if response and response.get("type") == "QUERY_LEAF_RESPONSE":
                if response.get("status") == "found":
                    peer_info = response.get("peer_info")
                    logger.info(f"Leaf: Peer found: {peer_info}")
                    return peer_info # {'ip': '...', 'p2p_port': ..., 'public_key_pem': '...'}
                else:
                    logger.warning(f"Leaf: Peer not found by Ultrapeer: {response.get('reason')}")
                    return None
            else:
                logger.error("Leaf: Invalid or no response from Ultrapeer for query.")
        else:
            logger.error("Leaf: Failed to send query message.")
        return None

    def connect_to_peer(self, peer_info):
        """Establishes a direct P2P SSL connection to another Leaf."""
        target_ip = peer_info.get("ip")
        # IMPORTANT: The port to connect to is derived from the TARGET's public key
        target_public_key_pem = peer_info.get("public_key_pem")
        if not target_public_key_pem:
            logger.error("Leaf: Target peer info missing public key PEM. Cannot derive port.")
            return None
            
        target_p2p_port = derive_port_from_public_key(target_public_key_pem)
        
        logger.info(f"Leaf: Attempting P2P connection to {target_ip}:{target_p2p_port} (derived from their pubkey)")

        try:
            p2p_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_ssl_context = create_ssl_context(is_server=False)
            # server_hostname can be the IP if DNS name is not used/verified for self-signed
            ssl_p2p_socket = client_ssl_context.wrap_socket(p2p_socket, server_hostname=target_ip) 
            ssl_p2p_socket.connect((target_ip, target_p2p_port))
            logger.info(f"Leaf: Successfully connected P2P to {target_ip}:{target_p2p_port}")
            
            # Store this connection or start interaction
            # For now, just return the socket for the caller to use
            # A more robust system would manage these connections
            return ssl_p2p_socket 
        except Exception as e:
            logger.error(f"Leaf: Failed to connect P2P to {target_ip}:{target_p2p_port}: {e}")
            return None

    def start(self):
        """Starts the Leaf node operations."""
        logger.info("Leaf: Starting...")
        if not self._connect_to_ultrapeer():
            logger.error("Leaf: Could not connect to Ultrapeer. Exiting.")
            return

        if not self._register_with_ultrapeer():
            logger.error("Leaf: Could not register with Ultrapeer. Exiting.")
            return

        # Start P2P listening thread
        p2p_listener_thread = threading.Thread(target=self._start_p2p_listening, daemon=True)
        p2p_listener_thread.start()
        
        logger.info("Leaf: Node started. P2P listener active. Registered with Ultrapeer.")
        logger.info("Type 'query <target_public_key_pem>' to find a peer.")
        logger.info("Type 'chat <target_public_key_pem> <message>' to send a P2P message.")
        logger.info("Type 'exit' to shutdown.")

        # Keep main thread alive for commands or until shutdown
        try:
            while not self.shutdown_event.is_set():
                # Simple command loop (can be replaced by a more sophisticated UI/input handling)
                try:
                    cmd_input = input("Leaf> ").strip()
                    if not cmd_input:
                        continue
                    
                    parts = cmd_input.split(" ", 2)
                    command = parts[0].lower()

                    if command == "exit":
                        break
                    elif command == "query" and len(parts) > 1:
                        target_key = parts[1]
                        peer_info = self.query_peer(target_key)
                        if peer_info:
                            print(f"Peer Info: IP={peer_info['ip']}, P2P_Port(their derived)={derive_port_from_public_key(peer_info['public_key_pem'])}, PubKey={peer_info['public_key_pem'][:30]}...")
                            # You could automatically try to connect here or let user do it.
                        else:
                            print("Peer not found or error during query.")
                    elif command == "connect" and len(parts) > 1: # For manual connect if you have full peer_info
                        # This is a bit manual, usually query would precede this
                        # Example: connect '{"ip": "127.0.0.1", "public_key_pem": "---BEGIN..."}'
                        try:
                            peer_info_str = parts[1]
                            peer_data = json.loads(peer_info_str)
                            conn_socket = self.connect_to_peer(peer_data)
                            if conn_socket:
                                print(f"Connected to peer. Socket: {conn_socket}. You can now send messages.")
                                # For simplicity, we're not managing this socket further in this loop.
                                # A real app would have a way to select this connection and send data.
                                # For now, let's send a test PING
                                send_message(conn_socket, {"type": "PING", "data": "Hello from Leaf!"})
                                response = receive_message(conn_socket)
                                print(f"Received from peer: {response}")
                                # conn_socket.close() # Or keep it open
                        except Exception as e:
                            print(f"Error processing connect command: {e}")
                    elif command == "chat" and len(parts) > 2:
                        target_key = parts[1]
                        chat_message = parts[2]
                        peer_info = self.query_peer(target_key)
                        if peer_info:
                            conn_socket = self.connect_to_peer(peer_info)
                            if conn_socket:
                                send_message(conn_socket, {"type": "CHAT", "text": chat_message})
                                print(f"Sent chat message to {target_key[:20]}...")
                                # In a real app, you'd wait for replies on the P2P listener thread.
                                # Or make this connection persistent and managed.
                                conn_socket.close() # Simple send and close for this example
                            else:
                                print(f"Could not connect to peer {target_key[:20]}... to send chat.")
                        else:
                            print(f"Could not find peer {target_key[:20]}... to chat with.")

                    else:
                        print(f"Unknown command: {cmd_input}")

                except EOFError: # Handle Ctrl+D
                    logger.info("EOF received, shutting down.")
                    break
                except KeyboardInterrupt: # Handle Ctrl+C
                    logger.info("Keyboard interrupt received, shutting down.")
                    break
                time.sleep(0.1) # Prevent busy-waiting in input loop

        finally:
            self.stop()

    def stop(self):
        logger.info("Leaf: Shutting down...")
        self.shutdown_event.set()
        self._disconnect_from_ultrapeer()
        
        if self.p2p_server_socket:
            try:
                # To unblock accept() if it's waiting
                # Create a dummy connection to itself if it's stuck in accept
                # This is a common trick to wake up a listening socket
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((self.node_host, self.derived_p2p_port))
            except: pass # Ignore errors, just trying to unblock
            finally:
                self.p2p_server_socket.close() # Listener thread should exit

        # Close any active P2P connections (if managed)
        # for sock in self.active_p2p_connections.values():
        # try: sock.close()
        # except: pass
            
        logger.info("Leaf: Shutdown complete.")

