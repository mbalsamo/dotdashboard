import adafruit_display_text.label
import board
import displayio
import busio
import framebufferio
import time
import rgbmatrix
import terminalio
from digitalio import DigitalInOut, Direction
from adafruit_ds3231 import adafruit_ds3231

import os
import ipaddress
import wifi
import socketpool

from adafruit_bitmap_font import bitmap_font

wifiSuccess = False
overwrite = ""
try:
    print()
    print("Attempting Wifi Connection 1")
    wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))
    print("Connected to WiFi at " + os.getenv('CIRCUITPY_WIFI_SSID'))
    pool = socketpool.SocketPool(wifi.radio)
    print("I am now a happy boy")
    print("My IP address is", wifi.radio.ipv4_address)
    print()
    wifiSuccess = True
    overwrite = "WIFI connected on " + os.getenv('CIRCUITPY_WIFI_SSID')
    
except:
    print("wifi failed first attempt!!!") 
    overwrite = "WIFI failed to connect. There is no WIFI. RIP"
    try:
        print("trying wifi 2")
        wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID2'), os.getenv('CIRCUITPY_WIFI_PASSWORD2'))
        print("Connected to WiFi at " + os.getenv('CIRCUITPY_WIFI_SSID2'))
        pool = socketpool.SocketPool(wifi.radio)
        print("I am now a happy boy")
        print("My IP address is", wifi.radio.ipv4_address)
        overwrite = "WIFI connected on " + os.getenv('CIRCUITPY_WIFI_SSID2')
        wifiSuccess = True
    except:
        print("failed wifi attempt on " + os.getenv('CIRCUITPY_WIFI_SSID2'))
        overwrite: "Wifi failed both attempts"




bit_depth_value = 5
base_width = 64
base_height = 32
chain_across = 1
tile_down = 2
serpentine_value = True

width_value = base_width * chain_across
height_value = base_height * tile_down

# If there was a display before (protomatter, LCD, or E-paper), release it so
# we can create ours
displayio.release_displays()

# send register
R1 = DigitalInOut(board.GP2)
G1 = DigitalInOut(board.GP3)
B1 = DigitalInOut(board.GP4)
R2 = DigitalInOut(board.GP5)
G2 = DigitalInOut(board.GP8)
B2 = DigitalInOut(board.GP9)
CLK = DigitalInOut(board.GP11)
STB = DigitalInOut(board.GP12)
OE = DigitalInOut(board.GP13)

R1.direction = Direction.OUTPUT
G1.direction = Direction.OUTPUT
B1.direction = Direction.OUTPUT
R2.direction = Direction.OUTPUT
G2.direction = Direction.OUTPUT
B2.direction = Direction.OUTPUT
CLK.direction = Direction.OUTPUT
STB.direction = Direction.OUTPUT
OE.direction = Direction.OUTPUT



OE.value = True
STB.value = False
CLK.value = False

MaxLed = 64

c12 = [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
c13 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]

for l in range(0, MaxLed):
    y = l % 16
    R1.value = False
    G1.value = False
    B1.value = False
    R2.value = False
    G2.value = False
    B2.value = False

    if c12[y] == 1:
        R1.value = True
        G1.value = True
        B1.value = True
        R2.value = True
        G2.value = True
        B2.value = True
    if l > (MaxLed - 12):
        STB.value = True
    else:
        STB.value = False
    CLK.value = True
    # time.sleep(0.000002) 
    CLK.value = False
STB.value = False
CLK.value = False

for l in range(0, MaxLed):
    y = l % 16
    R1.value = False
    G1.value = False
    B1.value = False
    R2.value = False
    G2.value = False
    B2.value = False

    if c13[y] == 1:
        R1.value = True
        G1.value = True
        B1.value = True
        R2.value = True
        G2.value = True
        B2.value = True
    if l > (MaxLed - 13):
        STB.value = True
    else:
        STB.value = False
    CLK.value = True
    # time.sleep(0.000002)
    CLK.value = False
STB.value = False
CLK.value = False

R1.deinit()
G1.deinit()
B1.deinit()
R2.deinit()
G2.deinit()
B2.deinit()
CLK.deinit()
STB.deinit()
OE.deinit()

# This next call creates the RGB Matrix object itself. It has the given width
# and height. bit_depth can range from 1 to 6; higher numbers allow more color
# shades to be displayed, but increase memory usage and slow down your Python
# code. If you just want to show primary colors plus black and white, use 1.
# Otherwise, try 3, 4 and 5 to see which effect you like best.
#
matrix = rgbmatrix.RGBMatrix(
    width=width_value, height=height_value, bit_depth=bit_depth_value,
    rgb_pins=[board.GP2, board.GP3, board.GP4, board.GP5, board.GP8, board.GP9],
    addr_pins=[board.GP10, board.GP16, board.GP18, board.GP20],
    clock_pin=board.GP11, latch_pin=board.GP12, output_enable_pin=board.GP13,
    tile=tile_down, serpentine=serpentine_value,
    doublebuffer=True)


# Associate the RGB matrix with a Display so that we can use displayio features
display = framebufferio.FramebufferDisplay(matrix, auto_refresh=False)

#display.brightness = .1
display.rotation = 0

# Create two lines of text to scroll. Besides changing the text, you can also
# customize the color and font (using Adafruit_CircuitPython_Bitmap_Font).
# To keep this demo simple, we just used the built-in font.
# The Y coordinates of the two lines were chosen so that they looked good
# but if you change the font you might find that other values work better.

i2c = busio.I2C(board.GP7, board.GP6)
rtc = adafruit_ds3231.DS3231(i2c)
t = rtc.datetime

# font = bitmap_font.load_font("/fonts/creep2.bdf"); # a tad smaller, but monospaced, so actually less text
subtextfont = bitmap_font.load_font("/fonts/frucs6.bdf"); # small font, all caps, lots of space. Good for subtext
mainfont = bitmap_font.load_font("/fonts/frucnorm6.bdf"); # REALLY NICE. FAVORITE. 




def GetCurrentTime(): 
    pm = "am"
    t = rtc.datetime
    temp = t.tm_hour
    #print(t)
    if(t.tm_hour > 12):
        temp = t.tm_hour - 12
    if(t.tm_hour >= 12):
        pm = "pm"
    formatted = time.struct_time((t.tm_year, t.tm_mon, t.tm_mday, temp, t.tm_min, t.tm_sec, 0, -1, -1))

    return formatted, pm


formatted, pm = GetCurrentTime()

line1 = adafruit_display_text.label.Label(
    mainfont,
    color=0x8000ff,
        text="{}:{:02}{}".format(formatted.tm_hour, formatted.tm_min, pm))
line1.x = display.width
line1.y = 5
line1.scale = 2

if line1.scale != 1:
    line1.y = line1.y + (line1.scale)

subText = "This is the dot dashboard"
subTextColor = 0xff8000
if wifiSuccess == False and overwrite != "":
    subText = overwrite
    subTextColor = 0xFF0000

line2 = adafruit_display_text.label.Label(
    mainfont,
    color=subTextColor,
        text="It's Saturday")
line2.x = display.width
line2.y = 17

line3 = adafruit_display_text.label.Label(
    subtextfont,
    color=subTextColor,
    text=subText)
line3.x = display.width
line3.y = 28


# Put each line of text into a Group, then show that group.
g = displayio.Group()
g.append(line1)
g.append(line2)
g.append(line3)
display.show(g)


def setDateTime():
    t = time.struct_time((2023, 11, 13, 15, 34, 00, 0, -1, -1))
    # you must set year, mon, date, hour, min, sec and weekday
    # yearday is not supported, isdst can be set but we don't do anything with it at this time
    print(b"Setting time to:", t)  # uncomment for debugging
    rtc.datetime = t


# This function will scoot one label a pixel to the left and send it back to
# the far right if it's gone all the way off screen. This goes in a function
# because we'll do exactly the same thing with line1 and line2 below.
def scroll(line):
    line.x = line.x - 1
    line_width = line.bounding_box[2]
    if line.x < -line_width:
        line.x = display.width

# This function scrolls lines backwards.  Try switching which function is
# called for line2 below!
def reverse_scroll(line):
    line.x = line.x + 1
    line_width = line.bounding_box[2]
    if line.x >= display.width:
        line.x = -line_width

    
LAST_CHANGE_LINE1 = -1
WAIT_DURATION_LINE1 = .125
LAST_CHANGE_LINE2 = -1
WAIT_DURATION_LINE2 = .15

LAST_CHANGE_CLOCKUPDATE = -1
WAIT_DURATION_CLOCKUPDATE = 60

clockUpdateCount = 0
line3Pause = 7

while True:
    now = time.monotonic()    
    if now >= LAST_CHANGE_LINE1 + WAIT_DURATION_LINE1 and line1.x != 1:
        LAST_CHANGE_LINE1 = now
        scroll(line1)
        if line1.scale == 1:
            scroll(line2)

        # ease in the speed. As it gets closer, delay a little bit more.
        if line1.x < 15:
            WAIT_DURATION_LINE1 += .015

    if now >= LAST_CHANGE_LINE2 + WAIT_DURATION_LINE2 and line3.x != 1:
        #if line3.x == 2:
            #time.sleep(line3Pause)
            # WAIT_DURATION_LINE_2 = 10 
        WAIT_DURATION_LINE_2 = .15

        LAST_CHANGE_LINE2 = now
        scroll(line3)
        
    rtc = adafruit_ds3231.DS3231(i2c)
    formatted, pm = GetCurrentTime()
    line1.text= "{}:{:02}:{:02}".format(formatted.tm_hour, formatted.tm_min, formatted.tm_sec);

    if now >= LAST_CHANGE_CLOCKUPDATE + WAIT_DURATION_CLOCKUPDATE:
        LAST_CHANGE_CLOCKUPDATE = now
        print(now)
        print("clock update " + "{}:{:02}.{}".format(t.tm_hour, t.tm_min, t.tm_sec))
        clockUpdateCount += 1
 

        line3.text="Run time: {} min".format(clockUpdateCount)
    
    # if clockUpdateCount > 5:
    #     line3Pause = 500
        


    #reverse_scroll(line2)
    display.refresh(minimum_frames_per_second=0)

