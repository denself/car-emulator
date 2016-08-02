import time

from twisted.internet import reactor, task

from interfaces import ILoop


class Loop(ILoop):
    period = 0.1  # Time to start server in s.

    def __init__(self):
        self.objects = []
        self.last_update = None
        self.task = None

    def add_object(self, obj):
        """
        Add object to the pool of objects
        :param obj: Updatable object
        :type obj: interfaces.IUpdatable
        """
        self.objects.append(obj)

    def tick(self):
        """
        Process update method of all objects
        """
        now = time.time()
        # Time between ticks in seconds
        t = now - self.last_update

        for o in self.objects:
            o.update(t)

        self.last_update = now

    def start(self):
        """
        Init loop and start reactor
        """
        self.last_update = time.time()

        self.task = task.LoopingCall(self.tick)
        self.task.start(self.period)

        reactor.run()
