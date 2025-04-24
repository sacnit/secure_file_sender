import os
from twisted.internet import reactor, ssl, threads
from twisted.internet.protocol import Protocol, ClientFactory
import logging
from Crypto.PublicKey import RSA
import threading
import argparse
import logging
from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor, ssl
from OpenSSL import crypto, SSL
import warnings
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="client.log",
    filemode="w"
)
logger = logging.getLogger(__name__)

class State:
    def __init__(self):
        self.connected = False
        self.querying = False
        
    def set_state(self, state, value):
        match state:
            case "connected":
                self.connected = value
            case "querying":
                self.querying = value
            case _:
                pass
    
    def get_state(self, state):
        match state:
            case "connected":
                return self.connected
            case "querying":
                return self.querying
            case _:
                pass

def multi_input():
        multiline_input = []
        while True:
            line = input()
            if not line:
                break
            multiline_input.append(line)    
        return b"\n".join([s.encode('utf-8') for s in multiline_input])

class MyClientProtocol(Protocol):
    def connectionMade(self):
        # When a connection is made, send the connection signal
        self.transport.write(f"CONNECT¬{keypair.public_key().export_key()}".encode('utf-8'))
        self.factory.client_instance = self

    def dataReceived(self, data):
        run_ui = True
        peer_info = str(self.transport.getPeer()).split(",")
        peer_address = peer_info[1].removeprefix("host=").strip("\'")
        peer_port = peer_info[2].removeprefix("port=").strip("\'")
        peer = f"{peer_address}:{peer_port}".removeprefix("\'").removesuffix(")")
        logger.info(f"Data received from: {peer}\n{data.decode('utf-8')}")
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
            
class MyClientFactory(ClientFactory):
    protocol = MyClientProtocol
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Secure File Sender",
        description="A secure communication application",
        epilog="Run as either an ultrapeer or peer"
    )
    parser.add_argument("-U", "--ultrapeer", dest="ultrapeer", default="127.0.0.1",
                        help="Ultrapeer host address (default: 127.0.0.1)")
    parser.add_argument("-P", "--port", dest="port", type=int, default=9999,
                        help="Ultrapeer port number (default: 9999)")
    args = parser.parse_args()
    state = State()
    keypair = RSA.generate(2048)
    context_factory = ssl.ClientContextFactory()
    factory = MyClientFactory()
    reactor.connectSSL(args.ultrapeer, args.port, factory, context_factory)
    reactor.run()