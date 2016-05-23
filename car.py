from interfaces import ICar, IUpdatable
from navigator import Navigator
from utils import to_hours, GeoVector

MAIDAN = 50.450115, 30.524245
TROYESHCHYNA = 50.516808, 30.600352
VINOGRADAR = 50.516236, 30.419813
MARMELAD = 50.445934, 30.442697


class Car(ICar, IUpdatable):
    def __init__(self, vin):
        self._vin = vin
        self._navigator = Navigator(vin)
        self._speed = 60
        self._heading = 0
        self._mileage = 0

    def get_heading(self):
        return self._heading

    def get_speed(self):
        return self._speed

    def get_location(self):
        return self._navigator.get_location()

    def get_odometer_value(self):
        return self._mileage

    def update(self, t):
        self._move(to_hours(t))

    def _move(self, t):
        potential_distance = t * self._speed

        while not self._navigator.is_arrived():
            old_location = self._navigator.get_location()
            next_point = self._navigator.get_next_point()

            vector_to_point = next_point - old_location
            self._heading = vector_to_point.heading % 360

            if potential_distance < vector_to_point.value:
                potential_vector = GeoVector(potential_distance,
                                             vector_to_point.heading)
                new_location = old_location + potential_vector
                self._navigator.set_location(new_location)
                break

            potential_distance -= vector_to_point.value
            self._navigator.pop_next_point()
