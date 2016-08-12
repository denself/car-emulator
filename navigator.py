import random

import datetime
from mapbox import Directions
from twisted.python import log

from utils.data import load_locations
from utils.geo import GeoLine, GeoVector


class Navigator(object):

    profile = 'mapbox.driving'

    def __init__(self, city, location):
        self.service = Directions()
        self.log = log
        self._locations = load_locations(city)
        self._heading = 0
        self._location = location or self.get_random_location()
        self._path = GeoLine()

    def get_location(self):
        """
        :rtype: utils.GeoPoint
        """
        return self._location

    def get_heading(self):
        """
        :rtype: float
        """
        return self._heading

    def move(self, length):
        """
        :param length: Length of path to move in meters
        :type length: int
        :return: is car arrived
        :rtype: bool
        """
        potential_distance = length
        moved_distance = 0
        while not self.is_arrived():
            old_location = self._location
            next_point = self.get_next_point()

            vector_to_point = next_point - old_location
            self._heading = vector_to_point.heading

            if potential_distance < vector_to_point.meters:
                potential_vector = GeoVector(
                    value=potential_distance, heading=vector_to_point.heading)
                new_location = old_location + potential_vector
                moved_distance += potential_distance
                self._location = new_location
                break

            potential_distance -= vector_to_point.meters
            moved_distance += vector_to_point.meters
            self.pop_next_point()

        return moved_distance

    def set_location(self, location):
        """
        :type location: utils.GeoPoint
        """
        self._location = location

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

    def build_path(self, point_to=None):
        """
        :param point_to: Destination point
        :type point_to: utils.GeoPoint
        :return: Whether path built successfully
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


if __name__ == '__main__':
    pass
