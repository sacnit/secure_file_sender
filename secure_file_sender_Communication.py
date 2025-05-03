from twisted.internet.protocol import Protocol, ClientFactory

class CommunicationProtocol(Protocol):
    def __init__(self, factory):
        self.factory = factory
        self.logger = factory.logger
    
    def connectionMade(self):
        pass

    def dataReceived(self, data):
        pass
            
class CommunicationFactory(ClientFactory):
    protocol = CommunicationProtocol

    def __init__(self, logger):
        self.logger = logger
        
    def buildProtocol(self, addr):
        protocol = ClientFactory.buildProtocol(self, addr)
        protocol.factory = self
        return protocol

    def clientConnectionFailed(self, connector, reason):
        pass

    def clientConnectionLost(self, connector, reason):
        pass