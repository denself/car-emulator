import math

from geopy.distance import great_circle


class GeoPoint(object):
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
            'coordinates': [self.longitude, self.latitude]
        }

    @classmethod
    def from_dict(cls, data):
        assert data['type'] == 'Point'
        point = cls()
        point.latitude = data['latitude']
        point.longitude = data['longitude']

    def __sub__(self, other):
        """
        :rtype: GeoVector
        """
        assert isinstance(other, GeoPoint)
        distance = great_circle(self.get_lat_lon(), other.get_lat_lon()).km
        heading = bearing(other, self)
        return GeoVector(distance, heading)

    def __add__(self, other):
        assert isinstance(other, GeoVector)
        _point = great_circle().destination(self.get_lat_lon(),
                                            other.heading, other.value)
        return GeoPoint(_point.latitude, _point.longitude)

    def __str__(self):
        return 'GeoPoint({:.6f}, {:.6f})'.format(*self.get_lat_lon())


class GeoVector(object):
    def __init__(self, value=0., heading=0.):
        self.value = value
        self.heading = heading

    def __str__(self):
        return 'GeoVector({:.6f}, {:.4f})'.format(self.value, self.heading)

    @property
    def meters(self):
        return self.value * 1000



def bearing(point1, point2):
    d_lon = point2.lon_rad - point1.lon_rad

    y = math.sin(d_lon) * math.cos(point2.lat_rad)
    x = math.cos(point1.lat_rad) * math.sin(point2.lat_rad) - \
        math.sin(point1.lat_rad) * math.cos(point2.lat_rad) * math.cos(d_lon)

    brng = math.atan2(y, x)
    return math.degrees(brng)


def to_hours(seconds):
    return seconds / (60. * 60.)

if __name__ == '__main__':
    p1 = GeoPoint(50.443622, 30.512418)
    p2 = GeoPoint(50.445727, 30.515208)
    print p1
    print p2
    v1 = p2 - p1
    print v1
    print p1 + v1
