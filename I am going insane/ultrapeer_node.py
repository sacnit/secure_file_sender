# ultrapeer_node.py
# Implements the Ultrapeer server logic.

import socket
import ssl
import threading
import logging
import time
import json
from collections import defaultdict

from crypto_utils import (
    generate_rsa_key_pair, serialize_key,
    generate_self_signed_cert, create_ssl_context
)
from network_utils import send_message, receive_message
from config import DEFAULT_HOST, BUFFER_SIZE

logger = logging.getLogger(__name__)

class UltrapeerNode:
    def __init__(self, host, leaf_port, up_port=None, known_ultrapeers=None):
        self.host = host
        self.leaf_port = leaf_port
        self.up_port = up_port # Port for other Ultrapeers to connect

        self.private_key, self.public_key = generate_rsa_key_pair()
        self.public_key_pem = serialize_key(self.public_key, is_private=False) # For identification if needed
        self.private_key_pem = serialize_key(self.private_key)

        self.cert_pem = generate_self_signed_cert(self.host, self.private_key, self.public_key)

        # Thread-safe leaf registry: { "public_key_pem": {"ip": "...", "p2p_port": ..., "conn_time": ...} }
        self.leaf_registry = {}
        self.registry_lock = threading.Lock()

        # Connections to other Ultrapeers: { "host:port_string": {"socket": sock, "writer_thread": thread} }
        self.connected_ultrapeers = {} 
        self.ultrapeer_lock = threading.Lock()
        self.known_ultrapeers_to_connect = known_ultrapeers or [] # List of ("host", port)

        self.shutdown_event = threading.Event()

        # Sockets
        self.leaf_server_socket = None
        self.up_server_socket = None


    def _start_listening_for_leafs(self):
        """Listens for connections from Leaf peers."""
        try:
            self.leaf_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.leaf_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            server_ssl_context = create_ssl_context(is_server=True, cert_pem=self.cert_pem, key_pem=self.private_key_pem)
            
            self.leaf_server_socket.bind((self.host, self.leaf_port))
            self.leaf_server_socket.listen(10) # Listen for up to 10 leaf connections
            logger.info(f"Ultrapeer: Listening for Leafs on {self.host}:{self.leaf_port}")

            while not self.shutdown_event.is_set():
                try:
                    self.leaf_server_socket.settimeout(1.0) # Timeout to check shutdown_event
                    conn, addr = self.leaf_server_socket.accept()
                    ssl_conn = server_ssl_context.wrap_socket(conn, server_side=True)
                    logger.info(f"Ultrapeer: Accepted Leaf connection from {addr}")
                    
                    thread = threading.Thread(target=self._handle_leaf_client, args=(ssl_conn, addr), daemon=True)
                    thread.start()
                except socket.timeout:
                    continue
                except Exception as e:
                    if not self.shutdown_event.is_set():
                         logger.error(f"Ultrapeer: Error accepting Leaf connection: {e}")
                    break # Exit listening loop on other errors
        except Exception as e:
            logger.error(f"Ultrapeer: Could not start Leaf listener: {e}")
        finally:
            if self.leaf_server_socket:
                self.leaf_server_socket.close()
            logger.info("Ultrapeer: Leaf listener stopped.")

    def _handle_leaf_client(self, leaf_sock, leaf_addr):
        """Handles messages from a connected Leaf peer."""
        logger.info(f"Ultrapeer: Leaf client handler started for {leaf_addr}")
        leaf_public_key_pem = None # To identify the leaf for deregistration
        client_ip = leaf_addr[0]

        try:
            while not self.shutdown_event.is_set():
                message = receive_message(leaf_sock)
                if message is None: # Connection closed or error
                    logger.info(f"Ultrapeer: Leaf {leaf_addr} disconnected or error.")
                    break
                
                msg_type = message.get("type")

                if msg_type == "REGISTER_LEAF":
                    leaf_public_key_pem = message.get("public_key_pem")
                    leaf_p2p_port = message.get("p2p_port")
                    if leaf_public_key_pem and isinstance(leaf_p2p_port, int):
                        with self.registry_lock:
                            self.leaf_registry[leaf_public_key_pem] = {
                                "ip": client_ip,
                                "p2p_port": leaf_p2p_port, # This is the port Leaf listens on
                                "public_key_pem": leaf_public_key_pem, # Store full key for queries
                                "conn_time": time.time()
                            }
                        logger.info(f"Ultrapeer: Registered Leaf {leaf_public_key_pem[:30]}... from {client_ip} on P2P port {leaf_p2p_port}")
                        send_message(leaf_sock, {"type": "REGISTER_ACK", "status": "success"})
                        # Broadcast this new leaf to other ultrapeers
                        self._broadcast_to_ultrapeers({
                            "type": "SYNC_LEAF_JOINED",
                            "leaf_info": {
                                "public_key_pem": leaf_public_key_pem,
                                "ip": client_ip,
                                "p2p_port": leaf_p2p_port
                            }
                        })
                    else:
                        logger.warning(f"Ultrapeer: Invalid registration from {leaf_addr}: {message}")
                        send_message(leaf_sock, {"type": "REGISTER_ACK", "status": "failure", "reason": "Invalid registration data"})
                        break # Invalid registration, close connection

                elif msg_type == "QUERY_LEAF":
                    target_pk_pem = message.get("target_public_key_pem")
                    found_peer_info = None
                    with self.registry_lock:
                        found_peer_info = self.leaf_registry.get(target_pk_pem)
                    
                    if found_peer_info:
                        logger.info(f"Ultrapeer: Query for {target_pk_pem[:30]}... successful. Found: {found_peer_info}")
                        send_message(leaf_sock, {"type": "QUERY_LEAF_RESPONSE", "status": "found", "peer_info": found_peer_info})
                    else:
                        logger.info(f"Ultrapeer: Query for {target_pk_pem[:30]}... not found.")
                        send_message(leaf_sock, {"type": "QUERY_LEAF_RESPONSE", "status": "not_found", "reason": "Peer not in registry"})
                
                # elif msg_type == "LEAF_LEAVING": # Graceful disconnect
                #     logger.info(f"Ultrapeer: Leaf {leaf_public_key_pem[:30]}... is leaving.")
                #     break # Will be handled by finally block

                else:
                    logger.warning(f"Ultrapeer: Unknown message type from Leaf {leaf_addr}: {msg_type}")

        except ConnectionResetError:
            logger.warning(f"Ultrapeer: Connection reset by Leaf {leaf_addr}.")
        except Exception as e:
            logger.error(f"Ultrapeer: Error handling Leaf {leaf_addr}: {e}")
        finally:
            if leaf_public_key_pem: # If leaf was registered
                with self.registry_lock:
                    if leaf_public_key_pem in self.leaf_registry:
                        del self.leaf_registry[leaf_public_key_pem]
                        logger.info(f"Ultrapeer: De-registered Leaf {leaf_public_key_pem[:30]}...")
                        # Broadcast this leaf removal to other ultrapeers
                        self._broadcast_to_ultrapeers({
                            "type": "SYNC_LEAF_LEFT",
                            "public_key_pem": leaf_public_key_pem
                        })
            try:
                leaf_sock.close()
            except: pass
            logger.info(f"Ultrapeer: Leaf client handler for {leaf_addr} (PK: {leaf_public_key_pem[:30] if leaf_public_key_pem else 'N/A'}) ended.")

    def _start_listening_for_ultrapeers(self):
        """Listens for connections from other Ultrapeers (if up_port is set)."""
        if not self.up_port:
            return # Not configured to listen for other Ultrapeers

        try:
            self.up_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.up_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            server_ssl_context = create_ssl_context(is_server=True, cert_pem=self.cert_pem, key_pem=self.private_key_pem)
            
            self.up_server_socket.bind((self.host, self.up_port))
            self.up_server_socket.listen(5)
            logger.info(f"Ultrapeer: Listening for other Ultrapeers on {self.host}:{self.up_port}")

            while not self.shutdown_event.is_set():
                try:
                    self.up_server_socket.settimeout(1.0)
                    conn, addr = self.up_server_socket.accept()
                    ssl_conn = server_ssl_context.wrap_socket(conn, server_side=True)
                    logger.info(f"Ultrapeer: Accepted Ultrapeer connection from {addr}")
                    
                    # Add to connected ultrapeers and start handler
                    # The handler will also manage sending initial sync data
                    self._add_ultrapeer_connection(ssl_conn, addr, is_initiator=False)
                except socket.timeout:
                    continue
                except Exception as e:
                    if not self.shutdown_event.is_set():
                        logger.error(f"Ultrapeer: Error accepting Ultrapeer connection: {e}")
                    break
        except Exception as e:
            logger.error(f"Ultrapeer: Could not start Ultrapeer listener: {e}")
        finally:
            if self.up_server_socket:
                self.up_server_socket.close()
            logger.info("Ultrapeer: Ultrapeer listener stopped.")

    def _connect_to_known_ultrapeers(self):
        """Attempts to connect to pre-configured known Ultrapeers."""
        for peer_host, peer_port in self.known_ultrapeers_to_connect:
            if self.shutdown_event.is_set(): break
            # Avoid connecting to self if listed, or already connected
            # A more robust check would involve unique IDs for ultrapeers
            peer_addr_str = f"{peer_host}:{peer_port}"
            with self.ultrapeer_lock:
                if peer_addr_str in self.connected_ultrapeers:
                    logger.info(f"Ultrapeer: Already connected to or connecting to {peer_addr_str}, skipping.")
                    continue
            
            try:
                logger.info(f"Ultrapeer: Attempting to connect to known Ultrapeer {peer_host}:{peer_port}")
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_ssl_context = create_ssl_context(is_server=False)
                # server_hostname can be the IP if DNS name is not used/verified
                ssl_sock = client_ssl_context.wrap_socket(sock, server_hostname=peer_host)
                ssl_sock.connect((peer_host, peer_port))
                logger.info(f"Ultrapeer: Connected to Ultrapeer {peer_host}:{peer_port}")
                self._add_ultrapeer_connection(ssl_sock, (peer_host, peer_port), is_initiator=True)
            except Exception as e:
                logger.error(f"Ultrapeer: Failed to connect to Ultrapeer {peer_host}:{peer_port}: {e}")
                # Could implement retry logic here

    def _add_ultrapeer_connection(self, up_sock, up_addr, is_initiator):
        """Adds and manages a new Ultrapeer connection."""
        peer_addr_str = f"{up_addr[0]}:{up_addr[1]}"
        with self.ultrapeer_lock:
            if peer_addr_str in self.connected_ultrapeers: # Should not happen if checks are done prior
                logger.warning(f"Ultrapeer: Connection to {peer_addr_str} already exists. Closing new one.")
                try: up_sock.close()
                except: pass
                return

            handler_thread = threading.Thread(target=self._handle_ultrapeer_messages, args=(up_sock, up_addr, is_initiator), daemon=True)
            self.connected_ultrapeers[peer_addr_str] = {"socket": up_sock, "thread": handler_thread, "address": up_addr}
            handler_thread.start()
            logger.info(f"Ultrapeer: Connection with Ultrapeer {peer_addr_str} established. Handler started.")

    def _handle_ultrapeer_messages(self, up_sock, up_addr, initiated_by_us):
        """Handles messages from/to another Ultrapeer and performs initial sync."""
        peer_addr_str = f"{up_addr[0]}:{up_addr[1]}"
        logger.info(f"Ultrapeer: Message handler started for UP {peer_addr_str}")

        # Perform initial synchronization
        # Send our current registry
        with self.registry_lock:
            initial_sync_data = {"type": "SYNC_FULL_REGISTRY", "registry": dict(self.leaf_registry)}
        
        if not send_message(up_sock, initial_sync_data):
            logger.error(f"Ultrapeer: Failed to send initial sync to {peer_addr_str}. Closing connection.")
            self._remove_ultrapeer_connection(peer_addr_str, up_sock)
            return

        logger.info(f"Ultrapeer: Sent initial full registry to {peer_addr_str}")

        try:
            while not self.shutdown_event.is_set():
                message = receive_message(up_sock)
                if message is None:
                    logger.info(f"Ultrapeer: Connection with {peer_addr_str} closed or error.")
                    break
                
                msg_type = message.get("type")
                logger.debug(f"Ultrapeer: Received message from UP {peer_addr_str}: {msg_type}")

                if msg_type == "SYNC_FULL_REGISTRY":
                    their_registry = message.get("registry", {})
                    logger.info(f"Ultrapeer: Received full registry from {peer_addr_str} with {len(their_registry)} entries.")
                    with self.registry_lock:
                        for pk_pem, info in their_registry.items():
                            if pk_pem not in self.leaf_registry: # Add if new
                                self.leaf_registry[pk_pem] = info
                                logger.debug(f"Ultrapeer: Synced (added) leaf {pk_pem[:20]} from {peer_addr_str}")
                            # More complex merge logic (e.g., timestamps) could be added here if needed
                            # For now, if it exists, we assume our local copy (if any) is more up-to-date
                            # or that the originating Ultrapeer is the source of truth.
                            # This simple merge prefers existing entries.
                
                elif msg_type == "SYNC_LEAF_JOINED":
                    leaf_info = message.get("leaf_info")
                    if leaf_info and "public_key_pem" in leaf_info:
                        pk_pem = leaf_info["public_key_pem"]
                        with self.registry_lock:
                            if pk_pem not in self.leaf_registry: # Only add if new to prevent loops
                                self.leaf_registry[pk_pem] = leaf_info
                                logger.info(f"Ultrapeer: Synced (joined) leaf {pk_pem[:20]} from {peer_addr_str}")
                                # Re-broadcast to other UPs *except* the sender
                                self._broadcast_to_ultrapeers(message, exclude_peer_addr=up_addr)
                            else:
                                logger.debug(f"Ultrapeer: Received SYNC_LEAF_JOINED for existing leaf {pk_pem[:20]} from {peer_addr_str}. Ignored.")
                    else:
                        logger.warning(f"Ultrapeer: Invalid SYNC_LEAF_JOINED from {peer_addr_str}: {message}")

                elif msg_type == "SYNC_LEAF_LEFT":
                    pk_pem = message.get("public_key_pem")
                    if pk_pem:
                        with self.registry_lock:
                            if pk_pem in self.leaf_registry:
                                del self.leaf_registry[pk_pem]
                                logger.info(f"Ultrapeer: Synced (left) leaf {pk_pem[:20]} from {peer_addr_str}")
                                # Re-broadcast
                                self._broadcast_to_ultrapeers(message, exclude_peer_addr=up_addr)
                            else:
                                logger.debug(f"Ultrapeer: Received SYNC_LEAF_LEFT for non-existent leaf {pk_pem[:20]} from {peer_addr_str}. Ignored.")
                    else:
                        logger.warning(f"Ultrapeer: Invalid SYNC_LEAF_LEFT from {peer_addr_str}: {message}")
                else:
                    logger.warning(f"Ultrapeer: Unknown message type from UP {peer_addr_str}: {msg_type}")

        except ConnectionResetError:
            logger.warning(f"Ultrapeer: Connection reset by UP {peer_addr_str}.")
        except Exception as e:
            logger.error(f"Ultrapeer: Error handling UP {peer_addr_str}: {e}")
        finally:
            self._remove_ultrapeer_connection(peer_addr_str, up_sock)
            logger.info(f"Ultrapeer: Message handler for UP {peer_addr_str} ended.")

    def _remove_ultrapeer_connection(self, peer_addr_str, sock_to_close):
        with self.ultrapeer_lock:
            if peer_addr_str in self.connected_ultrapeers:
                del self.connected_ultrapeers[peer_addr_str]
                logger.info(f"Ultrapeer: Removed connection to UP {peer_addr_str}")
        try:
            sock_to_close.close()
        except: pass


    def _broadcast_to_ultrapeers(self, message, exclude_peer_addr=None):
        """Sends a message to all connected Ultrapeers, optionally excluding one."""
        with self.ultrapeer_lock:
            # Create a copy of items to iterate over, as dict might change if a connection drops
            peers_to_broadcast = list(self.connected_ultrapeers.items()) 
        
        logger.debug(f"Ultrapeer: Broadcasting message: {message.get('type')}. Total UPs: {len(peers_to_broadcast)}")
        for peer_addr_str, up_data in peers_to_broadcast:
            if exclude_peer_addr and up_data["address"] == exclude_peer_addr:
                logger.debug(f"Ultrapeer: Skipping broadcast to sender {peer_addr_str} for message {message.get('type')}")
                continue
            
            up_sock = up_data["socket"]
            logger.debug(f"Ultrapeer: Sending to UP {peer_addr_str}: {message.get('type')}")
            if not send_message(up_sock, message):
                logger.warning(f"Ultrapeer: Failed to send broadcast to {peer_addr_str}. It might be disconnected.")
                # Consider removing this peer if send fails repeatedly, or rely on its handler to clean up.

    def start(self):
        """Starts the Ultrapeer node operations."""
        logger.info("Ultrapeer: Starting...")

        # Start listening for Leaf peers
        leaf_listener_thread = threading.Thread(target=self._start_listening_for_leafs, daemon=True)
        leaf_listener_thread.start()

        # Start listening for other Ultrapeers (if configured)
        if self.up_port:
            up_listener_thread = threading.Thread(target=self._start_listening_for_ultrapeers, daemon=True)
            up_listener_thread.start()
        
        # Connect to known Ultrapeers (if any)
        if self.known_ultrapeers_to_connect:
            # Run in a separate thread to not block main startup
            connect_thread = threading.Thread(target=self._connect_to_known_ultrapeers, daemon=True)
            connect_thread.start()

        logger.info("Ultrapeer: Node started. Listeners active.")
        logger.info("Type 'registry' to see current leaf registry.")
        logger.info("Type 'peers' to see connected ultrapeers.")
        logger.info("Type 'exit' to shutdown.")

        try:
            while not self.shutdown_event.is_set():
                try:
                    cmd_input = input("Ultrapeer> ").strip()
                    if not cmd_input:
                        continue
                    
                    if cmd_input == "exit":
                        break
                    elif cmd_input == "registry":
                        with self.registry_lock:
                            if not self.leaf_registry:
                                print("Leaf registry is empty.")
                            else:
                                print("Current Leaf Registry:")
                                for pk, info in self.leaf_registry.items():
                                    print(f"  - PK: {pk[:30]}... IP: {info['ip']}, P2P Port: {info['p2p_port']}")
                    elif cmd_input == "peers":
                        with self.ultrapeer_lock:
                            if not self.connected_ultrapeers:
                                print("Not connected to any other Ultrapeers.")
                            else:
                                print("Connected Ultrapeers:")
                                for addr_str, data in self.connected_ultrapeers.items():
                                    print(f"  - {addr_str} (Socket: {data['socket'].fileno() if data['socket'] else 'N/A'})")
                    else:
                        print(f"Unknown command: {cmd_input}")

                except EOFError: break
                except KeyboardInterrupt: break
                time.sleep(0.1)
        finally:
            self.stop()

    def stop(self):
        logger.info("Ultrapeer: Shutting down...")
        self.shutdown_event.set()

        # Close server sockets to stop accepting new connections
        if self.leaf_server_socket:
            try: self.leaf_server_socket.close()
            except: pass
        if self.up_server_socket:
            try: self.up_server_socket.close()
            except: pass
        
        # Close all connected Ultrapeer sockets
        with self.ultrapeer_lock:
            for peer_addr_str, up_data in list(self.connected_ultrapeers.items()): # Iterate on copy
                logger.info(f"Ultrapeer: Closing connection to UP {peer_addr_str}")
                try:
                    up_data["socket"].close()
                except Exception as e:
                    logger.error(f"Ultrapeer: Error closing socket to UP {peer_addr_str}: {e}")
            self.connected_ultrapeers.clear()

        # Wait for threads to finish (optional, as they are daemons but good for cleaner exit)
        # This part can be tricky if threads are blocked on I/O.
        # The shutdown_event should help them exit gracefully.
        # Forcing server sockets closed should unblock accept() calls.

        logger.info("Ultrapeer: Shutdown complete.")

