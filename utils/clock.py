import time

import datetime


class IClock(object):
    def time(self):
        raise NotImplementedError


class Clock(IClock):
    def __init__(self):
        self._clock = time

    def time(self):
        return self._clock.time()

    def datetime(self):
        return datetime.datetime.utcfromtimestamp(self._clock.time())


class HistoricalClock(IClock):
    def __init__(self):
        self._time = 0

    def time(self):
        return self._time

    def set_time(self, t):
        self._time = t
