import argparse
import logging
import os
import time
from twisted.internet.protocol import Protocol, Factory, ReconnectingClientFactory
from twisted.internet import reactor, ssl
from OpenSSL import crypto, SSL
import warnings
import threading
import hashlib
import json
import socket

# Configure logging
global logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename=f"./logs/{socket.gethostname()}.log",
    filemode="w"
)
logger = logging.getLogger(__name__)

class Forest:
    def __init__(self):
        self.forest = {}
        
    def get_serialized(self):
        logger.info("Getting forest")
        return json.dumps(self.forest)
    
    def from_serialized(self, json_dump):
        if json_dump == "{}": # Its just empty
            return
        self.forest = json.loads(json_dump)
        logger.info("Updated forest")

# This really doesnt need to be here
def to_mocking(text):
    result = ""
    for i, char in enumerate(text):
        if i % 2 == 0:
            result += char.lower()
        else:
            result += char.upper()
    return result

class ForestProtocol(Protocol):
    def __init__(self, factory):
        self.factory = factory
        
    def connectionMade(self):
        self.factory.trees.append(self)
        return self.transport.write(f"¬{forest.get_serialized()}".encode("utf-8"))
    
    def connectionLost(self, reason = ...):
        self.factory.trees.remove(self) # Hopefully this'll remove the now defunct tree
        return super().connectionLost(reason)
    
    def dataReceived(self, data):
        decoded_data = data.decode("utf-8")
        if decoded_data.startswith("¬"):
            json_dump = decoded_data.removeprefix("¬")
            forest.from_serialized(json_dump)
            
    def sendMessage(self, data):
        self.transport.write(data.encode('utf-8'))

class ForestFactory(ReconnectingClientFactory):
    def __init__(self):
        self.trees = []
    
    def broadcast_change(self):
        for tree in self.trees:
            tree.sendMessage(f"¬{forest.get_serialized()}") # Much simple just to resend the entire dictionary
    
    def buildProtocol(self, addr):
        return ForestProtocol(self)
    
    def clientConnectionLost(self, connector, reason):
        logger.error(f"Connection lost in ForestFactory\n{connector}")
        logger.error("Need to implement reconnecting to leaf nodes below:")
        # Need to reconnect to each peer
        for public_key, details in forest.forest.items():
            # reconnect stuff here
            logger.error(f"  Public Key: {public_key}, IP: {details["ip"]}, Remote Port: {details["rport"]}")
    
    def clientConnectionFailed(self, connector, reason):
        logger.error(f"Connection failed in ForestFactory\n{connector}")

class UltrapeerProtocol(Protocol):
    def __init__(self, factory):
        self.factory = factory

    def remove_client_by_transport(self, transport):
        try:
            for public_key, client_info in list(forest.forest.items()):
                if client_info["transport"] is transport:
                    logger.info(f"Removing client with public key: {public_key[88:108]}")
                    del forest.forest[public_key]
                    break
        
        
        
        except Exception as e:
            logger.error(f"Error removing client: {e}")

    def connectionMade(self):
        logger.info(f"Connection established with client")

    def connectionLost(self, reason):
        logger.info(f"Client disconnected. Reason: {reason.getErrorMessage()}")
        self.remove_client_by_transport(self.transport)

    def dataSend(self, data):
        try:
            time.sleep(2)
            self.transport.write(data.encode('utf-8'))
        
        
        
        except Exception as e:
            logger.error(f"Error sending data: {e}")

    def dataReceived(self, data):
        try:
            decoded = data.decode('utf-8').strip()
        except: # Data that cant be decoded this way is invalid
            return
        # Its a registration message so do not echo
        if decoded.startswith("Registration¬|¬"):
            leaf = self.transport.getPeer()
            parts = decoded.replace("Registration¬|¬", "").split("¬|¬")
            try:
                public_key = parts[0]
                port = parts[1]
                forest.forest[public_key] = {
                    "ip": leaf.host,
                    "port": port,
                    "rport": leaf.port
                }
                forest_factory.broadcast_change()
                logger.info(f"Registered: {leaf.host}:{public_key[88:108]}")
                self.transport.write(f"You are at {str(leaf.host)}".encode('utf-8'))
            
            
            
            except IndexError:
                logger.error(f"Registration message format error from {leaf.host}: {decoded}")
            except Exception as e:
                logger.error(f"Error processing registration from {leaf.host}: {e}")
        elif decoded.startswith("Query¬¬|"):
            # Its a query so do not echo
            public_key = decoded.replace("Query¬¬|", "")
            logger.info(f"Received query for {public_key[88:108]}")
            try:
                response_ip = forest.forest[public_key]["ip"]
                response_port = forest.forest[public_key]["port"]
                self.transport.write(f"Response||¬{public_key}||¬{response_ip}||¬{response_port}".encode('utf-8'))
            
            
            
            except KeyError:
                logger.warning(f"Query for unknown public key: {public_key[88:108]} from {self.transport.getPeer().host}")
                self.transport.write(f"Error||¬{public_key}||¬Unknown".encode('utf-8'))
            except Exception as e:
                logger.error(f"Error processing query for {public_key[88:108]}: {e}")
        else:
            logger.info(f"Received: {data.decode('utf-8')}")
            self.dataSend(to_mocking(decoded))

class UltrapeerFactory(Factory):
    def buildProtocol(self, addr):
        return UltrapeerProtocol(self)

class SSLFactory(ssl.ContextFactory):
    def __init__(self):
        # Generate certificate and key in memory
        key = crypto.PKey()
        try:
            key.generate_key(crypto.TYPE_RSA, 2048)
        
        
        
        except Exception as e:
            logger.error(f"Error generating private key: {e}")
            raise

        cert = crypto.X509()
        cert.get_subject().CN = "localhost"
        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(31536000) # Gimme a decade
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(key)
        try:
            cert.sign(key, "sha256")
        
        
        
        except Exception as e:
            logger.error(f"Error signing certificate: {e}")
            raise

        self.private_key = key
        self.certificate = cert

    def getContext(self):
        # Return cryptographic context
        try:
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
        
        
        
        except Exception as e:
            logger.error(f"Error creating SSL context: {e}")
            raise
    
def main(ultrapeer, uport, join, port, fport, certificate):
    global forest
    global forest_factory
    global ssl_factory
    global ultrapeer_factory
    
    forest = Forest()
    
    try:
        logger.info("Starting secure server on port 9999...")
        if certificate == "":
            ssl_factory = SSLFactory()
        else:
            try:
                ssl_factory = cert_options = ssl.CertificateOptions(
                    privateKey=(certificate+"cert.crt").encode('ascii'),
                    certificate=(certificate+"key.key").encode('ascii'),
                    verify=True # Genuinely it only needs verification if actual keys and certs are being used
                )
                pass
            except:
                print(f"Invalid SSL certificate directory {certificate}\nPlease make sure it contains both `cert.crt` and `key.key` and that they are a valid SSL certificate and key")
                os._exit(1)
        
        forest_factory = ForestFactory()
                
        reactor.listenSSL(fport, forest_factory, ssl_factory) # Start listening on the forst protocol
        if join:
            try:
                reactor.connectSSL(ultrapeer, uport, forest_factory, ssl_factory) # Try connect to the forest
            except:
                pass # It was not able to connect to the forest
        ultrapeer_factory = UltrapeerFactory()
        reactor.listenSSL(port, ultrapeer_factory, ssl_factory)
        reactor.run()
    
    
    
    except Exception as e:
        logger.critical(f"Failed to start the server: {e}")
        
# Starts listning using SSL
# Specifies Port, the factory (which makes the server node), and the cryptographic certs for SSL
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Twisted TUI Client",
        description="A Twisted client with an interactive terminal interface."
    )
    parser.add_argument("-U", "--ultrapeer", dest="ultrapeer", default="127.0.0.1",
                        help="Server host address (default: 127.0.0.1)")
    parser.add_argument("-UP", "--ultrapeer-port", dest="uport", type=int, default=4443,
                        help="Server port number (default: 4443)")
    parser.add_argument("-J", "--join", dest="join", default=False,
                        help="Should the ultrapeer specified be joined (default: False)")
    parser.add_argument("-P", "--port", dest="port", type=int, default=9999,
                        help="Server port number (default: 9999)")
    parser.add_argument("-F", "--forest-port", dest="fport", type=int, default=4444,
                        help="Port number to use for syncing with the forst (default: 4444)")
    parser.add_argument("-C", "--certificate", dest="certificate", type=str, default="",
                        help="Directory containing certificate `cert.crt` and key `key.key`")
    args = parser.parse_args()
    
    ultrapeer = args.ultrapeer
    uport = args.uport
    join = args.join
    port = args.port
    fport = args.fport
    certificate = args.certificate
    main(ultrapeer, uport, join, port, fport, certificate)