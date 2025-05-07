from twisted.internet.protocol import Protocol, ClientFactory

class CommunicationProtocol(Protocol):
    def __init__(self, factory, state):
        self.factory = factory
        self.logger = factory.logger
        self.state = state
    
    def connectionMade(self):
        pass

    def dataReceived(self, data):
        data_decoded = data.decode('utf-8')
        print("<< ", data_decoded)
        pass
            
class CommunicationFactory(ClientFactory):
    protocol = CommunicationProtocol

    def __init__(self, logger, state):
        self.logger = logger
        self.state = state
        
    def buildProtocol(self, addr):
        return CommunicationProtocol(self, self.state)

    def clientConnectionFailed(self, connector, reason):
        pass

    def clientConnectionLost(self, connector, reason):
        pass