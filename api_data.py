import os
import json
import time
import sys
import secrets
import spotify_secrets
import datetime
import requests
import binascii
import random
from init import log, log_error
from PIL import Image
from io import BytesIO
import traceback

ACCUWEATHER_API_KEY_CORE = secrets.ACCUWEATHER_API_KEY_CORE
ACCUWEATHER_LOCATION_KEY = secrets.ACCUWEATHER_LOCATION_KEY
SPOTIFY_CLIENT_ID = secrets.SPOTIFY_CLIENT_ID
SPOTIFY_CLIENT_SECRET = secrets.SPOTIFY_CLIENT_SECRET
SPOTIFY_MANUAL_AUTH_CODE = secrets.SPOTIFY_MANUAL_AUTH_CODE

def get_current_weather(fake = False, retry = False):
    try:
        if fake or "fake" in sys.argv:
            log("Returning fake weather report")
            return "Blue Skies Are Here", 75, get_weather_image("sun")
        log("-" * 40)
        log("Attempting to summon the meteorologists for the weather")
        base_url = f"https://dataservice.accuweather.com/currentconditions/v1/{ACCUWEATHER_LOCATION_KEY}"
        params = {'apikey': ACCUWEATHER_API_KEY_CORE}

        response = requests.get(base_url, params=params)
        response.raise_for_status()

        if response.status_code == 200:
            log("SUCCESS The meteorologists came through for us. Yeahhhhhhhh")
        else:
            log("The meteorologists ARE GONE. ERROR" + response.status_code)
            return "Response err:", response.status_code

        printJSON(response.json())

        data = response.json()[0]  
        printJSON(data)
        weather_text = data['WeatherText']
        temperature = round(data['Temperature']['Imperial']['Value'])

        log(f"It is currently {weather_text}, and {temperature}F")
        return weather_text, temperature, get_weather_image(weather_text)
    except Exception as e:
        log("Weather check had an error.")
        traceback.print_exc()
        
        if retry:
            log("Going to wait 4 seconds and retry the weather again.")
            time.sleep(10)
            return get_current_weather(retry = False)

        printRed(e)
        return "", "", get_weather_image("")

def get_today_weather(fake = False, retry = False):
    try:
        if fake or "fake" in sys.argv:
            print("Returning fake weather report")
            return 75, 50, [50,60,66,68,73,66,60]

        print("-" * 40)
        print("Attempting to summon the meteorologists for the weather")
        base_url = f"https://dataservice.accuweather.com/forecasts/v1/hourly/12hour/{ACCUWEATHER_LOCATION_KEY}"
        params = {'apikey': ACCUWEATHER_API_KEY_CORE}

        response = requests.get(base_url, params=params)
        response.raise_for_status()

        if response.status_code == 200:
            print("SUCCESS The meteorologists came through for us. Yeahhhhhhhh")
        else:
            print("The meteorologists ARE GONE. ERROR", response.status_code)
            return "Response err:", response.status_code

        printJSON(response.json())

        data = response.json()[0]  

        today_high = None
        today_low = float('inf')
        hourly_forecast = []

        for data in response.json():
            # Convert DateTime to a datetime object
            dt = datetime.datetime.fromisoformat(data['DateTime'].replace("Z", "+00:00"))
            
            # Only consider hours between 7am and 7pm
            if 7 <= dt.hour <= 19 or True: 
                temp = data['Temperature']['Value']
                
                # Update today's high and low temperatures
                today_high = max(today_high, temp) if today_high else temp
                today_low = min(today_low, temp)
                
                # Add the hourly forecast to the list
                hourly_forecast.append({
                    'hour': dt.hour,
                    'temperature': temp,
                    'conditions': data['IconPhrase']
                })

        for forecast in hourly_forecast:
            print(f"Hour: {forecast['hour']}")
            print(f"Temperature: {forecast['temperature']}")
            print(f"Conditions: {forecast['conditions']}")

        print(f"Today's high is {today_high}, and the low is {today_low}F")
        return round(today_high), round(today_low), hourly_forecast
    except Exception as e:
        print("Today weather check had an error.")
        
        # if retry:
        #     print("Going to wait 4 seconds and retry the weather again.")
        #     time.sleep(10)
        #     return get_today_weather(retry = False)

        traceback.print_exc()
        printRed(e)
        return "", ""


def get_weather_image(conditions):
    dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "")

    conditions = conditions.lower()
    filename = ""
    if "cloudy" in conditions:
        filename = "cloudy.jpg"
    elif "mostly sunny" in conditions or "partly sunny" in conditions:
        # filename = "sun-clouds-anim.GIF"
        options = ["sun-clouds.PNG", "sun-clouds-alt.PNG"]
        filename = random.choice(options)
    elif "sun" in conditions:
        options = ["sun-alt.PNG", "sun-alt-glasses.PNG", "sun-alt-lighter.PNG", "sun.PNG"]
        filename = random.choice(options)
    elif "storm" in conditions:
        filename = "thunderstorm.PNG"
    elif "heavy rain" in conditions:
        filename = "rain-heavy.PNG"
    elif "rain" in conditions or "showers" in conditions:
        options = ["rain.PNG"]
        filename = random.choice(options)
    elif "clear" in conditions:
        options = ["moon.PNG"]
        filename = random.choice(options)

    if filename == "":
        return ""

    log(f"Getting {filename} weather image for conditions: {conditions}")

    try:
        img = Image.open(f"{dir}assets/weather/{filename}")
        img = img.convert('RGB')
        
    except Exception as e:
        log(f"Failed to open the file '{filename}' for conditions '{conditions}'")
        return ""

    print(img)
    return img


def get_current_date():
    url = "http://worldtimeapi.org/api/timezone/America/Chicago"
    
    try:
        response = requests.get(url)
        response.raise_for_status() 
        data = response.json()
        
        date_iso = data['datetime']
        print(data)
        # Parse the datetime string into a datetime object
        date_part, time_part = date_iso.split("T")
        year, month, day = map(int, date_part.split("-"))
        time_part = time_part.split(".")[0]  # Ignore microseconds
        hour, minute, second = map(int, time_part.split(":"))
        day_of_week = data["day_of_week"]
        
        return {
            'month': month,
            'day': day,
            'year': year,
            'hour': hour,
            'minute': minute,
            'second': second,
            'day_of_week': day_of_week
        }
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching date and time: {e}")
        return None


def get_album_art(url):
    # Going to use the url as the name
    name = url.split('/')[-1]
    dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "")
    file_path = f"assets/albumart/{name}.jpg"
    file_path = dir + file_path
    color = None

    # If we already have the file, just use that
    if os.path.isfile(file_path):
        img = Image.open(file_path)
        color = None
        # color = get_dominant_color(img)
    else:
        try:
            # If the file does not exist, download the image
            response = requests.get(url)
            bigimg = Image.open(BytesIO(response.content))

            color = get_dominant_color(bigimg)

            img = bigimg.resize((21, 21))
            img.save(file_path)

            log("Using image " + file_path)
            print(img)
            # Delete all other files in the directory
            delete_all_albumart(skip=name)

        except Exception as e:
            LOG("HAD SOME PROBLEMS IN GETTING ALBUM ART??")
            print(e)
            return "", None

    return img, color

def delete_all_albumart(skip = ""):
    dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "")
    for filename in os.listdir(f'{dir}assets/albumart'):
        if filename != f"{skip}.jpg":
            print(f"Deleting old file {filename}")
            os.remove(f"{dir}/assets/albumart/{filename}")



def get_spotify_token(fake = False):
    if fake or "fake" in sys.argv:
        log("Returning fake token")
        return "5"
    
    log("-" * 40)
    log("Attempting to initially get the spotify token")

    url = "https://accounts.spotify.com/api/token"
    client_creds = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    client_creds_b64 = binascii.b2a_base64(client_creds.encode())[:-1].decode()  # remove the newline character
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic " + client_creds_b64
    }
    data = f"grant_type=authorization_code&code={SPOTIFY_MANUAL_AUTH_CODE}&redirect_uri=https://michaelbalsamo.com"

    response = requests.post(url, headers=headers, data=data)
    log("API Response from Spotify Token request is:", response.status_code)

    printYellow(response.content)
    token_info = json.loads(response.content)
    log()

    return token_info

def get_current_playing_track(fake = False, retry = True):
    if fake or "fake" in sys.argv:
        print("Returning fake music")
        return "Bippity Boppity aaaaa", "The Boppers Are Here", get_weather_image("sun"), None, 5, 9, False

    SPOTIFY_ACCESS_TOKEN = read_spotify_file("access_token")
    url = "https://api.spotify.com/v1/me/player/currently-playing"
    headers = {"Authorization": f"Bearer {SPOTIFY_ACCESS_TOKEN}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        log("Http Error while in get_current_playing_track(): ")
        log_error(traceback.format_exc())
        log("We probably just need a new token.")

    except requests.exceptions.ConnectionError as errc:
        log_error("Error Connecting while in get_current_playing_track(): ")
        log_error(traceback.format_exc())

    except requests.exceptions.Timeout as errt:
        log_error("Timeout Error while in get_current_playing_track(): ")
        log_error(traceback.format_exc())

    except requests.exceptions.RequestException as err:
        log_error("Something Else while in get_current_playing_track(): ")
        log_error(traceback.format_exc())

    except Exception as e:
        log_error("other error while in get_current_playing_track()??")
        log_error(traceback.format_exc())

    if response is None or response.status_code is None:
        log_error("response is null from checking current playing track in api_data???? i don't know whats happening")

    if response.status_code == 401 and retry:
        log_error("Spotify Current Song Request recieved 401 error code. Going to try to refresh the access token")
        refresh_spotify_token()
        return get_current_playing_track(retry=False)

    if response.status_code == 204:
        log("There is no music playing!")
        return "", "", "", None, 0, 0, False

    if response.status_code == 429:
        log_error("!!!")
        log_error("!!!")
        log_error("We are checking spotify too often. Need to lower the rate checking.")
        log_error("!!!")
        log_error("!!!")
        return "", "", "", None, 0, 0, False

    if response.status_code != 200:
        log_error(f"ERROR WE GOT STATUS CODE {response.status_code} WHEN CHECKING FOR SONG??")

        return "", "", "", None, 0, 0, False


    data = response.json()

    song_name = data['item']["name"]
    artist_names = [artist['name'] for artist in data['item']['artists']]
    artist_names_string = ', '.join(artist_names)
    images = data['item']['album']['images']
    albumart = min(images, key=lambda x: x['width'] * x['height'])['url']
    duration_ms = data['item']['duration_ms']
    progress_ms = data['progress_ms']
    is_playing = data.get('is_playing', False)
    print(f"Song :\033[94m {song_name}\033[00m")
    print(f"Artist Names: \033[94m {artist_names_string}\033[00m")
    print("-" * 40)
    image, color = get_album_art(albumart)

    return song_name, artist_names_string, image, color, progress_ms, duration_ms, is_playing

def refresh_spotify_token():
    if "fake" in sys.argv:
        log("Returning fake refreshed token")
        return ""

    log("-" * 40)
    log("Attempting to refresh the spotify token with refresh: ")
    
    SPOTIFY_REFRESH_TOKEN = read_spotify_file("refresh_token")
    printLightPurple(SPOTIFY_REFRESH_TOKEN)

    url = "https://accounts.spotify.com/api/token"
    client_creds = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    client_creds_b64 = binascii.b2a_base64(client_creds.encode())[:-1].decode()  # remove the newline character
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic " + client_creds_b64
    }
    data = f"grant_type=refresh_token&refresh_token={SPOTIFY_REFRESH_TOKEN}"
    response = requests.post(url, headers=headers, data=data)
    printYellow(response.json())
    output = response.json()
    if response.status_code != 200:
        raise Exception(f"Request failed with status {response.status_code}")

    printGreen("REFRESHED CODE WAS A SUCCESS!!??!? Writing new token to the secrets file")
    if 'refresh_token' in response.json():
        log("A new refresh token was given in response! ")
    else:
        log("We did not recieve a new refresh token. Saving the old one.")
        output['refresh_token'] = SPOTIFY_REFRESH_TOKEN

    with open('spotify_secrets.py', 'w') as file:
        file.write(json.dumps(output, indent=4))
        
# source: https://stackoverflow.com/a/61730849
def get_dominant_color(pil_img, palette_size=16, num_colors=10):
    # Resize image to speed up processing
    img = pil_img.copy()
    img.thumbnail((100, 100))

    # Reduce colors (uses k-means internally)
    paletted = img.convert('P', palette=Image.ADAPTIVE, colors=palette_size)

    # Find the color that occurs most often
    palette = paletted.getpalette()
    color_counts = sorted(paletted.getcolors(), reverse=True)

    dominant_colors = []
    for i in range(num_colors):
      palette_index = color_counts[i][1]
      dominant_colors.append(palette[palette_index*3:palette_index*3+3])

    #  Sort through to find a lighter color
    out = dominant_colors[0]
    i = 1
    print("Dominant colors in this image:")
    print(dominant_colors)
    DARKEST_ALLOWED_COLOR = 80

    while out[0] < DARKEST_ALLOWED_COLOR and out[1] < DARKEST_ALLOWED_COLOR and out[2] < DARKEST_ALLOWED_COLOR and i != num_colors:
        print(f"color {i} was too dark ({out}). Going to next color.")
        out = dominant_colors[i]
        i += 1
    
    # If colors are still too dark, slowly increase until we find a value that's right. Increase all to try to keep same shade?
    while out[0] < DARKEST_ALLOWED_COLOR and out[1] < DARKEST_ALLOWED_COLOR and out[2] < DARKEST_ALLOWED_COLOR:
        print("Colors are still too dark. Increasing by 10")
        out[0] += 10
        out[1] += 10
        out[2] += 10

    print(f"decided on color {out}")

    return out


def read_spotify_file(item):
    dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "")

    with open(f'{dir}spotify_secrets.py', 'r') as file:
        data = json.load(file)
    return data[item]

def get_new_token_if_needed(access_token, refresh_token):
   # Check if the access token is close to expiring
   if is_token_expiring(access_token):
       # If it is, use the refresh token to get a new access token
       new_access_token = refresh_spotify_token(refresh_token)
       return new_access_token
   else:
       # If it's not, just return the current access token
       return access_token

def is_token_expiring(access_token):
   # Get the expiration time of the access token
   expires_in = access_token['expires_in']
   # Calculate the time when the token will expire
   expiry_time = access_token['created_at'] + expires_in
   # Check if the token is close to expiring
   return time.time() > expiry_time - 60 # If it's less than 60 seconds away from expiring

def printJSON(skk): printYellow(skk)
def printYellow(skk):
   try:
        json_data = json.loads(skk)
        print("\033[93m {}\033[00m".format(json.dumps(json_data, indent=4)))

   except Exception as e:
        print("\033[93m {}\033[00m".format(skk))

def printLightPurple(skk): print("\033[94m {}\033[00m" .format(skk))

def printRed(skk): print("\033[91m {}\033[00m" .format(skk))
def printGreen(skk): print("\033[92m {}\033[00m" .format(skk))
def printPurple(skk): print("\033[95m {}\033[00m" .format(skk))
def printCyan(skk): print("\033[96m {}\033[00m" .format(skk))
