import os

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'data')
if not os.path.isdir(DATA_DIR):
    os.mkdir(DATA_DIR)


POINTS_FILE = os.path.join(DATA_DIR, 'points.json')
CARS_FILE = os.path.join(DATA_DIR, 'cars.json')


LOGS_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.isdir(LOGS_DIR):
    os.mkdir(LOGS_DIR)
