from twisted.internet import reactor, ssl
from twisted.internet.protocol import Protocol, ClientFactory
import logging
from OpenSSL import crypto
import warnings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

class MyClientProtocol(Protocol): 
    def connectionMade(self):
        # When a connection is made, send the connection signal
        self.transport.write(f"CONNECT¬".encode('utf-8'))

    def dataReceived(self, data):
        logger.info(f"Received: {data}")

        try:
            decrypted_data = self.cipher.decrypt(data)
            logger.info(f"Decrypted data: {decrypted_data.decode()}")
        except Exception as e:
            logger.warning(f"Decryption failed. Possible key mismatch or corrupted data. Error: {e}")

class MyClientFactory(ClientFactory):
    protocol = MyClientProtocol

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
        return ctx

if __name__ == "__main__":
    reactor.connectSSL("127.0.0.1", 9999, MyClientFactory(), InMemoryContextFactory())
    reactor.run()