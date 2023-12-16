from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from busio import I2C
import board
import time
from adafruit_ds3231 import adafruit_ds3231
import os

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

    
    # OLD PICO RGBMATRIX LIBRARY:

    # gc.collect()
    # print("-" * 40)
    # print(f"Initializing boot - Current free memory: {gc.mem_free()}")


    # bit_depth_value = 2
    # base_width = 64
    # base_height = 32
    # chain_across = 1
    # tile_down = 2
    # serpentine_value = True

    # width_value = base_width * chain_across
    # height_value = base_height * tile_down

    # # If there was a display before (protomatter, LCD, or E-paper), release it so
    # # we can create ours
    # displayio.release_displays()

    # # send register
    # R1 = displayio.DigitalInOut(board.GP2)
    # G1 = displayio.DigitalInOut(board.GP3)
    # B1 = displayio.DigitalInOut(board.GP4)
    # R2 = displayio.DigitalInOut(board.GP5)
    # G2 = displayio.DigitalInOut(board.GP8)
    # B2 = displayio.DigitalInOut(board.GP9)
    # CLK = displayio.DigitalInOut(board.GP11)
    # STB = displayio.DigitalInOut(board.GP12)
    # OE = displayio.DigitalInOut(board.GP13)

    # R1.direction = Direction.OUTPUT
    # G1.direction = Direction.OUTPUT
    # B1.direction = Direction.OUTPUT
    # R2.direction = Direction.OUTPUT
    # G2.direction = Direction.OUTPUT
    # B2.direction = Direction.OUTPUT
    # CLK.direction = Direction.OUTPUT
    # STB.direction = Direction.OUTPUT
    # OE.direction = Direction.OUTPUT

    # OE.value = True
    # STB.value = False
    # CLK.value = False

    # MaxLed = 64

    # c12 = [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    # c13 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]

    # for l in range(0, MaxLed):
    #     y = l % 16
    #     R1.value = False
    #     G1.value = False
    #     B1.value = False
    #     R2.value = False
    #     G2.value = False
    #     B2.value = False

    #     if c12[y] == 1:
    #         R1.value = True
    #         G1.value = True
    #         B1.value = True
    #         R2.value = True
    #         G2.value = True
    #         B2.value = True
    #     if l > (MaxLed - 12):
    #         STB.value = True
    #     else:
    #         STB.value = False
    #     CLK.value = True
    #     # time.sleep(0.000002) 
    #     CLK.value = False
    # STB.value = False
    # CLK.value = False

    # for l in range(0, MaxLed):
    #     y = l % 16
    #     R1.value = False
    #     G1.value = False
    #     B1.value = False
    #     R2.value = False
    #     G2.value = False
    #     B2.value = False

    #     if c13[y] == 1:
    #         R1.value = True
    #         G1.value = True
    #         B1.value = True
    #         R2.value = True
    #         G2.value = True
    #         B2.value = True
    #     if l > (MaxLed - 13):
    #         STB.value = True
    #     else:
    #         STB.value = False
    #     CLK.value = True
    #     # time.sleep(0.000002)
    #     CLK.value = False
    # STB.value = False
    # CLK.value = False

    # R1.deinit()
    # G1.deinit()
    # B1.deinit()
    # R2.deinit()
    # G2.deinit()
    # B2.deinit()
    # CLK.deinit()
    # STB.deinit()
    # OE.deinit()

    # # This next call creates the RGB Matrix object itself. It has the given width
    # # and height. bit_depth can range from 1 to 6; higher numbers allow more color
    # # shades to be displayed, but increase memory usage and slow down your Python
    # # code. If you just want to show primary colors plus black and white, use 1.
    # # Otherwise, try 3, 4 and 5 to see which effect you like best.
    # #
    # gc.collect()
    # print(f"Starting display buffer - Current free memory: {gc.mem_free()}")

    # matrix = rgbmatrix.RGBMatrix(
    #     width=width_value, height=height_value, bit_depth=bit_depth_value,
    #     rgb_pins=[board.GP2, board.GP3, board.GP4, board.GP5, board.GP8, board.GP9],
    #     addr_pins=[board.GP10, board.GP16, board.GP18, board.GP20],
    #     clock_pin=board.GP11, latch_pin=board.GP12, output_enable_pin=board.GP13,
    #     tile=tile_down, serpentine=serpentine_value,
    #     doublebuffer=True)

    # # Associate the RGB matrix with a Display so that we can use displayio features
    # display = framebufferio.FramebufferDisplay(matrix, auto_refresh=False)

    # print(f"Display init successful. Free mem - {gc.mem_free()}")
    # del matrix
    # gc.collect()
    # print(f"Display init successful. Free mem - {gc.mem_free()}")
    # print("-" * 40)

    # display.rotation = 0
    # return display


# def InitiateWifiConnection(num):
#     SSID = os.getenv('CIRCUITPY_WIFI_SSID')
#     PASSWORD = os.getenv('CIRCUITPY_WIFI_PASSWORD')

#     if num == 2:
#         SSID = os.getenv('CIRCUITPY_WIFI_SSID2')
#         PASSWORD = os.getenv('CIRCUITPY_WIFI_PASSWORD2')

#     try:
#         print()
#         print("Attempting Wifi Connection on " + SSID)
#         wifi.radio.connect(SSID, PASSWORD)
#         print("Connected to WiFi")
#         pool = socketpool.SocketPool(wifi.radio)
#         print("I am now a happy boy")
#         print("My IP address is", wifi.radio.ipv4_address)
#         return True
#     except:
#         print("Wifi failed for " + SSID)
#         return False

# def AttemptAllWifi():
#     wifiAttempts = 0
#     wifiSuccess = False
#     while wifiSuccess == False and wifiAttempts <= 4:
#         wifiSuccess = InitiateWifiConnection(1)    
#         wifiAttempts += 1
#         time.sleep(2)

#     while wifiSuccess == False and wifiAttempts <= 6:
#         wifiSuccess = InitiateWifiConnection(2)    
#         wifiAttempts += 1
#         time.sleep(2)
#     print("There were {} wifi attempts".format(wifiAttempts))
#     print()
#     return wifiSuccess


def setDateTime():
    # you must set year, mon, date, hour, min, sec and weekday
    # yearday is not supported, isdst can be set but we don't do anything with it at this time
    t = time.struct_time((2023, 11, 13, 15, 34, 00, 0, -1, -1))
    print(b"Setting time to:", t) 
    i2c = busio.I2C(board.GP7, board.GP6)
    rtc = adafruit_ds3231.DS3231(i2c)
    rtc.datetime = t
