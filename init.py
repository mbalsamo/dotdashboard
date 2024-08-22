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

# matrix = False

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

    # SetDateTime(hour=20, minute=9, second=40)
    # SetDateTime(8, 21, 2024, 16, 4, 20, 4)

    matrix = RGBMatrix(options = options)
    do_loading_screen(matrix)
    return matrix

def SetDateTime(month=rtc.datetime.tm_mon, day=rtc.datetime.tm_mday, year=rtc.datetime.tm_year, hour=rtc.datetime.tm_hour, minute=rtc.datetime.tm_min, second=0, weekday=rtc.datetime.tm_wday):
    # you must set year, mon, date, hour, min, sec and weekday
    # yearday is not supported, isdst can be set but we don't do anything with it at this time
    t = time.struct_time((year, month, day, hour, minute, second, weekday, -1, -1))
    print("\033[94m {}\033[00m" .format(f"Setting time to:"))
    print("\033[94m {}\033[00m" .format(t))
    i2c = I2C(board.SCL, board.SDA)
    rtc = adafruit_ds3231.DS3231(i2c)
    rtc.datetime = t



def do_loading_screen(matrix):
    canvas = matrix.CreateFrameCanvas()
    
    font = graphics.Font()
    # font = fontg.LoadFont(os.path.join(os.path.dirname(os.path.realpath(__file__)), "/assets/fonts/t0-22-uni.bdf"))

    location = os.path.join(os.path.dirname(os.path.realpath(__file__)), "")
    location += "/assets/fonts/frucnorm6.bdf"
    font.LoadFont(location)
    color = graphics.Color(150, 150, 150)
    text = "loading..."

    global t
    hours = t.tm_hour
    minutes = t.tm_min
    
    if hours == 0:
        hours = 12
        am_pm = "am"
    elif hours == 12:
        am_pm = "pm"
    elif hours > 12:
        hours -= 12
        am_pm = "pm"
    else:
        am_pm = "am"
    text = "{}:{:02d}{}".format(hours, minutes, am_pm)
    graphics.DrawText(canvas, font, 15, 15, color, text)
    canvas = matrix.SwapOnVSync(canvas)


logging = False
filename = (
    "{:02d}-{:02d}-{:02d} {:02d}-{:02d}-{:02d}".format(
        t.tm_year,
        t.tm_mon,
        t.tm_mday,
        t.tm_hour,
        t.tm_min,
        t.tm_sec
    )
)

if "on-boot" in sys.argv:
    filename += " on-boot"
else:
    filename += " manual"

if "fake" in sys.argv:
    filename += " fake"

if "log" in sys.argv or logging:
    log("WE LOGGIN")
    logging = True

dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "")

def log(text, error = False):
    print(text)
    global t
    date = (
        "{:02d}/{:02d} {:02d}:{:02d}:{:02d}".format(
            t.tm_mon,
            t.tm_mday,
            t.tm_hour,
            t.tm_min,
            t.tm_sec
        )
    )
    if logging:
        with open(f'{dir}logs/normal/{filename}.txt', 'a') as file:
            file.write(date + " " + text + "\n")
    
    if error:
        with open(f'{dir}logs/errors/err {filename}.txt', 'a') as file:
            file.write(date + " " + text + "\n")


def log_error(text):
    print()
    print("\033[91m {}\033[00m" .format("LOGGING ERROR:"))
    
    # If it is just a string
    if isinstance(text, str):  
        log(text, error=True)
    # List of strings
    elif isinstance(text, list) and all(isinstance(item, str) for item in text):  
        for t in text:
            log(t, error=True)
