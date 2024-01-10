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

log = False

date = f"{views.GetCurrentTime().tm_mon}-{views.GetCurrentTime().tm_mday}-{views.GetCurrentTime().tm_year} {views.GetCurrentTime().tm_hour}-{views.GetCurrentTime().tm_min}" 
def Log(text):
    if log:
        with open(f'logs/log {date}.txt', 'a') as file:
            file.write(text + "\n")
Log("\n\n-------------------------------------")
Log(f"Initializing new boot! {views.GetCurrentTime().tm_mon} {views.GetCurrentTime().tm_mday} {views.GetCurrentTime().tm_hour}:{views.GetCurrentTime().tm_min}")

matrix = init.DoTheInitThings()
OVERRIDE_VIEW = None

if "NightClock" in sys.argv:
   OVERRIDE_VIEW = views.NightClock(matrix)
elif "CurrentWeather" in sys.argv:
   OVERRIDE_VIEW = views.CurrentWeather(matrix)
elif "SpotifyJams" in sys.argv:
   OVERRIDE_VIEW = views.SpotifyJams(matrix)

now = time.monotonic()
SPOTIFY_LAST_POLL = -99999999
SPOTIFY_POLL_DELAY = 3 * 60 
Log("starting boot. going to check relevant view")

checks = 0

def SetRelevantView(view):
    if not isinstance(OVERRIDE_VIEW, type(None)):
        return OVERRIDE_VIEW

    global SPOTIFY_LAST_POLL
    global SPOTIFY_POLL_DELAY
    global checks
    checks += 1

    # If it is currently spotify, just stick with it. 
    # In the view if we detect music not playing we can change it back...
    if isinstance(view, views.SpotifyJams):
        if checks < 5:
            Log("ALREADY SPOTIFY SO LEAVING IT")
        return view


    if checks < 5:
        Log("checking view")
        Log(f"{SPOTIFY_LAST_POLL} was the last spotify poll. now is {now}")

    # Do a poll if spotify should be checked every few minutes 
    if now >= SPOTIFY_LAST_POLL + SPOTIFY_POLL_DELAY:
        Log("TRYING TO DO SPOTIFY!!")

        print("Preparing to poll spotify for any playing music")
        SPOTIFY_LAST_POLL = time.monotonic()
        try:
            song, artist, image, progress, totalDuration, is_playing = data.get_current_playing_track(retry = True, fake = len(sys.argv) > 1 and sys.argv[1] == "fake")
            if song != "":
                return views.SpotifyJams(matrix)
        except Exception as e:
            Log("error polling spotify!")
            Log(traceback.format_exc())

            print("Error when polling if spotify is currently playing...")
            data.printRed(traceback.format_exc())
            print("Going to increase polling delay to 20 m")
            SPOTIFY_POLL_DELAY = 20 * 60
            return views.CurrentWeather(matrix)


    # If it is between 10:30pm-4am, show the night clock 
    t = views.GetCurrentTime()
    if (t.tm_hour == 22 and t.tm_min > 30) or t.tm_hour > 22 or t.tm_hour < 4:
        if not isinstance(view, views.NightClock):
            return views.NightClock(matrix) 
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


# the manual one

# try:
#     spotify_token_obj = data.get_spotify_token()
#     access_token = spotify_token_obj['access_token']
#     refresh_token = spotify_token_obj['refresh_token']

#     data.printGreen("Successfully got initial spotify token!")
#     with open('spotify_secrets.py', 'w') as file:
#         file.write(json.dumps(spotify_token_obj))
# except Exception as e:
#     print("Failed to do the initial spotify token retrieval.")
#     data.printRed(e)
#     print()

# data.refresh_spotify_token(spotify_token)


while True:
    try:
        view = SetRelevantView(view)
        # If the display returns False, we reset the view
        good = view.Display(matrix)

        if good == False:
            view = None

    except KeyboardInterrupt:
        print("Goodbye.\n")
        sys.exit(0)

# font = bitmap_font.load_font("/fonts/creep2.bdf"); # a tad smaller, but monospaced, so actually less text
# mainfont = bitmap_font.load_font("/fonts/frucnorm6.bdf"); # REALLY NICE. FAVORITE. 
# subtextfont = bitmap_font.load_font("/fonts/frucs6.bdf"); # small font, all caps, lots of space. Good for subtext