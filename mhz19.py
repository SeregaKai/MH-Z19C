#!/usr/bin/env python

import sys
import time
import serial # need to install pyserial

class TMHZ19(object):
    REQ_READ_CONCENTRATION = b'\xFF\x01\x86\x00\x00\x00\x00\x00\x79'

    class TCommunicationError(Exception):
        pass

    def __init__(self, port, timeout = 1):
        self.port = port
        self.timeout = timeout
        self.ser = serial.Serial(port, baudrate = 9600, timeout = self.timeout)

    def send_request(self, request):
        try:
            self.ser.write(request)
        except serial.SerialTimeoutException:
            raise self.TCommunicationError("timeout while sending request")

    def read_concentration(self):
        self.send_request(self.REQ_READ_CONCENTRATION)
        payload = self.read_response()
        return payload[2] * 256 + payload[3]

    def read_response(self):
        resp_len = 9
        resp = self.ser.read(resp_len)
        payload = list(resp)
        print(f"payload = {payload}")
        if len(resp) != resp_len:
            raise self.TCommunicationError("expected %d bytes, got %d" % (resp_len, len(resp)))

        crc =((sum(payload[1:-1]) % 256) ^ 0xFF) + 1
        if crc != payload[-1]:
            raise self.TCommunicationError("checksum error")

        return payload



class TMQTTMHZ19Sensor(object):

    def init_sensor(self, port):
        self.mhz19 = TMHZ19(port)

    def __init__(self, port):
        self.port = port
        self.poll_interval = 10

    def start(self):
        self.init_sensor(self.port)

        while True:
            try:
                co2_ppm = self.mhz19.read_concentration()
            except TMHZ19.TCommunicationError:
                print("TMHZ19.TCommunicationError")
            else:
                print(f"co2 = {co2_ppm}")

            time.sleep(self.poll_interval)

        return 0


def main():
    if len(sys.argv) != 2:
        print("Please pass com port as arg!")
        return 1

    sensor = TMQTTMHZ19Sensor(sys.argv[1])
    sensor.start()

    return 0


if __name__ == '__main__':
    main()
