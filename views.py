# import adafruit_display_text.label
# from adafruit_bitmap_font import bitmap_font
# from displayio import Group
import board
import adafruit_ds3231
import time
import api_data as data
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from init import i2c
import os
from PIL import Image
import sys 
import traceback


class Line:
    def __init__(self, matrix):

        self.isText = True
        self.text = ""
        self.isImage = False
        self.image = None
        self.IsProgressBar = False
        self.progress = 0
        self.totalDuration = 0

        self.animateInitialSlide = True
        self.animateLastChange = -1
        self.animateDelay = .1
        self.animateAutoScroll = True

        self.isClock = False
        self.isCentered = False
        self.font = graphics.Font()
        # self.font.LoadFont(os.path.join(os.path.dirname(os.path.realpath(__file__)), "fonts/t0-22-uni.bdf"))
        self.SetFont("pixelmix-b6.bdf")
        

        self.x = 2
        self.y = 10
        self.max_x = 64
        self.min_x = 1

        # self.color = graphics.Color(0, 85, 170) # too dark
        self.color = hex_to_rgb("0099cc")

        self.length = 0
        self.background = True
        self.estimated_height = 7
        self.left_margin = 1

    def SetFont(self, fontName):
        dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "")
        if "fonts/" not in fontName:
            dir += "fonts/"
        dir += fontName
        if ".bdf" not in fontName:
            dir += ".bdf"

        if fontName == "frucnorm6":
            self.estimated_height = 7

        # print(f"loading the font {dir}")
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

        self.SetFont("IMB_EGA_7.bdf")
        self.y = 18


        # self.line1.font = bitmap_font.load_font("/fonts/Px437_DOS-V_re._JPN16-16.bdf")
        # self.lines = 2
        # self.line1.y = 12
        # self.line2.y = 25

        # # Chunkier style
        # self.line1.font = bitmap_font.load_font("/fonts/frucnorm6.bdf")
        # self.line1.scale = 2
        # self.line1.y = 7

    # def SetImage(self, imageDir):
    #     self.imageDir = imageDir
    #     self.isImage = True



class View:
    def __init__(self, matrix):
        self.lines = []
        # subTextColor = 0xff8000
        self.canvas = matrix.CreateFrameCanvas()
        self.shownError = False

    def Display(self, matrix):
        now = time.monotonic()    
        self.canvas.Clear()
        for line in self.lines:
            if line.background == True:
                DrawRectangle(self.canvas, line.x - line.left_margin, line.y - line.estimated_height - 2, line.x + line.length, line.y,  graphics.Color(0, 0, 0))

            if line.isText:
                line.length = graphics.DrawText(self.canvas, line.font, line.x, line.y, line.color, line.text)
                if line.isClock:
                    # if line.length >= 60:
                    #     line.text = GetFriendlyTimeString(hidepm=True)
                    # else:
                    line.text = GetFriendlyTimeString()

            if now >= line.animateLastChange + line.animateDelay and ((line.x != line.min_x and line.animateInitialSlide) or (line.animateAutoScroll and line.length > line.max_x)):
                line.animateLastChange = now
                # pause when it hits left side
                if line.x == 3:
                    line.animateLastChange += 10
                line.x = scroll(line.min_x, line.max_x, line.x, line.length)

            try: 
                if line.isImage:
                    self.canvas.SetImage(line.image, line.x, line.y)
            except Exception as e:
                if not self.shownError:
                    # data.printRed(traceback.format_exc())
                    print("Had an error while trying to render an image.")
                    print("Going to act like nothing happened")
                    print("-" * 40)
                    self.shownError = True


            if line.IsProgressBar and line.totalDuration != 0:
                draw_progress_bar(self.canvas, line.progress, line.totalDuration)


            if line.isCentered:
                line.x = int(32 - line.length / 2)
            
        self.canvas = matrix.SwapOnVSync(self.canvas)
            



class CurrentWeather(View):
    def __init__(self, matrix):
        print("Initializing the view for CurrentWeather")
        super().__init__(matrix)

        self.line1 = Line(matrix)
        self.line1.isClock = True
        self.line1.animateInitialSlide = False
        self.line1.SetBigClock()
        
        self.line2 = Line(matrix)
        self.line2.y = 30
        self.line2.SetFont("tb-8")
        # self.line2.SetFont("frucs6")
        self.line2.color = hex_to_rgb("ffe53c")
        self.line2.text = "<weather data>"
        # Later we set line 2's maximum X and line 3's actual x. We need to do this after the initial render.

        self.line3 = Line(matrix)
        self.line3.y = self.line2.y
        self.line3.color = hex_to_rgb("ffe53c")
        self.line3.SetFont("frucnorm6")
        self.line3.animateInitialSlide = True

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
                conditions, temperature = data.get_weather(fake = "fake" in sys.argv, retry = True)
                if "Partly " in conditions:
                    conditions = conditions.replace('Partly ', '~')
                if "Mostly " in conditions:
                    conditions = conditions.replace('Partly ', '~')
                self.line2.text = f"{conditions}"
                self.line3.text = f"{temperature}°"
                self.line2.color = hex_to_rgb("ffe53c")
                self.line3.color = hex_to_rgb("ffe53c")

            except Exception as e:
                print("WEATHER FAILED. RIP")
                data.printRed(traceback.format_exc())
                data.printRed(e)
                self.line2.color = graphics.Color(255, 20, 20)
                self.line3.color = graphics.Color(255, 20, 20)
                # self.line2.text = f"Err: {e} :("


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


class SpotifyJams(View):
    def __init__(self, matrix):
        print("Initializing the view for SPOTIFY JAMS")
        super().__init__(matrix)
        self.line1 = Line(matrix)
        self.line1.animateInitialSlide = False
        self.line1.isClock = True
        self.line1.color = graphics.Color(154, 154, 154)

        self.line2 = Line(matrix)
        self.line2.text = "<artist name>"
        self.line2.y = 20
        self.line2.SetFont("frucs6")
        self.line2.color = hex_to_rgb("1f9000")
        self.line2.max_x = 64 - 20 - 2

        self.line3 = Line(matrix)
        self.line3.text = "<song name>"
        self.line3.y = 29
        self.line3.SetFont("tb-8")
        self.line3.color = hex_to_rgb("47b800")

        self.line4 = Line(matrix)
        self.line4.isImage = True
        self.line4.x = 64 - 21
        self.line4.y = 0
        self.line4.isText = False
        self.line4.animateInitialSlide = False
        self.line4.left_margin = 3

        self.line5 = Line(matrix)
        self.line5.IsText = False
        self.line5.IsProgressBar = True

        self.lines.append(self.line1)
        self.lines.append(self.line2)
        self.lines.append(self.line3)
        self.lines.append(self.line4)
        self.lines.append(self.line5)
    
    SPOTIFY_LAST_UPDATE = -99999999
    SPOTIFY_DELAY = 15 # seconds
    MILLISECONDS = time.time() * 1000

    def Display(self, matrix):
        now = time.monotonic()   

        # Try to add fake milliseconds even if we don't poll spotify on this tick
        change = time.time() * 1000 - self.MILLISECONDS
        self.line5.progress = self.line5.progress + change
        self.MILLISECONDS = time.time() * 1000

        if now >= self.SPOTIFY_LAST_UPDATE + self.SPOTIFY_DELAY or (self.line5.progress > self.line5.totalDuration and self.line5.totalDuration != 0):
            print("Going to poll spotify from the view!")
            self.SPOTIFY_LAST_UPDATE = now
            try:
                song, artist, image, progress, totalDuration = data.get_current_playing_track(retry = True, fake = len(sys.argv) > 1 and sys.argv[1] == "fake")

                self.line2.text = f"{artist}"
                self.line3.text = f"{song}"
                self.line4.image = image
                self.line5.progress = progress
                self.line5.totalDuration = totalDuration
                if song == "":
                    print("Had spotify return no music, so going to increase the delay to 30 sec")
                    # No music is playing. Increase delay ?
                    self.SPOTIFY_DELAY = 30
                    return False


            except Exception as e:
                print("SPOTIFY FAILED. RIP")
                data.printRed(traceback.format_exc())
                self.line2.text = f"Spotify err :("
                self.line3.text = f"{e}"
                print()
                print("Increasing spotify check delay")
                self.SPOTIFY_DELAY = 30 * 60


        # Now that the display is rendered, we have our lengths set. Make 3 in teh right spot and set 2's max x so that they don't overlap
        # self.line3.x = 64 - self.line3.length
        # self.line2.max_x = self.line3.x - 2
        super().Display(matrix)




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

def clear_rectangle(canvas, x, y, width, height):
    color = graphics.Color(0, 0, 0)  # Black color
    for i in range(x, x + width):
        for j in range(y, y + height):
            canvas.SetPixel(i, j, color.red, color.green, color.blue)


def draw_progress_bar(canvas, progress, total):
    # Calculate the x-coordinate of the progress line
    progress_x = int((progress / total) * 60)

    # Define the colors
    unwatched_color = graphics.Color(64, 64, 64) # Gray
    watched_color = graphics.Color(150, 150, 150) # Light gray

    # Draw the unwatched part of the line
    #                canvas, x1, y1, x2,     y2,  color):
    graphics.DrawLine(canvas, 2, 31, 64 - 4, 31, unwatched_color)
    # Draw the watched part of the line
    if progress_x > 0:
        graphics.DrawLine(canvas, 2, 31, progress_x - 1, 31, watched_color)

   # Update the display
