from twisted.internet.protocol import Protocol, ClientFactory

class LeafProtocol(Protocol):
    def __init__(self, factory, state):
        self.factory = factory
        self.logger = factory.logger
        self.state = state
    
    def connectionMade(self):
        self.state.ultrapeerConnection = True
        pass

    def dataReceived(self, data):
        data_decoded = data.decode('utf-8')
        print("<< ", data_decoded)
        # For now just assume it wants input
        self.state.ultrapeerAwaitingInput = True
        pass
    
    def dataSend(self, data):
        self.transport.write(data.encode('utf-8'))
            
class LeafFactory(ClientFactory):
    protocol = LeafProtocol

    def __init__(self, logger, state):
        self.logger = logger
        self.state = state
        
    def buildProtocol(self, addr):
        return LeafProtocol(self, self.state)

    def clientConnectionFailed(self, connector, reason):
        pass

    def clientConnectionLost(self, connector, reason):
        pass