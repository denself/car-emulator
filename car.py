import json
import os
import random

import datetime
from twisted.internet import reactor
from twisted.python import log

from interfaces import ICar, IUpdatable
from navigator import Navigator
from utils.geo import GeoVector, GeoPoint
from utils.units_helpers import to_meters_per_second, to_liters_per_meter


class Car(ICar, IUpdatable):
    def __init__(self, vin, city, schedule):
        """

        :param vin:
        :param city:
        :type schedule: utils.datehelper.Schedule
        """
        # TODO: internal logger
        self._vin = vin
        self._saver = CarSaver(vin, self)
        data = self._saver.load()
        self._navigator = Navigator(city, data.get('position'))
        self._max_speed = to_meters_per_second(60)
        self._speed = 0
        self._moving = False
        self._heading = data.get('heading', 0)
        self._mileage = data.get('mileage', 0)
        self._tank_value = 50.
        self._fuel_level = data.get('fuel_level', self._tank_value)
        self._fuel_speed = to_liters_per_meter(12)
        self._schedule = schedule
        self._delayed_start(3)

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
        if self._moving:
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

        moved_distance = self._navigator.move(potential_distance)
        self._heading = self._navigator.get_heading()
        if moved_distance and self._navigator.is_arrived():
            self._on_arrived()

        return moved_distance

    def _on_arrived(self):
        log.msg("Car {} arrived to destination point".format(self._vin))
        self._moving = False
        self._speed = 0
        # TODO: custom reactor
        self._delayed_start()

    def _delayed_start(self, delay=300):
        now = datetime.datetime.utcnow()
        timeout = self._schedule.get_time_to_next_ride(now, delay=delay,
                                                       precision=2)
        reactor.callLater(timeout, self._start)

    def _start(self):
        if not self._navigator.build_path():
            self._delayed_start()
        else:
            log.msg("Car {} Start moving. Fuel level: {}"
                    "".format(self._vin, self._fuel_level))
            self._moving = True
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
