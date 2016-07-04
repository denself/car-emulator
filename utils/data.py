import json
from utils.geo import GeoPoint


def load_locations(filename):
    with open(filename) as f:
        data = json.load(f)
    points = [GeoPoint.from_dict(point) for point in data]
    assert len(points) >= 2
    return points
