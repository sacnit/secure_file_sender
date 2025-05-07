# Import required libraries
import os
import threading
import logging
import argparse
import time
from twisted.internet import reactor, threads
from twisted.internet.threads import deferToThread
from twisted.internet.defer import Deferred
from twisted.internet.asyncioreactor import install
import socket
from threading import Event
from Crypto.PublicKey import RSA
import asyncio

# Import other scripts
import secure_file_sender_Ultrapeer as Ultrapeer
import secure_file_sender_Leaf as Leaf
import secure_file_sender_Communication as Communication
import secure_file_sender_TUI as TUI

def exitProgram():
    try:
        reactor.stop()
    except:
        os._exit(1)
    os._exit(1)

async def start_async_interface():
    await Terminal_User_Interface.interfaceLoop()
    exitProgram()

def startInterfaceLoop():
    d = threads.deferToThread(Terminal_User_Interface.interfaceLoop)
    d.addCallback(exitProgram)

class State:
    def __init__(self):
        self.interruptSignal = asyncio.Event()
        self.identity = RSA.generate(2048)
        self.ultrapeerConnection = False
        self.ultrapeerAwaitingInput = False
        self.running = True
        
    def setInterruptSignal(self):
        self.interruptSignal.set()

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
    if str(args.mode).lower() == "leaf":
        install()
        
        # Initialise state
        state = State()
        
        # Initialise factories
        Leaf_Factory = Leaf.LeafFactory(logger, state)
        Communication_Factory = Communication.CommunicationFactory(logger, state)
        Leaf_SSL_Factory = Ultrapeer.SSLContextFactory()
        
        # TUI must be initialised first
        Terminal_User_Interface = TUI.TerminalUserInterface(Leaf_Factory, Communication_Factory, state)
        
        # Listen on ports & Connect on ports
        reactor.connectSSL(args.ultrapeer, args.port, Leaf_Factory, Leaf_SSL_Factory)
        
        # Start the TUI
        reactor.callWhenRunning(lambda: asyncio.create_task(start_async_interface()))
        
        # Run the reactor
        reactor.run()
    # Start twisted as Ultrapeer
    elif str(args.mode).lower() == "ultrapeer":
        # Initialise state
        state = State()
        
        # Initialise factories
        Ultrapeer_Factory = Ultrapeer.UltrapeerFactory(logger, state)
        Ultrapeer_SSL_Factory = Ultrapeer.SSLContextFactory()
        
        # Listen on ports
        reactor.listenSSL(args.port, Ultrapeer_Factory, Ultrapeer_SSL_Factory)
        
        # No TUI needed for Ultrapeer
        
        # Run the reactor
        reactor.run()
    else:
        parser.print_help()