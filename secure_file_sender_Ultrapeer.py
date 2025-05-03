import threading
from twisted.internet import ssl
from twisted.internet.protocol import Protocol, Factory
from Crypto.PublicKey import RSA
from OpenSSL import crypto, SSL
import warnings

class UltrapeerProtocol(Protocol):
    def __init__(self, factory):
        self.factory = factory
        self.logger = factory.logger
        
    def connectionMade(self):
        pass

    def connectionLost(self, reason):
        pass

    def dataReceived(self, data):
        pass
    
class UltrapeerFactory(Factory):
    protocol = UltrapeerProtocol
    
    def __init__(self, logger):
        self.logger = logger    

    def buildProtocol(self, addr):
        protocol = UltrapeerFactory.buildProtocol(self, addr)
        protocol.factory = self
        return protocol

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
            ## For verification - requires valid certificates so cannot be used for in memory self signed certs
            # ctx.set_verify(
            #     SSL.VERIFY_PEER | SSL.VERIFY_CLIENT_ONCE | SSL.VERIFY_FAIL_IF_NO_PEER_CERT
            # )
        return ctx