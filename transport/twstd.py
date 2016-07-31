from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ReconnectingClientFactory
from twisted.python import log


class Transport(Protocol):

    def __init__(self, handshake):
        self._connected = False
        self._handshake = handshake

    def send_data(self, data):
        if self._connected:
            self.write(data)

    def connectionMade(self):
        self.write(self._handshake)
        self._connected = True

    def write(self, data):
        log.msg("Sending data: {}".format(data))
        self.transport.write(data)

    def dataReceived(self, data):
        log.msg('Received: {}'.format(data))

    def connectionLost(self, reason=None):
        self._connected = False


class TransportFactory(ReconnectingClientFactory):
    maxDelay = 60

    def __init__(self, parser):
        self.parser = parser
        self.transport = None
        reactor.callLater(0, self.connect)

    def send(self, data):
        package = self.parser.dump(data)
        self.transport.send_data(package)

    def buildProtocol(self, addr):
        log.msg('Connection established')
        self.resetDelay()
        self.transport = Transport(self.parser.get_handshake())
        return self.transport

    def clientConnectionFailed(self, connector, reason):
        log.msg('Connection failed: {}. Reconnecting in {}'
                ''.format(reason, self.delay))
        self.transport = None
        ReconnectingClientFactory \
            .clientConnectionFailed(self, connector, reason)

    def clientConnectionLost(self, connector, reason):
        log.msg('Connection lost: {}. Reconnecting in {}.'
                ''.format(reason, self.delay))
        self.transport = None
        ReconnectingClientFactory \
            .clientConnectionLost(self, connector, reason)

    def startedConnecting(self, connector):
        log.msg('Connection started')

    def connect(self):
        reactor.connectTCP(self.parser.host, self.parser.port, self)

    @property
    def is_connected(self):
        return self.transport and self.transport.connected
