import board
import adafruit_ds3231
import time
import api_data as data
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from init import i2c, log_error
import os
from PIL import Image
import sys 
import traceback

error_count = 0

class Line:
    def __init__(self, matrix):
        matrix.brightness = 100

        self.debugName = ""
        self.isText = True
        self.text = ""
        self.isImage = False
        self.isChart = False
        self.image = None
        self.IsProgressBar = False
        self.progress = 0
        self.totalDuration = 0
        self.is_playing = True

        self.animateInitialSlide = False
        self.animateLastChange = -1
        self.animateDelay = .1
        self.animateAutoScroll = True
        self.state_scrolling = False

        self.isDate = False
        self.isClock = False
        self.isBigClock = False
        self.isCentered = False
        self.font = graphics.Font()
        self.font_name = ""
        # self.font.LoadFont(os.path.join(os.path.dirname(os.path.realpath(__file__)), "/assets/fonts/t0-22-uni.bdf"))
        # self.SetFont("pixelmix-b6.bdf")
        self.SetFont("frucnorm6.bdf")
        

        self.x = 2
        self.y = 10
        self.x_right_aligned = False
        self.max_x = 64
        self.min_x = 2

        # self.color = graphics.Color(0, 85, 170) # too dark
        # self.color = hex_to_rgb("0099cc")
        self.color = graphics.Color(154, 154, 154) # white-ish


        self.length = 0
        self.background = True
        self.estimated_height = 7
        self.left_margin = 1

        self.canvas = None

    def SetFont(self, fontName):
        dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "")
        if "assets/fonts/" not in fontName:
            dir += "assets/fonts/"
        dir += fontName
        if ".bdf" not in fontName:
            dir += ".bdf"

        if "frucnorm6" in fontName:
            self.estimated_height = 9
        if "frucs6" in fontName:
            self.estimated_height = 5


        # print(f"loading the font {dir}")
        self.font = graphics.Font()
        self.font.LoadFont(dir)
        self.font_name = fontName
        # self.mainfont = bitmap_font.load_font("assets/fonts/frucnorm6.bdf")
        # # self.mainfont = bitmap_font.load_font("assets/fonts/Dina_r400-6.bdf") # bit chunky

        # # self.subtextfont = bitmap_font.load_font("assets/fonts/frucs6.bdf")
        # # self.subtextfont = bitmap_font.load_font("assets/fonts/tb-8.bdf") #tad smaller, curvy


    def SetBigClock(self, align = True, small = False):
        print("setting big clock now")
        self.isClock = True
        # self.SetFont("helvR12.bdf")

        self.isBigClock = True
        self.animateAutoScroll = False
        if small:
            print("thats a really small clock")
            self.SetFont("frucnorm6.bdf")
        else:
            self.SetFont("IMB_EGA_7.bdf")

        if align:
            self.isCentered = True
            self.y = 12


        # self.line1.font = bitmap_font.load_font("assets/fonts/Px437_DOS-V_re._JPN16-16.bdf")
        # self.lines = 2
        # self.line1.y = 12
        # self.line2.y = 25

        # # Chunkier style
        # self.line1.font = bitmap_font.load_font("assets/fonts/frucnorm6.bdf")
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
    
    loggedcount = 0
    global_animation_start = time.monotonic()
    was_scrolling = False

    def Display(self, matrix):
        now = time.monotonic()    
        self.canvas.Clear()            
        self.loggedcount += 1

        # janky attempt to pause auto scrolling unless everything is at the starting position
        no_lines_scrolling = all((temp.x == temp.min_x or not temp.isText or temp.isClock or temp.isImage or temp.IsProgressBar) for temp in self.lines)
        
        # If we stopped scrolling now, then change the global wait time
        if self.was_scrolling and no_lines_scrolling:
            data.printYellow("We were scrolling, just stopped. Adding 10 tick timer")
            self.global_animation_start = now + 10

        self.was_scrolling = not no_lines_scrolling
        
        # if self.loggedcount % 70 == 0:
        #     if (not no_lines_scrolling):
        #         data.printRed("someone is scrolling cus ")
        #         for l in self.lines:
        #             print(f"{l.debugName}\n x= {l.x} but min_x= {l.min_x}")
        #         print()
        #     else:
        #         data.printRed("NOBODY IS SCROLLING??")

        for line in self.lines:
            if line.background == True:
                y_bottom = line.y - line.estimated_height - 2
                if y_bottom < 0:
                    # Image y is always on top left, despite text being 
                    y_bottom = -y_bottom

                draw_rectangle(self.canvas, line.x - line.left_margin, y_bottom, line.x + line.length, line.y + 1,  graphics.Color(0, 0, 0))

            if line.isText:
                if line.isClock:
                    line.text = get_friendly_time_string(hidepm=False)
                    if len(line.text) > 6 and line.isBigClock and "t0-22b-uni" in line.font_name:
                        line.text = get_friendly_time_string(hidepm=True)
                if line.isDate:
                    line.text = get_friendly_date_string()

                line.length = graphics.DrawText(self.canvas, line.font, line.x, line.y, line.color, line.text)

            # if self.loggedcount % 20 == 0:
            #     print(f"{line.animateLastChange} was last change, delay is {line.animateDelay}, ")
            # if (line.debugName == "Artist" or line.debugName == "Song") and self.loggedcount % 100 == 0:
            #     data.printCyan("Looking at " + line.debugName)
            #     print(f"now: {now}")
            #     print(f"last change: {line.animateLastChange}")
            #     print(f"animateDelay: {line.animateDelay}")
            #     print(f"time to next: {line.animateLastChange + line.animateDelay - now}")
            #     print(f"global_animation_start: {self.global_animation_start}")
            #     print(f"state_scrolling: {line.state_scrolling}")

            if (now >= line.animateLastChange + line.animateDelay and ((no_lines_scrolling and now >= self.global_animation_start) or line.state_scrolling)) and ((line.x != line.min_x and line.animateInitialSlide) or (line.animateAutoScroll and line.length > line.max_x)):
                if self.loggedcount % 100 == 0:
                    data.printCyan("scrolling " + line.debugName)
                line.state_scrolling = True
                line.animateLastChange = now
                
                line.x = scroll(line.min_x, line.max_x, line.x, line.length)
                # pause when it hits left side
                if line.x == line.min_x:
                    data.printCyan("just stopped scrolling " + line.debugName)
                    line.state_scrolling = False

            try: 
                if line.isImage:
                    self.canvas.SetImage(line.image, line.x, line.y)
            except Exception as e:
                
                if not self.shownError:
                    print("Had an error while trying to render an image.")
                    record_error()
                    log_error(traceback.format_exc())
                    print("Going to act like nothing happened")
                    print("-" * 40)
                    self.shownError = True


            if line.IsProgressBar and line.totalDuration != 0:
                draw_progress_bar(self.canvas, line.progress, line.totalDuration)

            if line.isCentered:
                line.x = int(32 - line.length / 2)

            if line.x_right_aligned:
                line.x = 64 - line.length

            if line.isChart:
                # currently does not abide by y coordinate 
                draw_chart(self.canvas, line.hourly_forecast, line.high, line.low, line.x, line.max_x, 15, 30, line.color)


        # draw the error dot
        if (error_count > 0):
                #            canvas, x1, y1, x2,     y2,  color):
            graphics.DrawLine(self.canvas, 64, 32, 644, 32, hex_to_rgb("B0413E"))
            
        self.canvas = matrix.SwapOnVSync(self.canvas)
        return self.canvas



class CurrentWeather(View):
    def __init__(self, matrix):
        print("Initializing the view for CurrentWeather")
        super().__init__(matrix)

        self.line1 = Line(matrix)
        self.line1.isClock = True
        self.line1.animateInitialSlide = False
        self.line1.SetBigClock(align=False)
        
        self.line2 = Line(matrix)
        self.line2.y = 30
        #self.line2.SetFont("frucs6") #  normal size
        self.line2.SetFont("tb-8") # 
        self.line2.color = hex_to_rgb("ffe53c")
        self.line2.text = "<conditions>"

        # Later we set line 2's maximum X and line 3's actual x. We need to do this after the initial render.

        self.line3 = Line(matrix)
        self.line3.y = self.line2.y
        self.line3.color = hex_to_rgb("ffe53c")
        self.line3.SetFont("frucnorm6")
        self.line3.animateInitialSlide = True
        self.line3.x_right_aligned = True

        self.line4 = Line(matrix)
        self.line4.y = 20
        # self.line4.SetFont("frucs6") # norm
        self.line4.SetFont("tb-8") # 
        self.line4.isDate = True
        # self.line4.color = hex_to_rgb("ffe53c")
        self.line4.text = "<Date>"


        IMG_HEIGHT = 11
        self.line5 = Line(matrix)
        self.line5.isImage = True
        self.line5.x = 64 - IMG_HEIGHT - 1
        self.line5.y = 1
        self.line5.isText = False
        self.line5.animateInitialSlide = False
        self.line5.left_margin = 3
        self.line5.estimated_height = -IMG_HEIGHT


        self.lines.append(self.line1)
        self.lines.append(self.line2)
        self.lines.append(self.line3)
        self.lines.append(self.line4)
        self.lines.append(self.line5)

        # self.line1.color = 0x0055aa # nice sky blue
        # # self.line1.color = 0xaaffff # diamond baby blue
        # self.line2.color = 0xff5500 # nice yelllow
        # self.textColor = 0x0055aa

    WEATHER_LAST_UPDATE = -99999999
    WEATHER_DELAY = 45 * 60 
    weatherUpdateCount = 0
    i = 0

    def Display(self, matrix):
        # Perform the default scrolling
        super().Display(matrix)

        # Every 30 minutes needs to update weather 
        now = time.monotonic()   
        if now >= self.WEATHER_LAST_UPDATE + self.WEATHER_DELAY and self.line2.x == 2: # When conditions x == 2, that's so that it doesn't swap while it's halfway through a scroll
            print("it is now time to update the weather from the view")
            self.WEATHER_LAST_UPDATE = now
            try:
                conditions, temperature, img = data.get_current_weather(retry = True)
                self.line2.text = f"{conditions}"
                self.line2.x = 2
                self.line3.text = f"{temperature}°"
                self.line5.image = img

                conditions = conditions.lower()
                if "cloudy" in conditions:
                    self.line2.color = hex_to_rgb("717171")
                    self.line3.color = hex_to_rgb("858585") #grey 
                elif "mostly sunny" in conditions or "partly sunny" in conditions:
                    self.line2.color = hex_to_rgb("ffe53c") #yellow 
                    self.line3.color = hex_to_rgb("ffe53c")
                elif "sunny" in conditions:
                    self.line2.color = hex_to_rgb("ffe53c") #yellow 
                    self.line3.color = hex_to_rgb("ffe53c")
                elif "thunderstorm" in conditions:
                    self.line2.color = hex_to_rgb("#4E92A6") # dark blue
                    self.line3.color = hex_to_rgb("#417A8B")
                elif "heavy rain" in conditions:
                    self.line2.color = hex_to_rgb("5d9fb3") #blue 
                    self.line3.color = hex_to_rgb("#4E92A6")
                elif "rain" in conditions:
                    self.line2.color = hex_to_rgb("5d9fb3") #blue 
                    self.line3.color = hex_to_rgb("#4E92A6")
                else:
                    print("Conditions didn't have specific color mapping: '" + conditions + "'")
                    color = data.get_dominant_color(img, num_colors = 2)
                    self.line2.color = graphics.Color(color[0], color[1], color[2])
                    self.line3.color = graphics.Color(min(color[0]+10, 250), min(color[1]+10, 250), min(color[2]+10, 250))

                # self.line2.max_x = self.line3.x

            except Exception as e:
                print("WEATHER FAILED. RIP")
                data.printRed(traceback.format_exc())
                data.printRed(e)
                self.line2.color = graphics.Color(100, 20, 20)
                self.line3.color = graphics.Color(100, 20, 20)
                self.line2.text = f"{e}"
                self.line3.text = ""
                # self.line2.text = f"Err: {e} :("

            self.weatherUpdateCount += 1
        # Now that the display is rendered, we have our lengths set. Make 3 in the right spot and set 2's max x so that they don't overlap
        # self.line3.x = 64 - self.line3.length
        self.line2.max_x = self.line3.x - 2


class TodayWeather(View):
    def __init__(self, matrix):
        print("Initializing the view for TodayWeather")
        super().__init__(matrix)

        self.line_clock = Line(matrix)
        self.line_clock.isClock = True
        self.line_clock.animateInitialSlide = False
        self.line_clock.SetBigClock(align=False)
        self.lines.append(self.line_clock)
        
        self.line_temp_high = Line(matrix)
        self.line_temp_high.y = 22
        self.line_temp_high.background = False
        self.line_temp_high.SetFont("tb-8")
        self.line_temp_high.color = graphics.Color(176, 65, 62) # Red for HIGH
        self.line_temp_high.text = "50^"
        self.lines.append(self.line_temp_high)

        self.line_temp_low = Line(matrix)
        self.line_temp_low.y = 30
        self.line_temp_low.background = False
        self.line_temp_low.SetFont("tb-8")
        self.line_temp_low.color = hex_to_rgb("0055aa") # Baby blue for LOW
        self.line_temp_low.text = "40`"
        self.lines.append(self.line_temp_low)

        self.line_chart = Line(matrix)
        self.line_chart.y = 40
        self.line_chart.x = 20
        self.line_chart.color = graphics.Color(150, 150, 150)
        self.line_chart.isText = False
        self.line_chart.isChart = True
        self.line_chart.high = 0
        self.line_chart.low = 0
        self.line_chart.hourly_forecast = []
        self.line_chart.background = False
        self.lines.append(self.line_chart)

        # IMG_HEIGHT = 11
        # self.line_img = Line(matrix)
        # self.line_img.isImage = True
        # self.line_img.y = 1
        # self.line_img.isText = False
        # self.line_img.animateInitialSlide = False
        # self.line_img.left_margin = 3
        # self.line_img.estimated_height = -IMG_HEIGHT
        # self.line_img.x_right_aligned = True
        # self.lines.append(self.line_img)

        # self.line1.color = 0x0055aa # nice sky blue
        # # self.line1.color = 0xaaffff # diamond baby blue
        # self.line2.color = 0xff5500 # nice yelllow
        # self.textColor = 0x0055aa

    WEATHER_LAST_UPDATE = -99999999
    WEATHER_DELAY = 60 * 60 
    weatherUpdateCount = 0
    i = 0

    def Display(self, matrix):
        # Perform the default scrolling
        canvas = super().Display(matrix)

        now = time.monotonic()   
        if now >= self.WEATHER_LAST_UPDATE + self.WEATHER_DELAY:
            print("it is now time to update TODAY's weather from the view")
            self.WEATHER_LAST_UPDATE = now
                
            high, low, hourly_forecast = data.get_today_weather(retry = True)
            data.printCyan(f"Retrieved weather: high {high}, low {low}, hourly {hourly_forecast}")
            self.line_chart.hourly_forecast = hourly_forecast
            self.line_chart.high = high
            self.line_chart.low = low
            self.line_temp_high.text = f"{high}^"
            self.line_temp_low.text = f"{low}`"
            self.canvas = matrix.SwapOnVSync(self.canvas)

            # self.line_chart.x = self.line_temp_high.x + self.line_temp_high.length + 2
            self.line_chart.x = 18
            self.line_chart.max_x = 64-2


            self.weatherUpdateCount += 1
        # draw_chart(canvas, self.hourly_forecast, self.high, self.low, 30, 60, 15, 30, hex_to_rgb("ffe53c"))
        # Now that the display is rendered, we have our lengths set. Make 3 in teh right spot and set 2's max x so that they don't overlap
        # self.line2.max_x = self.line3.x - 2


class NightClock(View):
    def __init__(self, matrix):
        print("Initializing the view for NightClock")
        super().__init__(matrix)
        self.line1 = Line(matrix)
        self.line1.SetBigClock()
        self.line1.animateInitialSlide = False
        self.line1.color = graphics.Color(255, 0, 0)
        # self.line1.SetFont("6x13")
        # self.line1.SetFont("t0-22b-uni.bdf") # huge
        self.lines.append(self.line1)
        matrix.brightness = 10

        # self.line1.color = 0xFF0000
        # self.subtextfont = bitmap_font.load_font("/assets/fonts/frucs6.bdf")

    def Display(self, matrix):
        super().Display(matrix)
        # self.line1.x = int(35 - self.line1.length / 2)
        self.line1.y = int(32 - self.line1.estimated_height -5)


class SpotifyJams(View):
    def __init__(self, matrix):
        print("Initializing the view for SPOTIFY JAMS")
        super().__init__(matrix)
        self.line1 = Line(matrix)
        self.line1.debugName = "Clock"
        self.line1.animateInitialSlide = False
        self.line1.isClock = True
        self.line1.color = graphics.Color(154, 154, 154)
        self.line1.background = False

        self.line2 = Line(matrix)
        self.line2.debugName = "Artist"
        self.line2.text = "<artist name>"
        self.line2.y = 20
        self.line2.SetFont("frucs6")
        self.line2.color = graphics.Color(184, 188, 184)
        self.line2.max_x = 64 - 20 - 2

        self.line3 = Line(matrix)
        self.line3.debugName = "Song"
        self.line3.text = "<song name>"
        self.line3.y = 29
        self.line3.SetFont("tb-8")
        self.line3.color = graphics.Color(184, 184, 184)

        IMG_HEIGHT = 21
        self.line4 = Line(matrix)
        self.line4.debugName = "Album Art"
        self.line4.isImage = True
        self.line4.x = 64 - IMG_HEIGHT
        self.line4.y = 0
        self.line4.isText = False
        self.line4.animateInitialSlide = False
        self.line4.left_margin = 3
        self.line4.estimated_height = -IMG_HEIGHT

        self.line5 = Line(matrix)
        self.line5.debugName = "Progress Bar"
        self.line5.IsText = False
        self.line5.IsProgressBar = True
        self.line5.background = False

        self.lines.append(self.line1)
        self.lines.append(self.line2)
        self.lines.append(self.line3)
        self.lines.append(self.line4)
        self.lines.append(self.line5)

    data.delete_all_albumart()
    SPOTIFY_LAST_UPDATE = -99999999
    SPOTIFY_DELAY = 12 # seconds
    MILLISECONDS = time.time() * 1000

    IS_PLAYING = False
    TIME_PAUSED = 9999999999999999999

    def Display(self, matrix):
        now = time.monotonic()   

        # Try to add fake milliseconds even if we don't poll spotify on this tick
        if self.IS_PLAYING:
            change = time.time() * 1000 - self.MILLISECONDS
            self.line5.progress = self.line5.progress + change
            self.MILLISECONDS = time.time() * 1000
        elif now - self.TIME_PAUSED > 45:
            # if it has been paused for over 60 seconds, go back to clock
            return False
            ################################### there's a good chance this may have broken something here after the 60 second check
        # print(f"now {now} - TIME_PAUSED {TIME_PAUSED}")

        # If ready for next check, and the lines are not moving (to prevent stutter), or if the song ended, then check if anything changed.
        if (now >= self.SPOTIFY_LAST_UPDATE + self.SPOTIFY_DELAY) or (self.line5.progress > self.line5.totalDuration and self.line5.totalDuration != 0):
            self.SPOTIFY_LAST_UPDATE = now
            try:
                print("Checking for spotify song changes")
                song, artist, image, color, progress, totalDuration, is_playing = data.get_current_playing_track(retry = True, fake = len(sys.argv) > 1 and sys.argv[1] == "fake")

                # If the song changed, then reset the spot 
                if self.line3.text != f"{song}":
                    self.line2.x = self.line2.min_x #UGH this is jank. Adding 1 because we expect it to scroll once.
                    self.line3.x = self.line3.min_x 
                    self.MILLISECONDS = time.time() * 1000
                if self.IS_PLAYING == True and is_playing == False: # If it was playing, but now it is not playing, then record time
                    self.TIME_PAUSED = now
                elif is_playing == True: # Now it has been set to playing again, so wipe the pause time.
                    self.TIME_PAUSED = 9999999999999999

                self.IS_PLAYING = is_playing
                self.line2.text = f"{artist}"
                self.line3.text = f"{song}"
                self.line4.image = image
                self.line5.progress = progress
                self.line5.totalDuration = totalDuration
                
                if (color is not None):
                    self.line2.color = graphics.Color(color[0], color[1], color[2])
                    self.line3.color = graphics.Color(min(color[0]+10, 250), min(color[1]+10, 250), min(color[2]+10, 250))
                    print("setting line colors to ", color[0], color[1], color[2])
                else:
                    print("We are not updating album colors")

                if song == "":
                    print("Had spotify return no music")
                    # No music is playing. Return false so it'll go back to the currentweather view
                    return False

            except Exception as e:
                print("SPOTIFY FAILED. RIP")
                data.printRed(traceback.format_exc())
                self.line2.text = f"Spotify err :("
                self.line3.text = f"{e}"
                print()
                print("Increasing spotify check delay")
                self.SPOTIFY_DELAY = 30
                log_error([
                    get_mean_datetime_string() + " - Spotify error from view",
                    f"{traceback.format_exc()}"
                ])

        # Now that the display is rendered, we have our lengths set. Make 3 in teh right spot and set 2's max x so that they don't overlap
        # self.line3.x = 64 - self.line3.length
        # self.line2.max_x = self.line3.x - 2
        super().Display(matrix)

def GetCurrentTime(): 
    rtc = adafruit_ds3231.DS3231(i2c)
    t = rtc.datetime
    return t

def get_friendly_time_string(hidepm = False):
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
        return "{}:{:02d}".format(hours, minutes)
    return "{}:{:02d}{}".format(hours, minutes, am_pm)

    
def get_friendly_date_string(hideyear = True):
    t = GetCurrentTime()
    month_name = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    day_suffixes = ["st", "nd", "rd", "th"]
    days_of_week = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    
    month = t.tm_mon
    day = t.tm_mday
    year = t.tm_year
    weekday = days_of_week[t.tm_wday]

    if day < 4:
        ordinal_suffix = day_suffixes[day - 1] 
    else:
        ordinal_suffix = "th"

    if hideyear:
        year = ""
    return "{}, {} {}{} {}".format(weekday, month_name[month - 1], day, ordinal_suffix, year)

def get_mean_datetime_string():
    t = GetCurrentTime()
    
    return "{}/{}/{} {}".format(t.tm_mday, t.tm_mon, t.tm_year, get_friendly_time_string())

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
def draw_rectangle(c, x0, y0, x1, y1, color):
   for y in range(y0, y1):
       # Draw a horizontal line for each row
       graphics.DrawLine(c, x0, y, x1, y, color)


def draw_progress_bar(canvas, progress, total):
    # Calculate the x of the progress line
    progress_x = int((progress / total) * 60)
    unwatched_color = graphics.Color(64, 64, 64) # Gray
    watched_color = graphics.Color(150, 150, 150) # Light gray

    # Draw the unwatched part of the line
    #                canvas, x1, y1, x2,     y2,  color):
    graphics.DrawLine(canvas, 2, 31, 64 - 4, 31, unwatched_color)
    # Draw the watched part of the line
    if progress_x > 0:
        graphics.DrawLine(canvas, 2, 31, progress_x - 1, 31, watched_color)


def draw_chart(canvas, hourly_forecast, today_high, today_low, left_x_boundary, max_x_boundary, min_y_boundary, max_y_boundary, color):
    try:
        # Normalize the hourly forecast data to fit within the given boundaries
        normalized_forecast = []
        height = max_y_boundary - min_y_boundary
        for i, forecast in enumerate(hourly_forecast):
            # Map the hour to the x-coordinate
            x = left_x_boundary + ((max_x_boundary - left_x_boundary) * i / len(hourly_forecast))
            
            # Map the temperature to the y-coordinate
            y = min_y_boundary + ((max_y_boundary - min_y_boundary) * (forecast['temperature'] - today_low) / (today_high - today_low))
            
            normalized_forecast.append((x, -y+32+(height/2), forecast['hour']))
        
        if (len(normalized_forecast) < 2):
            data.printRed(f"We only had {len(normalized_forecast)} values in the normalized forecast for today?")
            data.printRed(f"hourly_forecast: {hourly_forecast}")
            data.printRed(f"today_high: {today_high}")
            data.printRed(f"today_low: {today_low}")
            data.printRed(f"")
            return

        # Draw a line connecting the normalized forecast data
        prev_x, prev_y, prev_hr = normalized_forecast[0]
        for x, y, hr in normalized_forecast[1:]:
            # print(f"chart {hr}: {prev_x}, {prev_y}, {x}, {y}")
            if hr == 12:
                graphics.DrawLine(canvas, prev_x, prev_y, x, y, hex_to_rgb("ffe53c"))
            else:
                graphics.DrawLine(canvas, prev_x, prev_y, x, y, color)
            prev_x, prev_y = x, y

    except Exception as e:
        record_error()
        log_error("Drawing the chart did not go as planned.")
        log_error(traceback.format_exc())
        data.printRed(e)

def record_error(count = 1):
    global error_count
    error_count += count