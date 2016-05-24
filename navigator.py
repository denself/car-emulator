import json
import os
import random

import datetime
from mapbox import Directions
from twisted.internet import reactor
from twisted.python import log

from utils.geo import GeoLine, GeoPoint

ZHULYANY = GeoPoint(50.412277, 30.443422)
BORYSPIL = GeoPoint(50.349110, 30.897184)
KYIV = GeoPoint(50.450115, 30.524245)
TROYESHCHYNA = GeoPoint(50.516808, 30.600352)
VINOGRADAR = GeoPoint(50.516236, 30.419813)
MARMELAD = GeoPoint(50.445934, 30.442697)
RAILROAD = GeoPoint(50.440756, 30.490026)
BEERWOOD = GeoPoint(50.481086, 30.454878)
BOT_GARDEN = GeoPoint(50.415400, 30.556502)
DARNYTSIA = GeoPoint(50.430836, 30.648600)
BUS_STATION = GeoPoint(50.406793, 30.519341)
VDNH = GeoPoint(50.379930, 30.477425)

locations = [ZHULYANY, BORYSPIL, KYIV, TROYESHCHYNA, VINOGRADAR, MARMELAD,
             RAILROAD, BEERWOOD, BOT_GARDEN, DARNYTSIA, BUS_STATION, VDNH]


class Navigator(object):

    profile = 'mapbox.driving'

    def __init__(self, vin):
        self.service = Directions()
        self.vin = vin
        self.log = log
        self._saver = LocationSaver(self)
        self._location = self._saver.load()
        self._path = GeoLine()
        reactor.callLater(15, self.build_path)

    def get_location(self):
        """
        :rtype: utils.GeoPoint
        """
        return self._location

    def set_location(self, location):
        """
        :type location: utils.GeoPoint
        """
        self._location = location

    def build_path(self, point_to=None):
        """
        :param point_to: Destination point
        :type point_to: utils.GeoPoint
        :return: GeoJson
        :rtype: dict
        """
        origin = self._location.to_feature()
        if not point_to:
            point_to = self.get_random_location()
        self.log.msg('Building path to {}'.format(point_to))
        destination = point_to.to_feature()

        response = self.service.directions([origin, destination],
                                           profile=self.profile,
                                           alternatives=True,
                                           steps=False)
        if response.status_code != 200:
            self.log.msg('Failed to build path: {}. '
                         'Next attempt after 5 minutes.'
                         ''.format(response.content))
            reactor.callLater(300, self.build_path)
        else:
            path = response.geojson()['features'][0]
            self._path = GeoLine.from_dict(path['geometry'])
            props = path['properties']
            self.log.msg(
                'Path built. Distance: {:.2f} km, duration: {}'
                ''.format(props['distance'] / 1000.,
                          datetime.timedelta(seconds=props['duration'])))

    @staticmethod
    def get_random_location():
        return random.choice(locations)

    def is_arrived(self):
        return not self._path

    def get_next_point(self):
        return self._path.get()

    def pop_next_point(self):
        point = self._path.pop_next()
        self.set_location(point)
        if not self._path:
            reactor.callLater(300, self.build_path)
        return point


class LocationSaver(object):
    period = 5

    def __init__(self, obj):
        """
        :type obj: Navigator
        """
        self.obj = obj

    def _get_filename(self):
        return 'data/{}.json'.format(self.obj.vin)

    def load(self):
        """
        :rtype: utils.GeoPoint
        """
        self.call_later()
        if os.path.exists(self._get_filename()):
            try:
                with open(self._get_filename(), 'r') as f:
                    data = json.load(f)
                return GeoPoint.from_dict(data)
            finally:
                pass
        return KYIV

    def save(self):
        point = self.obj.get_location()
        data = point.to_dict()
        with open(self._get_filename(), 'w') as f:
            json.dump(data, f)
        self.call_later()

    def call_later(self):
        reactor.callLater(self.period, self.save)


if __name__ == '__main__':
    pass
