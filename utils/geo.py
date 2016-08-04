import math

from geopy.distance import great_circle


class GeoPoint(object):
    # precision in degrees between two points
    d = 0.000001

    def __init__(self, latitude=0., longitude=0.):
        self.latitude = latitude
        self.longitude = longitude

    @classmethod
    def from_reversed(cls, lon, lat):
        return cls(lat, lon)

    @property
    def lat_rad(self):
        return math.radians(self.latitude)

    @property
    def lon_rad(self):
        return math.radians(self.longitude)

    def get_lat_lon(self):
        return self.latitude, self.longitude

    def get_lon_lat(self):
        return self.longitude, self.latitude

    def to_dict(self):
        return {
            'type': 'Point',
            'coordinates': self.get_lon_lat()
        }

    def to_feature(self):
        return {
            'type': 'Feature',
            'geometry': self.to_dict()
        }

    @classmethod
    def from_dict(cls, data):
        assert data['type'] == 'Point'
        return cls.from_reversed(*data['coordinates'])

    def __sub__(self, other):
        """
        :rtype: GeoVector
        """
        assert isinstance(other, GeoPoint)
        # Calculated distance between two points
        distance = great_circle(self.get_lat_lon(), other.get_lat_lon())
        heading = bearing(other, self)
        return GeoVector(distance.meters, heading)

    def __add__(self, other):
        assert isinstance(other, GeoVector)
        _point = great_circle().destination(
            self.get_lat_lon(), other.heading, other.kilometers)
        return GeoPoint(_point.latitude, _point.longitude)

    def __eq__(self, other):
        return (abs(self.latitude - other.latitude) < self.d) and \
               (abs(self.longitude - other.longitude) < self.d)

    def __str__(self):
        return 'GeoPoint({:.6f}, {:.6f})'.format(*self.get_lat_lon())


class GeoVector(object):
    def __init__(self, value=0., heading=0.):
        self._value = value  # vector length in m
        self._heading = heading  # vector angle in degrees

    def __str__(self):
        return 'GeoVector({:.6f}, {:.4f})'.format(self.meters, self.heading)

    @property
    def heading(self):
        """
        :return: Vector heading 0..359.9 in degrees
        """
        return self._heading % 360

    @property
    def meters(self):
        """
        :return: Get vector length in meters (m)
        """
        return self._value

    @property
    def kilometers(self):
        """
        :return: Get vector length in kilometers (km)
        """
        return self._value / 1000.


class GeoLine(object):
    def __init__(self):
        self._points = []
        self._pointer = 0

    def __nonzero__(self):
        return len(self._points) > self._pointer

    def get(self, i=0):
        return GeoPoint.from_reversed(*self._points[self._pointer + i])

    def pop_next(self):
        res = self.get()
        self._pointer += 1
        return res

    def to_dict(self):
        return {
            'type': 'LineString',
            'coordinates': self._points
        }

    def to_feature(self):
        return {
            'type': 'Feature',
            'geometry': self.to_dict()
        }

    @classmethod
    def from_dict(cls, data):
        assert data['type'] == 'LineString'
        line = cls()
        line._points = data['coordinates'][:]
        return line

    @classmethod
    def from_feature(cls, data):
        assert data['type'] == 'Feature'
        return cls.from_dict(data['geometry'])

    def __str__(self):
        return "GeoLine({}..)".format(self.get())


def bearing(point1, point2):
    d_lon = point2.lon_rad - point1.lon_rad

    y = math.sin(d_lon) * math.cos(point2.lat_rad)
    x = math.cos(point1.lat_rad) * math.sin(point2.lat_rad) - \
        math.sin(point1.lat_rad) * math.cos(point2.lat_rad) * math.cos(d_lon)

    return math.degrees(math.atan2(y, x))


def to_hours(seconds):
    return seconds / (60. * 60.)


if __name__ == '__main__':
    path = GeoLine()
    path._points = [(50.412277, 30.443422),
                    (50.349110, 30.897184),
                    (50.450115, 30.524245)]
    for i in range(10):
        print path.get()
