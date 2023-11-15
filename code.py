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
from adafruit_bitmap_font import bitmap_font
import init
import views
import data



display = init.DoTheInitThings()

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
line1.scale = 1

if line1.scale != 1:
    line1.y = line1.y + (line1.scale)

temp, conditions = data.get_weather()

subText = "This is the dot dashboard"
subTextColor = 0xff8000
# if wifiSuccess == False and overwrite != "":
#     subText = overwrite
#     subTextColor = 0xFF0000

line2 = adafruit_display_text.label.Label(
    mainfont,
    color=subTextColor,
        text="{} {}F*".format(conditions, temp))
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
    line1.text= "{}:{:02}{}".format(formatted.tm_hour, formatted.tm_min, pm);

    if now >= LAST_CHANGE_CLOCKUPDATE + WAIT_DURATION_CLOCKUPDATE:
        LAST_CHANGE_CLOCKUPDATE = now
        print(now)
        print("clock update " + "{}:{:02}".format(t.tm_hour, t.tm_min, t.tm_sec))
        clockUpdateCount += 1
 

        line3.text="Run time: {} min".format(clockUpdateCount)
    
    display.refresh(minimum_frames_per_second=0)

