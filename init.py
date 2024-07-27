from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from busio import I2C
import board
import time
import adafruit_ds3231
import os
import sys

i2c = I2C(board.D3, board.D2)
rtc = adafruit_ds3231.DS3231(i2c)
t = rtc.datetime

matrix = False

def DoTheInitThings():
    
    options = RGBMatrixOptions()
    options.drop_privileges = False

    options.rows = 32
    options.cols = 64
    options.chain_length = 1
    options.parallel = 1
    options.row_address_type = 0
    options.multiplexing = 0
    options.pwm_bits = 11
    options.brightness = 100
    options.pwm_lsb_nanoseconds = 130
    options.led_rgb_sequence = "RGB"
    options.pixel_mapper_config = ""
    options.panel_type = ""


    return RGBMatrix(options = options)

def SetDateTime(day, month, year, hour, minute, second, weekday):
    # you must set year, mon, date, hour, min, sec and weekday
    # yearday is not supported, isdst can be set but we don't do anything with it at this time
    t = time.struct_time((year, month, day, hour, minute, second, weekday, -1, -1))
    print(b"Setting time to:", t) 
    print(b"Setting time to:", dir(board)) 
    i2c = I2C(board.SCL, board.SDA)
    rtc = adafruit_ds3231.DS3231(i2c)
    rtc.datetime = t

# init.SetDateTime(22, 6, 2024, 17, 32, 50, 6)

log = False
filename = f"{rtc.datetime.tm_year}-{rtc.datetime.tm_mon}-{rtc.datetime.tm_mday} {rtc.datetime.tm_hour}-{rtc.datetime.tm_min}-{rtc.datetime.tm_sec}" 

if "on-boot" in sys.argv:
    filename += " auto"
else:
    filename += " manual"

if "fake" in sys.argv:
    filename += " fake"


def Log(text):
    print(text)
    if log:
        dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "")
        with open(f'{dir}logs/{filename}.txt', 'a') as file:
            file.write(text + "\n")

        