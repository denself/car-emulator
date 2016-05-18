"""
?	_Bool	bool	1
b	signed char		integer	1
B	unsigned char	integer	1
h	short			integer	2
H	unsigned short	integer	2
i	int				integer	4
I	unsigned int	integer	4
l	long			integer	4
L	unsigned long	integer	4
q	long long		integer	8
Q	unsigned long long	integer	8
"""
import struct
import time


class BCE(object):

    port = 9004
    host = 'localhost'
    HANDSHAKE = "#BCE#\r\n"

    def __init__(self, imei):
        self._confirmation_key = -1
        self.imei = imei

    def dump(self, data):
        result = struct.pack('L', int(self.imei))

        for packages in [data]:
            result += BCEMessage.dump(packages)

        result += self._get_cs(result)
        return result

    def _get_confirmation_key(self):
        self._confirmation_key += 1
        self._confirmation_key %= 256
        return struct.pack('B', self._confirmation_key)

    @staticmethod
    def _get_cs(data):
        cs = sum(ord(c) for c in data) % 256
        return struct.pack('B', cs)


class BCEMessage(object):

    CONFIRMATION_KEY_MASK = 0x7F
    ASYNC_STACK = 0xA5
    STACK_CONFIRM = 0x19
    TIME_TRIGGERED_PACKET = 0xA0
    OUTPUT_CONTROL = 0x41
    OUTPUT_CONTROL_ACK = 0xC1
    READ_FW_VERSION = 0x08
    READ_FW_VERSION_ACK = 0x88

    @staticmethod
    def dump(data, package_type=TIME_TRIGGERED_PACKET):

        result = struct.pack('BB', package_type, 0)
        while data:
            result += BCEMessageData.dump(data.pop(0))

        message_length = len(result)
        return struct.pack('H', message_length) + result


class BCEMessageData(object):
    @staticmethod
    def dump(data, data_type=0x07):
        gps_time = data.get('gps_time') or time.time()
        time_type = ((int(gps_time) - 0x47798280) / 2)
        time_type <<= 4
        time_type += data_type
        result = struct.pack('I', time_type)
        if data_type == 0x07:
            result += BCEDataType7.dump(data)

        message_length = len(result)
        return struct.pack('B', message_length) + result


class BCEDataType7(object):
    @staticmethod
    def dump(data):
        return BCEDataType7Mask1.dump(data)


class BCEDataType7Mask1(object):
    @staticmethod
    def dump(data):
        mask = 0
        result = ''
        if 'latitude' in data:
            result += struct.pack('f', data.get('longitude', 0))
            result += struct.pack('f', data.get('latitude', 0))
            result += struct.pack('B', data.get('gps_speed', 0))
            gps_quality = data.get('hdop', 0) & 0xf
            gps_quality <<= 4
            gps_quality += data.get('satellites', 0) & 0xf
            result += struct.pack('B', gps_quality)
            result += struct.pack('B', data.get('heading', 0) / 2)
            result += struct.pack('h', data.get('altitude', 0))
            result += struct.pack('f', data.get('odometer', 0))
            mask |= 1

        return struct.pack('H', mask) + result


if __name__ == '__main__':
    dt = {
        'gps_time': time.time(),
        'latitude': 12.34,
        'longitude': 34.56
    }
    b = BCE()
    b.add_message(dt)
    res = BCE.dump('351777042773935')
    print res.encode('hex')
