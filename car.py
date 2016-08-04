import json
import os
import random

from twisted.internet import reactor
from twisted.python import log

from interfaces import ICar, IUpdatable
from navigator import Navigator
from utils.geo import to_hours, GeoVector, GeoPoint
from utils.helpers import to_meters_per_second, to_liters_per_meter


class Car(ICar, IUpdatable):
    def __init__(self, vin, city):
        # TODO: internal logger
        self._vin = vin
        self._saver = CarSaver(vin, self)
        data = self._saver.load()
        self._navigator = Navigator(city, data.get('position'))
        self._max_speed = to_meters_per_second(60)
        self._speed = 0
        self._heading = data.get('heading', 0)
        self._mileage = data.get('mileage', 0)
        self._tank_value = 50.
        self._fuel_level = data.get('fuel_level', self._tank_value)
        self._fuel_speed = to_liters_per_meter(12)
        reactor.callLater(3, self._start)

    def get_heading(self):
        return self._heading

    def get_speed(self):
        return self._speed

    def get_location(self):
        return self._navigator.get_location()

    def get_odometer_value(self):
        return 0

    def get_full_mileage(self):
        return self._mileage

    def get_fuel_level(self):
        return self._fuel_level

    def get_fuel_level_rel(self):
        return (self._fuel_level / self._tank_value) * 100

    def update(self, t):
        if not self._navigator.is_arrived():
            path = self._move(t)
            self._update_fuel(path)

    def _get_fuel_speed(self):
        """
        Get random fuel consumption in range 0.8origin .. 1.2origin
        :return:
        """
        return self._fuel_speed * random.uniform(0.8, 1.2)

    def _update_fuel(self, path):
        """
        :param path: length on moved path in m
        """
        # Fuel spent in liters
        value = path * self._get_fuel_speed()
        self._fuel_level -= value
        # TODO: logic for smart fuel refills
        if self._fuel_level < 0:
            self._fuel_level = 0

    def _update_refuel(self):
        if self._fuel_level <= 5.:
            free_value = self._tank_value - self._fuel_level
            self._fuel_level += random.randint(int(0.5 * free_value), int(free_value))

    def _move(self, t):
        """
        :param t: Time passed since last update in seconds
        :return: Path moved in meters
        """
        potential_distance = t * self.get_speed()  # meters
        moved_distance = 0

        while not self._navigator.is_arrived():
            old_location = self.get_location()
            next_point = self._navigator.get_next_point()

            vector_to_point = next_point - old_location
            self._heading = vector_to_point.heading

            if potential_distance < vector_to_point.meters:
                potential_vector = GeoVector(
                    value=potential_distance, heading=vector_to_point.heading)
                new_location = old_location + potential_vector
                moved_distance += potential_distance
                self._navigator.set_location(new_location)
                break

            potential_distance -= vector_to_point.meters
            moved_distance += vector_to_point.meters
            self._navigator.pop_next_point()
        else:
            # arrived
            self._on_arrived()

        return moved_distance

    def _on_arrived(self):
        log.msg("Car {} arrived to destination point".format(self._vin))
        self._speed = 0
        # TODO: custom reactor
        reactor.callLater(300, self._start)

    def _start(self):
        if not self._navigator.build_path():
            reactor.callLater(300, self._start)
        else:
            log.msg("Car {} arrived to destination point. Fuel level: {}"
                    "".format(self._vin, self._fuel_level))
            self._update_refuel()
            self._speed = self._max_speed


class CarSaver(object):
    period = 5

    def __init__(self, vin, obj):
        """
        :type obj: Car
        """
        self._vin = vin
        self._obj = obj

    def _get_filename(self):
        return 'data/{}.json'.format(self._vin)

    def load(self):
        """
        :rtype: utils.GeoPoint
        """
        self.call_later()
        if os.path.exists(self._get_filename()):
            try:
                with open(self._get_filename(), 'r') as f:
                    data = json.load(f)
                if 'type' in data:

                    return {
                        'position': GeoPoint.from_dict(data)
                    }
                data['position'] = GeoPoint.from_dict(data['position'])
                return data
            finally:
                pass

    def save(self):
        data = {
            'position': self._obj.get_location().to_dict(),
            'mileage': self._obj.get_odometer_value(),
            'heading': self._obj.get_heading(),
            'fuel_level': self._obj.get_fuel_level()
        }
        with open(self._get_filename(), 'w') as f:
            json.dump(data, f)
        self.call_later()

    def call_later(self):
        reactor.callLater(self.period, self.save)
