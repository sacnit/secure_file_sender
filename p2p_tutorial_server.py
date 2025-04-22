import logging
from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor, ssl
from OpenSSL import crypto, SSL
import warnings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

class SecureServer(Protocol):
    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        client_info = str(self.transport.getPeer()).split(",")
        client_address = client_info[1].strip("\'").split("=")[1]
        client_port = client_info[2].strip("\'").split("=")[1]
        client = f"{client_address}:{client_port}".removeprefix("\'").removesuffix(")") # Removing a prefix and suffix as it is being a little bit difficult
        #client_cert = self.transport.getPeerCertificate() # Not currently recieving a cert from client
        logger.info(f"Connection established with client: {client}") # \n{client_cert} removed

    def connectionLost(self, reason):
        # Remove the client from the factory's dictionary
        client_info = str(self.transport.getPeer()).split(",")
        client_address = client_info[1].removeprefix("host=").strip("\'")
        client_port = client_info[2].removeprefix("port=").strip("\'")
        client = f"{client_address}:{client_port}".removeprefix("\'").removesuffix(")")
        logger.info(f"Client at address disconnected: {client}")

    def dataReceived(self, data):
        try:
            message = data.decode('utf-8')
            logger.info(f"Data recieved, prefix: {message.split("¬")[0]}")
            if message.startswith("CONNECT¬"):
                # Handle client registration
                pass
        except Exception as e:
            logger.error(f"Error processing data: {e}")

    def send_encrypted_message(self, message):
        ## Send shit to client
        pass

    def send_client_info(self):
        ## This is here for querying
        pass

class SecureServerFactory(Factory):
    def __init__(self):
        self.clients = {}  # Dictionary of clients

    def buildProtocol(self, addr):
        return SecureServer(self)

class InMemoryContextFactory(ssl.ContextFactory):
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

# Starts listning using SSL
# Specifies Port, the factory (which makes the server node), and the cryptographic certs for SSL
if __name__ == "__main__":
    logger.info("Starting secure server on port 9999...")
    reactor.listenSSL(9999, SecureServerFactory(), InMemoryContextFactory())
    reactor.run()