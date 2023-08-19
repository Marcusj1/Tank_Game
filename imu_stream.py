# code to read mpu9250 and control GPIO
import socket
import smbus
import math
import time
import RPi.GPIO as GPIO
import numpy as np
import logging
from datetime import datetime
import statistics
from _thread import *

# GPIO.setmode(GPIO.BCM)
# GPIO.setup(12, GPIO.OUT)

# Register
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c


def read_byte(reg):
    return bus.read_byte_data(address, reg)


def read_word(reg):
    h = bus.read_byte_data(address, reg)
    l = bus.read_byte_data(address, reg + 1)
    value = (h << 8) + l
    return value


def read_mag_word(reg):
    l = bus.read_byte_data(address, reg)
    h = bus.read_byte_data(address, reg + 1)
    value = (h << 8) + l
    return value


def read_mag_word_2c(reg):
    val = read_mag_word(reg)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val


def read_word_2c(reg):
    val = read_word(reg)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val


def dist(a, b):
    return math.sqrt((a * a) + (b * b))


def get_y_rotation(x, y, z):
    radians = math.atan2(x, dist(y, z))
    return math.degrees(radians)


def get_x_rotation(x, y, z):
    radians = math.atan2(y, dist(x, z))
    return math.degrees(radians)


def data_wrapper(name, value):
    prepared_string = str({"[", name, ":",  value, "]"})
    return prepared_string


bus = smbus.SMBus(1)  # bus = smbus.SMBus(0) fuer Revision 1
address = 0x68  # via i2cdetect

# Activate the MPU so the module can talk to it
bus.write_byte_data(address, power_mgmt_1, 0)
bus.write_byte_data(address, 28, 0)  # change range of z-axis accelerometer

logging.basicConfig(filename='Data.log', level=logging.DEBUG)
logging.info("Time (sec)  xRot   yRot")

#################################


def client(conn, connection_number):
    ACCEL_BUFFER_SIZE = 100
    y = [1] * ACCEL_BUFFER_SIZE
    gyro = []
    i = 0

    def send(data_name, data_value):
        wrapped_data = data_wrapper(data_name, data_value)
        conn.send(str.encode(wrapped_data))

    while True:

        i += 1
        if i > ACCEL_BUFFER_SIZE - 1:
            i = 0
        time.sleep(0.001)
        inst_time = float(time.time())

        gyroskop_xout = read_word_2c(0x43)
        scaled_gyro_xout = gyroskop_xout / 131

        beschleunigung_xout = read_word_2c(0x3b)
        beschleunigung_yout = read_word_2c(0x3d) + 6000
        beschleunigung_zout = read_word_2c(0x3f) + 4800
        x = read_mag_word_2c(0x0C)

        beschleunigung_xout_skaliert = beschleunigung_xout / 16384.0
        beschleunigung_yout_skaliert = beschleunigung_yout / 16384.0
        beschleunigung_zout_skaliert = beschleunigung_zout / 16384.0

        ax = beschleunigung_xout_skaliert
        ay = beschleunigung_yout_skaliert
        az = beschleunigung_zout_skaliert

        xRot = get_x_rotation(beschleunigung_xout_skaliert, beschleunigung_yout_skaliert, beschleunigung_zout_skaliert)
        yRot = get_y_rotation(beschleunigung_xout_skaliert, beschleunigung_yout_skaliert, beschleunigung_zout_skaliert)

        current_accel = math.sqrt(ax ** 2 + ay ** 2 + az ** 2)
        y[i] = current_accel
        gyro.append(scaled_gyro_xout)

        # math:
        avg_accel = sum(y) / len(y)
        std_dev = statistics.pstdev(y)

        send("avg accel:", avg_accel)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 5555
server = "192.168.1.2"

try:
    sock.bind((server, port))
except socket.error as e:
    str(e)

sock.listen(2)
connection_number = 0

while True:
    conn, addr = sock.accept()

    start_new_thread(client, (conn, connection_number))
    connection_number += 1


#################################