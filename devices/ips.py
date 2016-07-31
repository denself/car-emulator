import datetime

SD_PACKAGE = '#SD#{date:%d%m%y};{date:%H%M%S};{lat.value};{lat.part};' \
             '{lon.value};{lon.part};{speed};{course};{height};{sats}\r\n'


def get_or_na(data, name, func=lambda x: x):
    if name in data:
        return func(data[name])
    return 'NA'


def to_dec_min(coord, tp):
    if coord != 'NA':
        pat = '{:010.4f}' if tp == 'lon' else '{:09.4f}'
        value = pat.format(abs((coord // 1) * 100 + coord % 1 * 60))
        part = ('EW' if tp == 'lon' else 'NS')[coord < 0]
    else:
        value, part = 'NA'
    return type('DecMin', (object,), {'value': value, 'part': part})


class IPS(object):

    port = 9006
    host = 'dev.mobiliuz.com'
    HANDSHAKE = "#L#{imei};NA\r\n"

    def __init__(self, imei):
        self.imei = imei

    def get_handshake(self):
        return self.HANDSHAKE.format(imei=self.imei)

    def dump(self, data):
        result = ''

        while data:
            result += self.to_sd_package(data.pop(0))

        return result

    @staticmethod
    def to_sd_package(data):
        date = datetime.datetime.utcfromtimestamp(data['gps_time'])
        res = SD_PACKAGE.format(
            date=date, speed=get_or_na(data, 'gps_speed', int),
            lat=to_dec_min(get_or_na(data, 'latitude'), 'lat'),
            lon=to_dec_min(get_or_na(data, 'longitude'), 'lon'),
            course=get_or_na(data, 'heading', int), height='NA', sats='NA',
        )
        return res
