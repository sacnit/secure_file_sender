# p2p_main.py
# Main script to run the P2P node in Leaf or Ultrapeer mode.

import argparse
import logging
import sys

# It's good practice to ensure the current directory is in PYTHONPATH
# if running scripts from a subdirectory, especially for module imports.
# However, if all files are in the same directory, direct imports usually work.
# For robustness, especially if you structure this as a package:
# import os
# sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from leaf_node import LeafNode
from ultrapeer_node import UltrapeerNode
from config import DEFAULT_HOST

def main():
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(name)s - %(threadName)s - %(message)s')

    parser = argparse.ArgumentParser(description="Hybrid P2P Network Node")
    parser.add_argument("mode", choices=["leaf", "ultrapeer"], help="Mode to run the node in (leaf or ultrapeer)")
    
    # Common arguments
    parser.add_argument("--host", default=DEFAULT_HOST, help="Host IP address for this node to bind to (for listening sockets). Default: 0.0.0.0")

    # Leaf arguments
    leaf_group = parser.add_argument_group("Leaf Mode Options")
    leaf_group.add_argument("--up-host", help="Ultrapeer host to connect to (Leaf mode)")
    leaf_group.add_argument("--up-port", type=int, help="Ultrapeer port to connect to (Leaf mode)")

    # Ultrapeer arguments
    up_group = parser.add_argument_group("Ultrapeer Mode Options")
    up_group.add_argument("--leaf-port", type=int, help="Port for listening to Leaf connections (Ultrapeer mode)")
    up_group.add_argument("--up-listen-port", type=int, help="Port for listening to other Ultrapeer connections (Ultrapeer mode, optional)")
    up_group.add_argument("--connect-ups", nargs='*', help="List of other Ultrapeers to connect to, format: host1:port1 host2:port2 (Ultrapeer mode, optional)")

    args = parser.parse_args()

    if args.mode == "leaf":
        if not args.up_host or not args.up_port:
            parser.error("For Leaf mode, --up-host and --up-port are required.")
        leaf = LeafNode(ultrapeer_host=args.up_host, ultrapeer_port=args.up_port, node_host=args.host)
        try:
            leaf.start()
        except KeyboardInterrupt:
            logging.info("Leaf node shutting down via KeyboardInterrupt.")
        finally:
            leaf.stop()

    elif args.mode == "ultrapeer":
        if not args.leaf_port:
            parser.error("For Ultrapeer mode, --leaf-port is required.")
        
        known_ultrapeers_to_connect = []
        if args.connect_ups:
            for up_addr_str in args.connect_ups:
                try:
                    host, port_str = up_addr_str.split(':')
                    known_ultrapeers_to_connect.append((host, int(port_str)))
                except ValueError:
                    parser.error(f"Invalid Ultrapeer address format: {up_addr_str}. Use host:port.")

        ultrapeer = UltrapeerNode(
            host=args.host,
            leaf_port=args.leaf_port,
            up_port=args.up_listen_port,
            known_ultrapeers=known_ultrapeers_to_connect
        )
        try:
            ultrapeer.start()
        except KeyboardInterrupt:
            logging.info("Ultrapeer node shutting down via KeyboardInterrupt.")
        finally:
            ultrapeer.stop()
            
    logging.info("Program terminated.")

if __name__ == "__main__":
    main()
