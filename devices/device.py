import time

from twisted.internet.protocol import ClientFactory, Protocol

from devices.bce import BCE
from devices.transport import Transport, TransportFactory
from interfaces import IUpdatable


class Device(ClientFactory, IUpdatable):

    sending_period = 5
    pushing_period = 5

    def __init__(self, imei='350000000000035', protocol=BCE):
        """
        :type self.last_point: utils.GeoPoint
        """
        self.car = None
        self.imei = imei
        self.data = {}
        self.last_send_time = time.time()
        self.last_push_time = time.time()
        self.last_point = None
        self.stack = []
        self.transport = TransportFactory(protocol(imei))

    def connect_to_car(self, car):
        """
        Connect current device to car, that should be observed
        :param car: Observable car
        :type car: interfaces.ICar
        """
        self.car = car
        self.last_point = car.get_location()

    def update(self, t):
        if not self.car:
            return
        now = time.time()
        self.update_values()
        if self.is_time_to_push():
            self.update_sending_values(now)
            self.push_data()
        if self.is_time_to_send():
            self.send_data()

    def is_time_to_send(self):
        return time.time() - self.last_send_time > self.sending_period

    def is_time_to_push(self):
        return time.time() - self.last_push_time > self.pushing_period

    def update_values(self):
        car_speed = self.car.get_speed()
        old_speed = self.data.get('speed', 0)
        self.data['speed'] = max(old_speed, car_speed)

    def update_sending_values(self, now):
        car_position = self.car.get_location()

        path = car_position - self.last_point
        time_passed = now - self.last_push_time
        speed = path.value / (time_passed / 3600.)

        self.data['latitude'] = car_position.latitude
        self.data['longitude'] = car_position.longitude
        self.data['gps_time'] = now
        self.data['gps_speed'] = int(speed)
        self.data['hdop'] = 1
        self.data['satellites'] = 12
        self.data['odometer'] = path.meters
        self.data['heading'] = self.car.get_heading()
        self.last_point = car_position

    def push_data(self):
        self.stack.append(self.data)
        self.data = {}
        self.last_push_time = time.time()

    def send_data(self):
        self.transport.send(self.stack)
        self.last_send_time = time.time()
