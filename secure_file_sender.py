import os
import threading
import warnings
from twisted.internet import reactor, ssl, threads
from twisted.internet.protocol import Protocol, ClientFactory
import logging
from Crypto.PublicKey import RSA
from OpenSSL import crypto, SSL
import argparse
import logging
from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor, ssl
from OpenSSL import crypto, SSL
import warnings
import threading

# Client Behaviour

# For handling the state of the program and TUI
class State:
    def __init__(self):
        self.connected = False # Is the leaf connected to an ultrapeer
        self.querying = False # Is the leaf trying to query for a leafs address
        
    # Take a guess chucklenuts
    def set_state(self, state, value):
        match state:
            case "connected":
                self.connected = value
            case "querying":
                self.querying = value
            case _:
                pass
    
    # Take a guess chucklenuts
    def get_state(self, state):
        match state:
            case "connected":
                return self.connected
            case "querying":
                return self.querying
            case _:
                pass

# Take input from multiple lines, with an empty line stopping the input
def multi_input():
        multiline_input = []
        while True:
            line = input()
            if not line:
                break
            multiline_input.append(line)    
        return b"\n".join([s.encode('utf-8') for s in multiline_input])

class LeafProtocol(Protocol):
    def connectionMade(self):
        # When a connection is made, send the connection signal
        self.transport.write(f"CONNECT¬{keypair.public_key().export_key()}".encode('utf-8'))
        self.factory.client_instance = self

    # Against all warnings I am writing the TUI within the recieving data function because why not
    def dataReceived(self, data):
        run_ui = True
        peer_info = str(self.transport.getPeer()).split(",")
        peer_address = peer_info[1].removeprefix("host=").strip("\'")
        peer_port = peer_info[2].removeprefix("port=").strip("\'")
        peer = f"{peer_address}:{peer_port}".removeprefix("\'").removesuffix(")")
        logger.info(f"Data received from {peer}, prefix: {data.decode('utf-8').split("¦")[0]}")
        if data.decode('utf-8').startswith("CONNECTED¦") and not state.get_state("connected"):
            logger.info(f"Connected to ultrapeer: {peer}")
            state.set_state("connected", True)
        if data.decode('utf-8').startswith("GIMME¦") and state.get_state("querying"):
            state.set_state("querying", False)
            logger.info("Server wants query")
            self.transport.write(f"QUERYPUBKEY¬{multi_input()}".encode('utf-8'))
            run_ui = False
        if data.decode('utf-8').startswith("HEREYAGO¦") and not state.get_state("querying"):
            print(f"Peer returned: {data.decode('utf-8').split("¦")[1]}")
        # Normal case UI
        while run_ui:
            user_input = input("> ")
            match user_input.lower():
                case "exit":
                    print("Shutting down...")
                    try:
                        reactor.stop()
                        factory.stopFactory()
                    except:
                        os._exit(1)
                    os._exit(1)
                case "query":
                    self.transport.write("QUERY¬".encode('utf-8'))
                    state.set_state("querying", True)
                    break
                case "identity":
                    print(f"Identity:\n{keypair.public_key().export_key().decode('utf-8')}")
            
class LeafFactory(ClientFactory):
    protocol = LeafProtocol
    client_instance = None

    def clientConnectionFailed(self, connector, reason):
        logger.warning("Client connection failed.")
        try:
            reactor.stop()
        except:
            pass

    def clientConnectionLost(self, connector, reason):
        logger.warning("Client connection lost.")
        try:
            reactor.stop()
        except:
            pass

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
        with self.clientele_lock:
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
        try:
            message = data.decode('utf-8')
            logger.info(f"Data received from {client_info}, prefix: {data.decode('utf-8').split("¬")[0]}")
            if message.startswith("CONNECT¬"):
                # Handle client registration
                client_keypair = message.split("¬")[1].removeprefix("b\'").removesuffix("\'").replace("\\n","\n")
                #logger.info(f"Public key provided:\n{client_keypair}") # For debug purposes, so i can differentiate between em
                synchronizer.add_peer(message.split("¬")[1], (client_info[0], int(client_info[1])))
                self.transport.write(f"CONNECTED¦".encode('utf-8')) # Replace with an identity to prepend
            if message.startswith("QUERY¬"):
                logger.info(f"Client requesting to query: {client_info}")
                self.transport.write(f"GIMME¦".encode('utf-8')) # Replace with an identity to prepend
            if message.startswith("QUERYPUBKEY¬"):
                logger.info(f"Pubkey provided by client: {client_info}")
                self.transport.write(f"HEREYAGO¦{synchronizer.query_peer(message.split("¬")[1])}".encode('utf-8'))
        except Exception as e:
            logger.error(f"Error processing data: {e}")

class UltrapeerFactory(Factory):
    def __init__(self):
        self.clients = {}  # Dictionary of clients

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

if __name__ == "__main__":
    # Handle arguments
    parser = argparse.ArgumentParser(
        prog="Secure File Sender",
        description="A secure communication application",
        epilog="Run as either an ultrapeer or peer"
    )
    parser.add_argument("-M", "--mode", dest="mode", default="leaf",
                        help="operating mode (default: leaf)")
    parser.add_argument("-U", "--ultrapeer", dest="ultrapeer", default="127.0.0.1",
                        help="Ultrapeer host address (default: 127.0.0.1)")
    parser.add_argument("-P", "--port", dest="port", type=int, default=9999,
                        help="Ultrapeer port number (default: 9999)")
    args = parser.parse_args()
    
    # Running in leaf mode
    if args.mode == "leaf":
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            filename="leaf.log",
            filemode="w"
        )
        logger = logging.getLogger(__name__)
        state = State()
        keypair = RSA.generate(2048)
        context_factory = SSLContextFactory()
        factory = LeafFactory()
        reactor.connectSSL(args.ultrapeer, args.port, factory, context_factory)
        reactor.run()
    
    # Running in ultrapeer mode
    elif args.mode == "ultrapeer":
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            filename="ultrapeer.log",
            filemode="w"
        )
        logger = logging.getLogger(__name__)
        logger.info("Starting secure server on port 9999...")
        reactor.listenSSL(9999, UltrapeerFactory(), SSLContextFactory())
        synchronizer = Synchronizer()
        reactor.run()
    
    # They messed up the inputs
    else:
        parser.print_help()