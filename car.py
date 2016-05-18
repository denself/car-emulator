import json

from twisted.internet import reactor

from interfaces import ICar, IUpdatable
from utils import GeoPoint, to_hours

KYIV = 50.450115, 30.524245


class Car(ICar, IUpdatable):
    def __init__(self, points):
        """
        :type points: list
        """
        self.speed = 60
        self.heading = 0
        self.points = [GeoPoint.from_reversed(*p) for p in points]
        self.location = self.points.pop(0)
        self._mileage = 0
        self._saver = CarSaver(self)

    def get_heading(self):
        return self.heading

    def get_speed(self):
        return self.speed

    def get_location(self):
        return self.location

    def get_odometer_value(self):
        return self._mileage

    def update(self, t):
        self._move(to_hours(t))
        # print '{:.6f}, {:.6f}'.format(*self.location.get_coords())

    def _move(self, t):
        if not self.points:
            return

        potential_distance = t * self.speed
        vector_to_point = self.points[0] - self.location

        while potential_distance >= vector_to_point.value:
            self.location = self.points.pop(0)
            if not self.points:
                return
            potential_distance -= vector_to_point.value
            vector_to_point = self.points[0] - self.location

        vector_to_point.value = potential_distance
        self.location = self.location + vector_to_point
        self.heading = vector_to_point.heading


class CarSaver(object):
    period = 5

    def __init__(self, car):
        """
        :type car: Car
        """
        self._car = car

    def save(self):
        point = self._car.get_location()
        with open('data/{}.json'.format('111'), 'w') as f:
            json.dump(point.to_dict(), f)
        self.call_later()

    def call_later(self):
        reactor.callLater(self.period, self.save)