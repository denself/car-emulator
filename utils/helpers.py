
def to_meters_per_second(value):
    """
    Convert speed from kilometers per hour to meters per second
    formula:
      speed * 1000m / 60m / 60s
    :param value: Speed in km/h
    :return: Speed in m/s
    """
    return value / 3.6


def to_kilometers_per_hour(value):
    """
    Convert speed from meters per second to kilometers per hour
    formula:
      speed * 60s * 60m / 1000m
    :param value: Speed in m/h
    :return: Speed in km/s
    """
    return value * 3.6


def to_liters_per_meter(value):
    """
    Converts fuel consumption speed from liters per 100km to liters per meter
    formula:
        fuel_consumption / 100km / 1000m
    :param value: Fuel consumption in liters per 100km
    :return: Fuel consumption in liters per meter
    """
    return value / 100000.
