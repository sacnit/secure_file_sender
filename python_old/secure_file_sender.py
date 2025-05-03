import hashlib
import os
import threading
import logging
import argparse
import time
from twisted.internet import reactor, ssl, threads
from twisted.internet.protocol import Protocol, Factory, ClientFactory
from twisted.internet.endpoints import SSL4ServerEndpoint, SSL4ClientEndpoint
from Crypto.PublicKey import RSA
from OpenSSL import crypto, SSL
import warnings
# FOR GETTING HOSTNAME PLEASE REMOVE LATER
import socket

# Input

class KeyboardThread(threading.Thread):
    def __init__(self, input_cbk = None, name='keyboard-input-thread'):
        self.input_cbk = input_cbk
        super(KeyboardThread, self).__init__(name=name, daemon=True)
        self.start()

    def run(self):
        while True:
            self.input_cbk(input()) #waits to get input + Return
            
# Client Behaviour

# For handling the state of the program and TUI
class State:
    def __init__(self, UPFactory, LFactory):
        self.Leaf_Ultrapeer_Factory: LeafFactory = UPFactory
        self.Leaf_Leaf_Factory: P2PFactory = LFactory
        self.connected = False # Is the leaf connected to an ultrapeer
        self.querying = False # Is the leaf trying to query for a leafs address
        self.connected_to_leaf = False # Is the leaf connected to another leaf
        self.contacts: dict[str, tuple[str, int]] = {} # The contacts list, add peeps to it when they are queried
        self.current_contact = ""

    # for rendering the TUI and taking user input to the correct locations
    def tui(self):
        running = True
        while running:
            # Check to see what state the program is in
            # Connected to an ultrapeer
            # Can take inputs (Identity, Exit, Query, Help)
            if self.connected_to_leaf: # If connected to a leaf it should be handled instead of the ultrapeer connection
                # ------------------------------------------------------------------------------------------------
                user_input = ""
                # ------------------------------------------------------------------------------------------------
                if not user_input:
                    # Its null so it was interrupted
                    return
                elif user_input.lower() == "exit":
                    running = False
                    try:
                        reactor.stop()
                        leaf_ultrapeer_factory.stopFactory()
                    except:
                        os._exit(1)
                    os._exit(1)
                else:
                    state.Leaf_Leaf_Factory.client_instance.dataSend(user_input)
                pass
            elif self.querying: # We have been told to give it the public key
                # global_stdscr.addstr("Provide public key:")
                # pubkey = self.multi_input(global_stdscr)
                pubkey = ""
                state.current_contact = pubkey
                self.Leaf_Ultrapeer_Factory.client_instance.SendMessage(f"QUERYPUBKEY¬{pubkey}")
                running = False
                self.querying = False
                pass
            elif self.connected: # If connected to an ultrapeer
                # ------------------------------------------------------------------------------------------------
                user_input = ""
                # ------------------------------------------------------------------------------------------------
                if not user_input:
                    # Its null so it was interrupted
                    return
                elif user_input.lower() == "exit":
                    running = False
                    try:
                        reactor.stop()
                        leaf_ultrapeer_factory.stopFactory()
                    except:
                        os._exit(1)
                    os._exit(1)
                elif user_input.lower() == "identity":
                    print(f"Identity:\n{keypair.public_key().export_key().decode('utf-8')}\n")
                elif user_input.lower() == "query":
                    running = False
                    self.Leaf_Ultrapeer_Factory.client_instance.SendMessage("QUERY¬")
                else: # The help command will be treated like an error as i cannot be bothered to introduce more logic yet
                    print(f"Ultrapeer commands:\n\"Identity\": Display  public key\n\"Exit\": Exit program\n\"Query\": Query and connect to a leaf identified by submitted public key\n\"Help\": Display this message\n")
            time.sleep(0.01) # Just to make it a lil less spammy when nothing is happening

    # I need a consistent way to get a port fromm both an exported key and a multi-line inputted key
    def derive_port(self, input):
        try:
            hashed_key = hashlib.sha256(input).digest()
            key_int = int.from_bytes(hashed_key, byteorder='big')
            port = 5000 + (key_int % (9998 - 5000))
            return port
        except:
            hashed_key = hashlib.sha256(bytes(input)).digest()
            key_int = int.from_bytes(hashed_key, byteorder='big')
            port = 5000 + (key_int % (9998 - 5000))
            return port

    # Take input from multiple lines, with an empty line stopping the input
    def multi_input(self, stdscr):
        # Display a prompt, take multiple lines of input, output them formatted
        multiline_input = ["",""]
        return b"\n".join([s.encode('utf-8') for s in multiline_input])

class LeafProtocol(Protocol):
    def connectionMade(self):
        # When a connection is made, send the connection signal
        self.transport.write(f"CONNECT¬{keypair.public_key().export_key()}".encode('utf-8'))
        self.factory.client_instance = self

    def dataReceived(self, data):
        # CONNECTED¦ for successful connection
        # GIMME¦ for requesting public key to query
        # HEREYAGO¦ for address response to query
        recieved = data.decode('utf-8')
        logger.info(f"Data recieved:\n{recieved}")
        if recieved.startswith("CONNECTED¦"):
            state.connected = True
        elif recieved.startswith("GIMME¦"):
            state.querying = True
        elif recieved.startswith("HEREYAGO¦"):
            leaf_address = recieved.split("¦")[1][1:-1].replace("'","").split(",")[0] # Assume theres some data afterwards
            print("Leaf identified")
            state.Leaf_Leaf_Factory = P2PFactory()
            reactor.connectSSL(leaf_address, state.derive_port(state.current_contact), state.Leaf_Leaf_Factory, SSLContextFactory())
            return # Nothing else needed from here as this protocols functions should take over
        state.tui() # Render the TUI
        
    def SendMessage(self, data):
        logger.info(f"Data sent:\n{data}")
        self.transport.write(data.encode('utf-8'))
            
class LeafFactory(ClientFactory):
    protocol = LeafProtocol
    client_instance: LeafProtocol = None

    def clientConnectionFailed(self, connector, reason):
        logger.warning("Client connection failed.")
        # try:
        #     reactor.stop()
        # except:
        #     pass

    def clientConnectionLost(self, connector, reason):
        logger.warning("Client connection lost.")
        # try:
        #     reactor.stop()
        # except:
        #     pass

# Server Behaviour

# Since the server will have multiple clients, I am assuming some locking to avoid deadlocks would be good
class Synchronizer():
    def __init__(self):
        self.clientele: dict[str, tuple[str, int]] = {} # A dictionary of all connected peers, currently not allowing for removal
        self.clientele_lock = threading.Lock()
        
    # It doesnt take a genuis to guess what this function does
    def add_peer(self, key, peer):
        with self.clientele_lock:
            self.clientele[key] = peer
            
    # Really...
    def query_peer(self, key):
        with self.clientele_lock: # Threading stuff may be the issue
            return self.clientele.get(key)

class UltrapeerProtocol(Protocol):
    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        client_info = str(self.transport.getPeer()).split(",")
        client_address = client_info[1].strip("\'").split("=")[1]
        client_port = client_info[2].strip("\'").split("=")[1]
        client = f"{client_address}:{client_port}".removeprefix("\'").removesuffix(")") # Removing a prefix and suffix as it is being a little bit difficult
        logger.info(f"Connection established with client: {client}")

    def connectionLost(self, reason):
        # Remove the client from the factory's dictionary
        client_info = str(self.transport.getPeer()).split(",")
        client_address = client_info[1].removeprefix("host=").strip("\'")
        client_port = client_info[2].removeprefix("port=").strip("\'")
        client = f"{client_address}:{client_port}".removeprefix("\'").removesuffix(")")
        logger.info(f"Client at address disconnected: {client}")

    def dataReceived(self, data):
        client_info = str(self.transport.getPeer()).replace("IPv4Address(type='TCP', host='", "").replace("', port","").replace(")","").split("=")
        logger.info(f"From:\n{client_info}\n{data.decode('utf-8')}")
        try:
            message = data.decode('utf-8')
            logger.info(f"Data received from {client_info}, prefix: {data.decode('utf-8').split("¬")[0]}")
            if message.startswith("CONNECT¬"):
                # Handle client registration
                client_keypair = message.split("¬")[1].removeprefix("b\'").removesuffix("\'").replace("\\n","\n")
                synchronizer.add_peer(message.split("¬")[1], (client_info[0], int(client_info[1])))
                self.transport.write(f"CONNECTED¦".encode('utf-8')) # Replace with an identity to prepend
            if message.startswith("QUERY¬"):
                logger.info(f"Client requesting to query: {client_info}")
                self.transport.write(f"GIMME¦".encode('utf-8')) # Replace with an identity to prepend
            if message.startswith("QUERYPUBKEY¬"):
                pubkey = message.split("¬")[1]
                address = synchronizer.query_peer(pubkey)
                self.transport.write(f"HEREYAGO¦{address}".encode('utf-8'))
        except Exception as e:
            logger.error(f"Error processing data: {e}")

class UltrapeerFactory(Factory):
    def buildProtocol(self, addr):
        return UltrapeerProtocol(self)

class SSLContextFactory(ssl.ContextFactory):
    def __init__(self):
        # Generate certificate and key in memory
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 2048)

        cert = crypto.X509()
        cert.get_subject().CN = "localhost"
        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(31536000) # Gimme a decade
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(key)
        cert.sign(key, "sha256")

        self.private_key = key
        self.certificate = cert

    def getContext(self):
        # Return cryptographic context
        ctx = ssl.SSL.Context(ssl.SSL.TLSv1_2_METHOD)
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            ctx.use_privatekey(self.private_key)
            ctx.use_certificate(self.certificate)
            ## Not behaving rn
            # ctx.set_verify(
            #     SSL.VERIFY_PEER | SSL.VERIFY_CLIENT_ONCE | SSL.VERIFY_FAIL_IF_NO_PEER_CERT
            # )
        return ctx

# P2P Protocol

class P2PProtocol(Protocol):
    def connectionMade(self):
        print("Connection made\n")
        logger.info("Connection made in P2PProtocol")
        state.connected_to_leaf = True
        self.factory.client_instance = self
        self.transport.write("Connection established".encode('utf-8'))
        # state.tui()
        # self.transport.write(f"PING¦¬¦{input(">> ")}".encode('utf-8'))

    def dataReceived(self, data):
        logger.info(f"Data recieved:\n{data.decode('utf-8')}")
        print(f"<< {data.decode('utf-8')}\n")
        state.tui()
        
    def dataSend(self, data):
        logger.info(f"Data sent:\n{data}")
        self.transport.write(data.encode('utf-8'))
    
class P2PFactory(ClientFactory):
    protocol = P2PProtocol # Oops forgot this part
    client_instance: P2PProtocol = None

    def clientConnectionFailed(self, connector, reason):
        logger.warning(f"Client connection failed on connector: {connector}\n{reason}")
        state.connected_to_leaf = False
        # try:
        #     reactor.stop()
        # except:
        #     pass
    
    def clientConnectionLost(self, connector, reason):
        logger.warning(f"Client connection lost on connector: {connector}\n{reason}")
        state.connected_to_leaf = False
        # try:
        #     reactor.stop()
        # except:
        #     pass

def main():
    global logger
    # FOR LOGGING PLEASE REMOVE LATER
    logname = f"./logs/{socket.gethostname()}.log"
    # Handle arguments
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
    
    try:
        # Assume if an error occurs, that its the inputs that messed up
        # Running in leaf mode
        if args.mode == "leaf":
            global state
            global keypair
            global leaf_ultrapeer_factory
            keypair = RSA.generate(2048)
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s [%(levelname)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                filename=logname,
                filemode="w"
            )
            logger = logging.getLogger(__name__)
            context_factory = SSLContextFactory()
            leaf_ultrapeer_factory = LeafFactory()
            leaf_leaf_factory = P2PFactory()
            state = State(leaf_ultrapeer_factory, leaf_leaf_factory)
            reactor.connectSSL(args.ultrapeer, args.port, leaf_ultrapeer_factory, context_factory) # If it doesnt actually connect to anything, this program just kinda sits there... Waiting...
            reactor.listenSSL(state.derive_port(keypair.public_key().export_key()), state.Leaf_Leaf_Factory, SSLContextFactory())
            reactor.run()
        
        # Running in ultrapeer mode
        elif args.mode == "ultrapeer":
            global synchronizer
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s [%(levelname)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                filename=logname,
                filemode="w"
            )
            logger = logging.getLogger(__name__)
            logger.info(f"Starting secure server on port {args.port}...")
            reactor.listenSSL(args.port, UltrapeerFactory(), SSLContextFactory())
            synchronizer = Synchronizer()
            reactor.run()
    except Exception as e:
        # They messed up the inputs
        parser.print_help()
        
main()