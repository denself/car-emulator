import json
import sys

from twisted.python import log

from car import Car
from devices.device import Device
from loop import Loop


def main():
    car = Car('111')
    device = Device()
    device.connect_to_car(car)

    loop = Loop()
    loop.add_object(car)
    loop.add_object(device)

    log.startLogging(sys.stdout)
    log.msg('Starting reactor')

    loop.start()


if __name__ == '__main__':
    main()
