# network_utils.py
# Utilities for network communication (message sending/receiving).

import json
import struct
import logging
from config import BUFFER_SIZE, MAX_MSG_LENGTH

logger = logging.getLogger(__name__)

def send_message(sock, message_data):
    """
    Serializes message_data to JSON, prefixes with 4-byte length, and sends.
    """
    try:
        json_payload = json.dumps(message_data).encode('utf-8')
        if len(json_payload) > MAX_MSG_LENGTH:
            logger.error(f"Message too long: {len(json_payload)} bytes")
            return False # Or raise an exception
            
        message_len = struct.pack('>I', len(json_payload)) # Pack length as 4-byte unsigned int
        sock.sendall(message_len + json_payload)
        logger.debug(f"Sent message: {message_data}")
        return True
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return False

def receive_message(sock):
    """
    Receives a 4-byte length prefix, then the JSON message.
    Returns the deserialized message (dict) or None on error/close.
    """
    try:
        # Read message length
        raw_msglen = recvall(sock, 4)
        if not raw_msglen:
            logger.info("Connection closed or no data received for length.")
            return None
        
        msglen = struct.unpack('>I', raw_msglen)[0]
        if msglen > MAX_MSG_LENGTH:
            logger.error(f"Incoming message too long: {msglen} bytes. Potential attack or error.")
            # Consume and discard potentially malicious large message to clear buffer
            # This is a basic way; more robust handling might be needed.
            while msglen > 0:
                chunk_size = min(msglen, BUFFER_SIZE)
                chunk = sock.recv(chunk_size)
                if not chunk: break # Connection lost
                msglen -= len(chunk)
            return None

        # Read the message data
        json_payload = recvall(sock, msglen)
        if not json_payload:
            logger.info("Connection closed or no data received for payload.")
            return None
        
        message_data = json.loads(json_payload.decode('utf-8'))
        logger.debug(f"Received message: {message_data}")
        return message_data
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}. Payload: {json_payload[:100] if 'json_payload' in locals() else 'N/A'}")
        return None
    except struct.error as e:
        logger.error(f"Struct unpack error (likely malformed length): {e}")
        return None
    except ConnectionResetError:
        logger.warning("Connection reset by peer.")
        return None
    except Exception as e:
        logger.error(f"Error receiving message: {e}")
        return None

def recvall(sock, n):
    """Helper function to receive exactly n bytes from a socket."""
    data = bytearray()
    while len(data) < n:
        try:
            packet = sock.recv(n - len(data))
            if not packet:
                return None # Connection closed
            data.extend(packet)
        except BlockingIOError:
            # This can happen with non-blocking sockets; ensure your socket is blocking
            # or handle this appropriately if using non-blocking.
            # For this example, assuming blocking sockets.
            logger.warning("Socket operation would block (recvall).")
            pass # Or sleep briefly and retry, or return None
        except Exception as e:
            logger.error(f"Error in recvall: {e}")
            return None
    return data
