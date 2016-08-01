from twisted.internet import protocol, reactor
from twisted.python import log


class Client(protocol.Protocol):
    def connectionMade(self):
        self.transport.write(b'Hello, world')

    def dataReceived(self, data):
        log.msg('Received: {}'.format(data))
        self.transport.loseConnection()


class ClientFactory(protocol.ClientFactory):
    def buildProtocol(self, addr):
        return Client()


if __name__ == '__main__':
    reactor.connectTCP('localhost', 8000, ClientFactory())
    reactor.run()
