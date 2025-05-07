# config.py
# Configuration constants for the P2P network

# Port range for Leaf P2P listening sockets (derived from public key)
LEAF_P2P_PORT_RANGE_START = 49152
LEAF_P2P_PORT_RANGE_END = 65535

# Default host for listening (0.0.0.0 means all available interfaces)
DEFAULT_HOST = "0.0.0.0"

# Buffer size for network communications
BUFFER_SIZE = 4096

# RSA Key size
RSA_KEY_SIZE = 2048

# Maximum message length (e.g., 1MB) for safety
MAX_MSG_LENGTH = 1024 * 1024
