import sys
sys.path.append('/home/michael/dotdashboard/lib')
import init
import views
import gc
import api_data as data
import os
import json
import secrets
import traceback
import time

print("|/\\" * 30)
print("|\\/" * 30)

init.Log("\n\n-------------------------------------")
init.Log(f"Initializing new boot! {views.GetCurrentTime().tm_mon} {views.GetCurrentTime().tm_mday} {views.GetCurrentTime().tm_hour}:{views.GetCurrentTime().tm_min}")

matrix = init.DoTheInitThings()
OVERRIDE_VIEW = None

if "NightClock" in sys.argv:
   OVERRIDE_VIEW = views.NightClock(matrix)
elif "TodayWeather" in sys.argv:
   OVERRIDE_VIEW = views.TodayWeather(matrix)
elif "CurrentWeather" in sys.argv:
   OVERRIDE_VIEW = views.CurrentWeather(matrix)
elif "SpotifyJams" in sys.argv:
   OVERRIDE_VIEW = views.SpotifyJams(matrix)
print("Running with custom debug params: ", sys.argv)

now = time.monotonic()
SPOTIFY_LAST_POLL = -99999
SPOTIFY_POLL_DELAY = 30 
init.Log("starting boot. going to check relevant view")

checks = 0
# When this launches on boot, we need to give it time to connect and do its thing
if "on-boot" in sys.argv:
    time.sleep(15)


def SetRelevantView(view):
    if not isinstance(OVERRIDE_VIEW, type(None)):
        return OVERRIDE_VIEW

    global SPOTIFY_LAST_POLL
    global SPOTIFY_POLL_DELAY
    global checks
    now = time.monotonic()
    checks += 1

    # If it is currently spotify, just stick with it. 
    # In the view if we detect music not playing we can change it back...
    if isinstance(view, views.SpotifyJams):
        return view

    if checks % 1000 == 0:
        init.Log(f"Spotify was the last checked at {round(SPOTIFY_LAST_POLL, 1)}. It is currently {round(now, 1)}")

    # Do a poll if spotify should be checked every few minutes 
    if now >= SPOTIFY_LAST_POLL + SPOTIFY_POLL_DELAY:
        init.Log("Checking Spotify NOW!!")
        SPOTIFY_LAST_POLL = time.monotonic()
        try:
            song, artist, image, color, progress, totalDuration, is_playing = data.get_current_playing_track(retry = True, fake = len(sys.argv) > 1 and sys.argv[1] == "fake")
            if song != "" and is_playing:
                init.Log("SPOTIFY is playing music right now, so starting Spotify view")
                return views.SpotifyJams(matrix)
            init.Log("No spotify song playing")
        except Exception as e:
            init.Log("error polling spotify for current playing!")
            init.Log(traceback.format_exc())

            data.printRed(traceback.format_exc())
            if (SPOTIFY_POLL_DELAY < 60*60*24): # max delay 24 hrs 
                SPOTIFY_POLL_DELAY *= 2
            init.Log(f"Increased polling delay to {round(SPOTIFY_POLL_DELAY/60, 1)} min")

            return views.CurrentWeather(matrix)
    elif checks % 1000 == 0:
        init.Log(f"Next Spotify check will be in: {round((SPOTIFY_LAST_POLL + SPOTIFY_POLL_DELAY - now)/60, 1)} min")

    # If it is between 9:30pm-6am, show the night clock 
    t = views.GetCurrentTime()
    if (t.tm_hour == 21 and t.tm_min > 30) or t.tm_hour > 21 or t.tm_hour < 6:
        if not isinstance(view, views.NightClock):
            return views.NightClock(matrix) 
        else:
            return view

    # Show today weather if it is the morning 6am-11am
    if (t.tm_hour >= 6 and t.tm_hour < 11):
        if not isinstance(view, views.TodayWeather):
            return views.TodayWeather(matrix) 
        else:
            return view

    # Just default to CurrentWeather if anything else is set
    if not isinstance(view, views.CurrentWeather):
        print("Nothing is set so we are changing relevant view to CurrentWeather")
        return views.CurrentWeather(matrix)
    
    return view
    

if not isinstance(OVERRIDE_VIEW, type(None)):
    print("Debug override view set to", type(OVERRIDE_VIEW))
    view = SetRelevantView(OVERRIDE_VIEW)
else:
    view = SetRelevantView(views.CurrentWeather(matrix))


while True:
    try:
        

        view = SetRelevantView(view)
        # If the display returns False, then the current view is done. Reset view to default
        success = view.Display(matrix)

        if success == False:
            view = None

    except KeyboardInterrupt:
        print("Goodbye.\n")
        sys.exit(0)

# font = bitmap_font.load_font("/fonts/creep2.bdf"); # a tad smaller, but monospaced, so actually less text
# mainfont = bitmap_font.load_font("/fonts/frucnorm6.bdf"); # REALLY NICE. FAVORITE. 
# subtextfont = bitmap_font.load_font("/fonts/frucs6.bdf"); # small font, all caps, lots of space. Good for subtext