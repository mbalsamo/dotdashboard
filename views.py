import adafruit_display_text.label
from adafruit_bitmap_font import bitmap_font
from displayio import Group
from board import GP7, GP6
from busio import I2C
from adafruit_ds3231 import adafruit_ds3231
import time
import api_data as data

class View:
    def __init__(self, display):
        # self.line1_x = 64
        # self.line1_y = 5
        # self.line2_y = 15
        # self.line3_x = 64
        # self.line3_y = 25
        # self.line3_x = 64
        # self.line1_scale = 1
        self.lines = 3
        self.ANIMATE_SLIDE = True
        self.autoscroll_line1 = False
        self.autoscroll_line2 = True
        self.autoscroll_line3 = True

        self.config_Line1IsClock = True


        self.mainfont = bitmap_font.load_font("/fonts/frucnorm6.bdf")
        # self.mainfont = bitmap_font.load_font("/fonts/Dina_r400-6.bdf") # bit chunky

        # self.subtextfont = bitmap_font.load_font("/fonts/frucs6.bdf")
        # self.subtextfont = bitmap_font.load_font("/fonts/tb-8.bdf") #tad smaller, curvy


        # formatted, pm = GetFormattedTime()
        self.line1 = adafruit_display_text.label.Label(
            self.mainfont,
            color=0x8000ff,
                text="")
        self.line1.x = display.width
        self.line1.y = 5
        self.line1.scale = 1

        subText = "This is the dot dashboard"
        subTextColor = 0xff8000

        self.line2 = adafruit_display_text.label.Label(
            self.mainfont,
            color=subTextColor,
                text="ooga booga")
        self.line2.x = display.width
        self.line2.y = 15

        # self.line3 = adafruit_display_text.label.Label(
        #     self.mainfont,
        #     color=subTextColor,
        #     text=subText)
        # self.line3.x = display.width
        # self.line3.y = 25

        self.LINE1_LASTCHANGE = -1
        self.LINE2_LASTCHANGE = -1
        self.LINE3_LASTCHANGE = -1
        self.LINE1_DELAY = .15
        self.LINE2_DELAY = .15
        self.LINE3_DELAY = .15

        g = Group()
        g.append(self.line1)
        g.append(self.line2)
        # g.append(self.line3)
        display.show(g)

    def SetBigClock(self):
        self.line1.font = bitmap_font.load_font("/fonts/Px437_DOS-V_re._JPN16-16.bdf")
        self.lines = 2
        self.line1.y = 12
        self.line2.y = 25

        # Chunkier style
        self.line1.font = bitmap_font.load_font("/fonts/frucnorm6.bdf")
        self.line1.scale = 2
        self.line1.y = 7

    

    def Display(self):
        now = time.monotonic()    

        # Update the clock
        if self.config_Line1IsClock:
            self.line1.text = GetFriendlyTimeString()
            if self.line1.width > 64:
                self.line1.text = GetFriendlyTimeString(hidepm=True)

        if now >= self.LINE1_LASTCHANGE + self.LINE1_DELAY and self.line1.x != 1 and self.ANIMATE_SLIDE:
            self.LINE1_LASTCHANGE = now
            scroll(self.line1)
        if self.lines > 1 and now >= self.LINE2_LASTCHANGE + self.LINE2_DELAY and ((self.line2.x != 1 and self.ANIMATE_SLIDE) or (self.autoscroll_line2 and self.line2.width > 64)):
            self.LINE2_LASTCHANGE = now
            if self.line2.x == 2: #if it reaches the end, delay for a few seconds before scrolling again
                self.LINE2_LASTCHANGE = self.LINE2_LASTCHANGE + 5
            scroll(self.line2)
        # if self.lines > 2 and now >= self.LINE3_LASTCHANGE + self.LINE3_DELAY and ((self.line3.x != 1 and self.ANIMATE_SLIDE) or (self.autoscroll_line3 and self.line3.width > 64)):
        #     self.LINE3_LASTCHANGE = now
        #     if self.line3.x == 2: #if it reaches the end, delay for a few seconds before scrolling again
        #         self.LINE3_LASTCHANGE = self.LINE3_LASTCHANGE + 5

        #     scroll(self.line3)




class CurrentWeather(View):
    def __init__(self, display):
        super().__init__(display)
        self.LINE1_DELAY = 0.08
        self.LINE2_DELAY = 0.08
        self.line1.color = 0x0055aa # nice sky blue
        # self.line1.color = 0xaaffff # diamond baby blue
        self.line2.color = 0xff5500 # nice yelllow


        super().SetBigClock()

    WEATHER_LAST_UPDATE = -99999999
    WEATHER_DELAY = 30 * 60 
    weatherUpdateCount = 0
    i = 0

    def Display(self):
        # Perform the default scrolling
        super().Display()

        # Every 30 minutes needs to update weather 
        now = time.monotonic()   
        if now >= self.WEATHER_LAST_UPDATE + self.WEATHER_DELAY:
            print("it is now time to update the weather from the thing")
            self.WEATHER_LAST_UPDATE = now
            conditions, temperature = data.get_weather(fake = False)
            self.weatherUpdateCount += 1
            if self.weatherUpdateCount > 82:
                self.line2.text = f"{conditions} {temperature}° ({self.weatherUpdateCount})"
            else:
                self.line2.text = f"{conditions} {temperature}°"

            if temperature == "":
                return True

class NightClock(View):
    def __init__(self, display):
        super().__init__(display)
        self.lines = 1
        self.ANIMATE_SLIDE = False
        self.line1.color = 0xFF0000
        self.mainfont = bitmap_font.load_font("/fonts/frucnorm6.bdf")
        # self.subtextfont = bitmap_font.load_font("/fonts/frucs6.bdf")

    def Display(self):
        super().Display()
        self.line1.x = int(32 - self.line1.width / 2)
        self.line1.y = int(16 - self.line1.height / 2)





i2c = I2C(GP7, GP6)
rtc = adafruit_ds3231.DS3231(i2c)
t = rtc.datetime

def GetCurrentTime(): 
    rtc = adafruit_ds3231.DS3231(i2c)
    t = rtc.datetime
    return t

def GetFriendlyTimeString(hidepm = False):
    t = GetCurrentTime()
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
    
    if hidepm:
        return "{}:{:02d} ".format(hours, minutes)
    return "{}:{:02d}{}".format(hours, minutes, am_pm)

def scroll(line):
    line.x = line.x - 1
    line_width = line.bounding_box[2]
    if line.x < -line_width:
        line.x = 64
