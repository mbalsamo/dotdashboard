import sys
sys.path.append('/home/michael/dotdashboard/lib')
import init
import views
import gc
import api_data as data
import os
import json

print("|/\\" * 30)
print("|\\/" * 30)

matrix = init.DoTheInitThings()
OVERRIDE_VIEW = None

# OVERRIDE_VIEW = views.NightClock(display) 
# OVERRIDE_VIEW = views.CurrentWeather(matrix) 


def SetRelevantView(view):
    if not isinstance(OVERRIDE_VIEW, type(None)):
        return OVERRIDE_VIEW

    # If it is between 10:30pm-4am, show the night clock 
    t = views.GetCurrentTime()
    if (t.tm_hour == 22 and t.tm_min > 30) or t.tm_hour > 22 or t.tm_hour < 4:
        if not isinstance(view, views.NightClock):
            return views.NightClock(matrix) 
        else:
            return view

    # Just default to CurrentWeather if anything else is set
    if not isinstance(view, views.CurrentWeather):
        return views.CurrentWeather(matrix)
    
    return view

if not isinstance(OVERRIDE_VIEW, type(None)):
    print("Debug override view set to", type(OVERRIDE_VIEW))
    view = SetRelevantView(OVERRIDE_VIEW)
else:
    view = SetRelevantView(views.CurrentWeather(matrix))


# the manual one
auth_code = ""
# spotify_token = data.get_spotify_token(auth_code)
# spotify_token = ""

# spotify = {
#    'SPOTIFY_ACCESS_TOKEN': spotify_token,
# }

# with open('secrets.py', 'w') as file:
#    file.write(json.dumps(spotify))


# spotify_token = ""
# data.get_current_playing_track(spotify_token)
# data.refresh_spotify_token(spotify_token)

# data.DownloadImage("https://i.scdn.co/image/ab67616d00004851e3a9237862f7b78057eb96dc", "music")

print("About to start main loop")

while True:
    try:
        view = SetRelevantView(view)
        view.Display(matrix)


    except KeyboardInterrupt:
        print("Goodbye.\n")
        sys.exit(0)

# font = bitmap_font.load_font("/fonts/creep2.bdf"); # a tad smaller, but monospaced, so actually less text
# mainfont = bitmap_font.load_font("/fonts/frucnorm6.bdf"); # REALLY NICE. FAVORITE. 
# subtextfont = bitmap_font.load_font("/fonts/frucs6.bdf"); # small font, all caps, lots of space. Good for subtext