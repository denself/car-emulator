import json
import os

import settings
from utils.geo import GeoPoint

city_locations = {}


def load_locations(city):
    if city not in city_locations:
        filename = os.path.join(settings.DATA_DIR, '{}.json'.format(city))
        with open(filename) as f:
            data = json.load(f)
        points = [GeoPoint.from_dict(point) for point in data]
        assert len(points) >= 2
        city_locations[city] = points
    return city_locations[city]
