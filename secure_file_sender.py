# Import required libraries
import os
import threading
import logging
import argparse
import time
from twisted.internet import reactor, threads
import socket

# Import other scripts
import secure_file_sender_Ultrapeer as Ultrapeer
import secure_file_sender_Leaf as Leaf
import secure_file_sender_Communication as Communication
import secure_file_sender_TUI as TUI

if __name__ == "__main__":
    # Set up logging
    global logger
    logname = f"./logs/{socket.gethostname()}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename=logname,
        filemode="w"
    )
    logger = logging.getLogger(__name__)
    
    # Parse arguments
    parser = argparse.ArgumentParser(
        prog="Secure File Sender",
        description="A secure communication application",
        epilog="Run as either an ultrapeer or peer"
    )
    parser.add_argument("-m", "--mode", dest="mode", default="leaf",
                        help="operating mode (default: leaf)")
    parser.add_argument("-u", "--ultrapeer", dest="ultrapeer", default="127.0.0.1",
                        help="Ultrapeer host address (default: 127.0.0.1)")
    parser.add_argument("-p", "--port", dest="port", type=int, default=9999,
                        help="Ultrapeer port number (default: 9999)")
    args = parser.parse_args()
    
    # Start twisted as Leaf
    if args.mode == "Leaf":
        # Initialise factories
        Leaf_Factory = Leaf.LeafFactory(logger)
        Communication_Factory = Communication.ClientFactory(logger)
        
        # Listen on ports
        
        # Start the TUI
        
        # Run the reactor
        pass
    # Start twisted as Ultrapeer
    elif args.mode == "Ultrapeer":
        # Initialise factories
        Ultrapeer_Factory = Ultrapeer.UltrapeerFactory(logger)
        
        # Listen on ports
        
        # No TUI needed for Ultrapeer
        
        # Run the reactor
        pass
    else:
        parser.print_help()