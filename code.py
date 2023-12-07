import init
import views
import gc
import api_data as data
import os
import json

print("|/\\" * 30)
print("|\\/" * 30)
init.AttemptAllWifi()

display = init.DoTheInitThings()
OVERRIDE_VIEW = None

# OVERRIDE_VIEW = views.NightClock(display) 
# OVERRIDE_VIEW = views.CurrentWeather(display) 


def SetRelevantView(view):
    if not isinstance(OVERRIDE_VIEW, type(None)):
        return OVERRIDE_VIEW

    # If it is between 10pm-4am, show the night clock 
    t = views.GetCurrentTime()
    # print(f"if ({clock.tm_hour} >= 10 and {pm} == ) or ({clock.tm_hour} <= 4 and {pm} == ")
    if (t.tm_hour > 10 and t.tm_min > 30) or (t.tm_hour < 4):
        if not isinstance(view, views.NightClock):
            return views.NightClock(display) 
        else:
            return view

    # Just default to CurrentWeather if anything else is set
    if not isinstance(view, views.CurrentWeather):
        return views.CurrentWeather(display)
    
    return view

if not isinstance(OVERRIDE_VIEW, type(None)):
    print("Debug override view set to", type(OVERRIDE_VIEW))
    view = SetRelevantView(OVERRIDE_VIEW)
else:
    view = SetRelevantView(views.CurrentWeather(display))


# the manual one
auth_code = ""
# spotify_token = data.get_spotify_token(auth_code)
# spotify_token = ""

# spotify = {
#    'SPOTIFY_ACCESS_TOKEN': spotify_token,
# }

# with open('secrets.py', 'w') as file:
#    file.write(json.dumps(spotify))


# spotify_token = "BQA_LxpfMugVtbddS1__mSyhfOUUsKJKQGv6tY6SBpYjxFdzZzFPDocU6mnqNfDn2n-YygfDPI02go23XFMNH7tRJyepcKBx-O38VSH86tT_UU9tcycxvLjF36YY0DGnYUPOPYTXMCleQmpgj17TmiiGY9WeGi3d8xRsSfvoNiMTn5CjnznF"
# data.get_current_playing_track(spotify_token)
# data.refresh_spotify_token(spotify_token)

# data.DownloadImage("https://i.scdn.co/image/ab67616d00004851e3a9237862f7b78057eb96dc", "music")


while True:
    view = SetRelevantView(view)
    memIssue = view.Display()

    # It's possible we had to delete the display buffer due to the lack of ram onboard 
    if memIssue:
        print(f"Rip, had to nuke the display. mem: {gc.mem_free()}")
        del display
        gc.collect()
        print(f"done. mem: {gc.mem_free()}")
        display = init.DoTheInitThings()

    display.refresh(minimum_frames_per_second=0)









# font = bitmap_font.load_font("/fonts/creep2.bdf"); # a tad smaller, but monospaced, so actually less text
# mainfont = bitmap_font.load_font("/fonts/frucnorm6.bdf"); # REALLY NICE. FAVORITE. 
# subtextfont = bitmap_font.load_font("/fonts/frucs6.bdf"); # small font, all caps, lots of space. Good for subtext





# line1 = adafruit_display_text.label.Label(
#     mainfont,
#     color=0x8000ff,
#         text="{}:{:02}{}".format(formatted.tm_hour, formatted.tm_min, pm))
# line1.x = display.width
# line1.y = 5
# line1.scale = 1

# if line1.scale != 1:
#     line1.y = line1.y + (line1.scale)



# subText = "This is the dot dashboard"
# subTextColor = 0xff8000
# # # if wifiSuccess == False and overwrite != "":
# # #     subText = overwrite
# # #    subTextColor = 0xFF0000

# line2 = adafruit_display_text.label.Label(
#     mainfont,
#     color=subTextColor,
#         text="{} {}°".format(conditions, temp))
# line2.x = display.width
# line2.y = 15

# line3 = adafruit_display_text.label.Label(
#     subtextfont,
#     color=subTextColor,
#     text=subText)
# line3.x = display.width
# line3.y = 25


# Put each line of text into a Group, then show that group.
# g = displayio.Group()
# g.append(line1)
# g.append(line2)
# g.append(line3)
# display.show(g)




# This function will scoot one label a pixel to the left and send it back to
# the far right if it's gone all the way off screen. This goes in a function
# because we'll do exactly the same thing with line1 and line2 below.
# def scroll(line):
#     line.x = line.x - 1
#     line_width = line.bounding_box[2]
#     if line.x < -line_width:
#         line.x = display.width
    
# LAST_CHANGE_LINE1 = -1
# WAIT_DURATION_LINE1 = .125
# LAST_CHANGE_LINE2 = -1
# WAIT_DURATION_LINE2 = .15

# LAST_CHANGE_CLOCKUPDATE = -1
# WAIT_DURATION_CLOCKUPDATE = 60

# clockUpdateCount = 0
# line3Pause = 7




# while True:
#     now = time.monotonic()    
#     if now >= LAST_CHANGE_LINE1 + WAIT_DURATION_LINE1 and line1.x != 1:
#         LAST_CHANGE_LINE1 = now
#         scroll(line1)
#         if line1.scale == 1:
#             scroll(line2)

#         # ease in the speed. As it gets closer, delay a little bit more.
#         if line1.x < 15:
#             WAIT_DURATION_LINE1 += .015

#     if now >= LAST_CHANGE_LINE2 + WAIT_DURATION_LINE2 and line3.x != 1:
#         #if line3.x == 2:
#             #time.sleep(line3Pause)
#             # WAIT_DURATION_LINE_2 = 10 
#         WAIT_DURATION_LINE_2 = .15

#         LAST_CHANGE_LINE2 = now
#         scroll(line3)
        
#     rtc = adafruit_ds3231.DS3231(i2c)
#     formatted, pm = GetCurrentTime()
#     line1.text= "{}:{:02}{}".format(formatted.tm_hour, formatted.tm_min, pm)

#     if now >= LAST_CHANGE_CLOCKUPDATE + WAIT_DURATION_CLOCKUPDATE:
#         LAST_CHANGE_CLOCKUPDATE = now
#         print(now)
#         print("clock update " + "{}:{:02}".format(t.tm_hour, t.tm_min, t.tm_sec))
#         clockUpdateCount += 1
 

#         line3.text="Run time: {} min".format(clockUpdateCount)
#         print(f"Memory status: {gc.mem_free()}")

    
#     display.refresh(minimum_frames_per_second=0)

