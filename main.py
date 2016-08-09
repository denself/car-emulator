import json
import sys

from twisted.python import log

import settings
from car import Car
from devices.bce import BCE
from devices.device import Device
from devices.ips import IPS
from loop import Loop
from utils.datehelper import Schedule


def main():
    loop = Loop()

    log.startLogging(sys.stdout)
    log.msg('Starting reactor')

    with open(settings.CARS_FILE) as f:
        data = json.load(f)
    for item in data:
        city = item.get('city', 'points')
        schedule = Schedule.from_dict(item.get('schedule'))
        car = Car(item["VIN"], city, schedule)
        device = Device(imei=item["IMEI"], protocol=BCE)
        device.connect_to_car(car)

        loop.add_object(car)
        loop.add_object(device)

    loop.start()


if __name__ == '__main__':
    main()
