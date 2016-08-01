import json
import sys

from twisted.python import log

import settings
from car import Car
from devices.bce import BCE
from devices.device import Device
from devices.ips import IPS
from loop import Loop


def main():
    loop = Loop()

    with open(settings.CARS_FILE) as f:
        data = json.load(f)
    for item in data:
        city = item.get('city', 'points')
        car = Car(item["VIN"], city)
        device = Device(imei=item["IMEI"], protocol=BCE)
        device.connect_to_car(car)

        loop.add_object(car)
        loop.add_object(device)

    log.startLogging(sys.stdout)
    log.msg('Starting reactor')

    loop.start()


if __name__ == '__main__':
    main()
