# import adafruit_display_text.label
# from adafruit_bitmap_font import bitmap_font
# from displayio import Group
import board
from adafruit_ds3231 import adafruit_ds3231
import time
import api_data as data
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from init import i2c
import os
from PIL import Image

class Line:
    def __init__(self, matrix):
        self.canvas = matrix.CreateFrameCanvas()

        self.isText = True
        self.text = ""
        self.isImage = False
        self.imageDir = ""

        self.animateInitialSlide = True
        self.animateLastChange = -1
        self.animateDelay = .15
        self.animateAutoScroll = True

        self.isClock = False
        self.isCentered = False
        self.font = graphics.Font()
        # self.font.LoadFont(os.path.join(os.path.dirname(os.path.realpath(__file__)), "fonts/t0-22-uni.bdf"))
        self.SetFont("pixelmix-b6.bdf")

        self.x = 1
        self.y = 10
        self.max_x = 64
        self.min_x = 0

        # self.color = graphics.Color(0, 85, 170) # too dark
        self.color = hex_to_rgb("0099cc")

        self.length = 0
        self.background = True

    def SetFont(self, fontName):
        dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "")
        if "fonts/" not in fontName:
            dir += "fonts/"
        dir += fontName
        if ".bdf" not in fontName:
            dir += ".bdf"

        print(f"loading the font {dir}")
        self.font = graphics.Font()
        self.font.LoadFont(dir)
        # self.mainfont = bitmap_font.load_font("/fonts/frucnorm6.bdf")
        # # self.mainfont = bitmap_font.load_font("/fonts/Dina_r400-6.bdf") # bit chunky

        # # self.subtextfont = bitmap_font.load_font("/fonts/frucs6.bdf")
        # # self.subtextfont = bitmap_font.load_font("/fonts/tb-8.bdf") #tad smaller, curvy

    def SetBigClock(self):
        print("setting big clock now")
        self.isClock = True
        # self.SetFont("helvR12.bdf")
        self.y = 11
        self.animateAutoScroll = False
        self.isCentered = True

        self.SetFont("IMB_EGA_8x8.bdf")
        self.y = 18


        # self.line1.font = bitmap_font.load_font("/fonts/Px437_DOS-V_re._JPN16-16.bdf")
        # self.lines = 2
        # self.line1.y = 12
        # self.line2.y = 25

        # # Chunkier style
        # self.line1.font = bitmap_font.load_font("/fonts/frucnorm6.bdf")
        # self.line1.scale = 2
        # self.line1.y = 7

    def SetImage(self, imageDir):
        self.imageDir = imageDir
        self.isImage = True



class View:
    def __init__(self, matrix):
        self.lines = []
        # subTextColor = 0xff8000
    

    def Display(self, matrix):
        now = time.monotonic()    
        for line in self.lines:
            line.canvas.Clear()

            # if line.background == True:
            #     DrawRectangle(line.canvas, line.x, line.y-7, line.x + line.length, line.y,  graphics.Color(0, 22, 0))

            if line.isText:
                line.length = graphics.DrawText(line.canvas, line.font, line.x, line.y, line.color, line.text)
                if line.isClock:
                    # if line.length >= 60:
                    #     line.text = GetFriendlyTimeString(hidepm=True)
                    # else:
                    line.text = GetFriendlyTimeString()

            # print("----------")
            # print("ANALYZING LINE", line.text)
            # print(f"if {now} >= {line.animateLastChange} + {line.animateDelay} and (({line.x} != 1 and {line.animateInitialSlide}) or ({line.animateAutoScroll} and {line.length} > 64)):")
            if now >= line.animateLastChange + line.animateDelay and ((line.x != line.min_x and line.animateInitialSlide) or (line.animateAutoScroll and line.length > line.max_x)):
                line.animateLastChange = now
                # pause when it hits left side
                if line.x == 3:
                    line.animateLastChange += 10
                line.x = scroll(line.min_x, line.max_x, line.x, line.length)


            if line.isImage:
                print("WE HAVE AN IMAGE???")
                image = Image.open(line.imageDir).convert('RGB')
                image.resize((matrix.width, matrix.height), Image.ANTIALIAS)

                img_width = 64
                img_height = 32 
                xpos = 0
                while True:
                    xpos += 1
                    if (xpos > img_width):
                        xpos = 0

                    line.canvas.SetImage(image, -xpos)
                    line.canvas.SetImage(image, -xpos + img_width)

                    line.canvas = matrix.SwapOnVSync(line.canvas)
                    time.sleep(0.01)

            

            if line.isCentered:
                line.x = int(32 - line.length / 2)
            line.canvas = matrix.SwapOnVSync(line.canvas)
            



class CurrentWeather(View):
    def __init__(self, matrix):
        print("Initializing the view for CurrentWeather")
        super().__init__(matrix)

        self.line1 = Line(matrix)
        self.line1.isClock = True
        self.line1.animateInitialSlide = False
        self.line1.SetBigClock()
        
        self.line4 = Line(matrix)
        self.line4.isText = False
        self.line4.SetImage("ready.webp")
        self.line4.isImage = True


        self.line2 = Line(matrix)
        self.line2.y = 30
        self.line2.SetFont("frucs6")
        self.line2.color = hex_to_rgb("ffe53c")
        self.line2.text = "<weather data>"

        self.line3 = Line(matrix)
        self.line3.y = self.line2.y
        self.line3.color = hex_to_rgb("ffe53c")
        self.line3.SetFont("frucnorm6")
        self.line3.animateInitialSlide = False

        self.lines.append(self.line1)
        self.lines.append(self.line2)
        self.lines.append(self.line3)
        # self.lines.append(self.line4)



        # self.line1.color = 0x0055aa # nice sky blue
        # # self.line1.color = 0xaaffff # diamond baby blue
        # self.line2.color = 0xff5500 # nice yelllow
        # self.textColor = 0x0055aa

    WEATHER_LAST_UPDATE = -99999999
    WEATHER_DELAY = 30 * 60 
    weatherUpdateCount = 0
    i = 0

    def Display(self, matrix):
        # Perform the default scrolling
        super().Display(matrix)

        # Every 30 minutes needs to update weather 
        now = time.monotonic()   
        if now >= self.WEATHER_LAST_UPDATE + self.WEATHER_DELAY:
            print("it is now time to update the weather from the view")
            self.WEATHER_LAST_UPDATE = now
            try:
                conditions, temperature = data.get_weather(fake = False)
                if self.weatherUpdateCount > 4:
                    self.line2.text = f"{conditions} {temperature} ({self.weatherUpdateCount})"
                else:
                    self.line2.text = f"{conditions}"
                    self.line3.text = f"{temperature}°"

            except Exception as e:
                print("WEATHER FAILED. RIP")
                print(e)
                self.line2.text = f"Err: {e} :("

            self.weatherUpdateCount += 1
        # Now that the display is rendered, we have our lengths set. Make 3 in teh right spot and set 2's max x so that they don't overlap
        self.line3.x = 64 - self.line3.length
        self.line2.max_x = self.line3.x - 2


            
            


class NightClock(View):
    def __init__(self, matrix):
        print("Initializing the view for NightClock")
        super().__init__(matrix)
        self.line1 = Line(matrix)
        self.line1.SetBigClock()
        self.line1.animateInitialSlide = False
        self.line1.color = graphics.Color(255, 0, 0)
        # self.line1.SetFont("6x13")
        self.line1.SetFont("t0-22b-uni.bdf")
        self.lines.append(self.line1)
        matrix.brightness = 50

        # self.line1.color = 0xFF0000
        # self.subtextfont = bitmap_font.load_font("/fonts/frucs6.bdf")

    def Display(self, matrix):
        super().Display(matrix)
        self.line1.x = int(35 - self.line1.length / 2)
        self.line1.y = int(32 - 20 / 2)







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

def scroll(min_x, max_x, pos, len):
    pos -= 1
    if (pos + len < min_x):
        pos = max_x
    return pos

    # line.x = line.x - 1
    # line_width = line.bounding_box[2]
    # if line.x < -line_width:
    #     line.x = 64

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return graphics.Color(int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16))

# Jankiest method of drawing a rectangle. Does a line for each row. Whats the worst that could happen????
# def DrawRectangle(c, x0, y0, x1, y1, height, color):

#     # Draw a horizontal line for each row
#    for y in range(0, height):
#        DrawLine(c, x0, y, x1, y, color)

def DrawRectangle(c, x0, y0, x1, y1, color):
   # Calculate the width of the rectangle
   width = x1 - x0

   # Iterate over each row of the rectangle
   for y in range(y0, y1):
       # Draw a horizontal line for each row
       graphics.DrawLine(c, x0, y, x0 + width, y, color)
