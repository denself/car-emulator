from twisted.internet import reactor
from twisted.internet.protocol import Protocol, connectionDone, ClientFactory


class Transport(Protocol):
    reconnect_period = 10

    def __init__(self, parser):
        self.parser = parser
        self._connected = False
        self._factory = TransportFactory(self)
        reactor.callLater(0.1, self.connect)

    def send_data(self, data):
        if self._connected:
            package = self.parser.dump(data)
            # self.transport.write(package)

    def connectionMade(self):
        self.transport.write(self.parser.HANDSHAKE)
        self._connected = True

    def dataReceived(self, data):
        print 'Received: {}'.format(data)

    def connectionLost(self, reason=connectionDone):
        self._connected = False
        reactor.callLater(self.reconnect_period, self.connect)

    def connect(self):
        reactor.connectTCP(self.parser.host, self.parser.port, self._factory)


class TransportFactory(ClientFactory):
    def __init__(self, transport):
        self.transport = transport

    def buildProtocol(self, addr):
        return self.transport
