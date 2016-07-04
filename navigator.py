import json
import os
import random

import datetime
from mapbox import Directions
from twisted.internet import reactor
from twisted.python import log

import settings
from utils.data import load_locations
from utils.geo import GeoLine, GeoPoint

locations = load_locations(settings.POINTS_FILE)


class Navigator(object):

    profile = 'mapbox.driving'

    def __init__(self, vin):
        self.service = Directions()
        self.vin = vin
        self.log = log
        self._saver = LocationSaver(self)
        self._location = self._saver.load() or self.get_random_location()
        self._path = GeoLine()
        reactor.callLater(5, self.build_path)

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
