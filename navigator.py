import random

import datetime
from mapbox import Directions
from twisted.internet import reactor
from twisted.python import log

from utils.data import load_locations
from utils.geo import GeoLine


class Navigator(object):

    profile = 'mapbox.driving'

    def __init__(self, city, location):
        self.service = Directions()
        self.log = log
        self._locations = load_locations(city)
        self._location = location or self.get_random_location()
        self._path = GeoLine()

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
        :return: Whethr path built successfully
        :rtype: bool
        """
        origin = self._location.to_feature()
        if not point_to:
            point_to = self.get_random_location()
        self.log.msg('Building path {} to {}'.format(self._location, point_to))
        destination = point_to.to_feature()

        response = self.service.directions([origin, destination],
                                           profile=self.profile,
                                           alternatives=True,
                                           steps=False)
        if response.status_code != 200:
            self.log.msg('Failed to build path: {}. '
                         'Next attempt after 5 minutes.'
                         ''.format(response.content))
            return False

        path = response.geojson()['features'][0]
        self._path = GeoLine.from_dict(path['geometry'])
        props = path['properties']
        self.log.msg(
            'Path built. Distance: {:.2f} km, duration: {}'
            ''.format(props['distance'] / 1000.,
                      datetime.timedelta(seconds=props['duration'])))
        return True

    def get_random_location(self):
        return random.choice(self._locations)

    def is_arrived(self):
        return not self._path

    def get_next_point(self):
        return self._path.get()

    def pop_next_point(self):
        point = self._path.pop_next()
        self.set_location(point)
        return point


if __name__ == '__main__':
    pass
