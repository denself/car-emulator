import datetime
import random
from twisted.python import log


class Schedule(object):

    def __init__(self, day_start, day_end):
        """
        :param day_start:
        :type day_start: datetime.time
        :param day_end:
        :type day_end: datetime.time
        """
        self._day_start = day_start
        self._day_end = day_end

    @classmethod
    def from_dict(cls, data):
        if not data:
            return cls.get_default()
        time_format = "%H:%M:%S"
        day_start = datetime.datetime.strptime(data['day_start'], time_format)
        day_end = datetime.datetime.strptime(data['day_end'], time_format)
        return cls(day_start.time(), day_end.time())

    @classmethod
    def get_default(cls):
        day_start = datetime.time(6, 0, 0)
        day_end = datetime.time(15, 0, 0)
        return cls(day_start, day_end)

    def time_in_range(self, dt):
        """
        Return True if dt is in the range [start, end]
        :type dt: datetime.datetime
        :rtype: bool
        """
        t = dt.time()
        if self._day_start <= self._day_end:
            return self._day_start <= t <= self._day_end
        else:
            return self._day_start <= t or t <= self._day_end

    def get_time_to_next_ride(self, now, delay=0, precision=0):
        t = delay
        if not self.time_in_range(now):
            next_start = datetime.datetime.combine(now.date(), self._day_start)
            if next_start < now:
                next_start += datetime.timedelta(days=1)
            log.msg("Time is out of schedule. Start scheduled to {}"
                    "".format(next_start))
            t = max((next_start - now).total_seconds(), delay)

        if precision:
            t = random.uniform(t, precision * 60)
        log.msg("Start after {} sec".format(t))
        return t
