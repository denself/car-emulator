from twisted.internet import reactor, task


class Reactor(object):
    def __init__(self):
        self._reactor = reactor

    @staticmethod
    def looping_call(func):
        return task.LoopingCall(func)

    def run(self):
        self._reactor.run()
