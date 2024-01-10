import os
import json
import time
import secrets
import spotify_secrets
import requests
import binascii
from PIL import Image
from io import BytesIO
import traceback



ACCUWEATHER_API_KEY_CORE = secrets.ACCUWEATHER_API_KEY_CORE
ACCUWEATHER_LOCATION_KEY = secrets.ACCUWEATHER_LOCATION_KEY
SPOTIFY_CLIENT_ID = secrets.SPOTIFY_CLIENT_ID
SPOTIFY_CLIENT_SECRET = secrets.SPOTIFY_CLIENT_SECRET
SPOTIFY_MANUAL_AUTH_CODE = secrets.SPOTIFY_MANUAL_AUTH_CODE

def get_weather(fake = False, retry = False):
    try:
            
        if fake:
            print("Returning fake weather report")
            return "Blue Skies are here", 75
        print("-" * 40)
        print("Attempting to summon the meteorologists for the weather")
        base_url = f"https://dataservice.accuweather.com/currentconditions/v1/{ACCUWEATHER_LOCATION_KEY}"
        params = {'apikey': ACCUWEATHER_API_KEY_CORE}

        response = requests.get(base_url, params=params)
        response.raise_for_status()

        if response.status_code == 200:
            print("SUCCESS The meteorologists came through for us. Yeahhhhhhhh")
        else:
            print("The meteorologists ARE GONE. ERROR", response.status_code)
            return "Response err:", response.status_code

        data = response.json()[0]  
        weather_text = data['WeatherText']
        temperature = round(data['Temperature']['Imperial']['Value'])

        print(f"It is currently {weather_text}, and {temperature}F")
        return weather_text, temperature
    except Exception as e:
        print("Weather check had an error.")
        
        if retry:
            print("Going to wait 4 seconds and retry the weather again.")
            time.sleep(4)
            return get_weather(retry = False)

        traceback.print_exc()
        printRed(e)
        return "", ""


def GetAlbumArt(url):

    # Going to use the url as the name
    name = url.split('/')[-1]
    file_path = f"img/{name}.jpg"

    # If we already have the file, just use that
    if os.path.isfile(file_path):
        print(f"We already have the file {name}, using that")
        img = Image.open(file_path)
    else:
        # If the file does not exist, download the image
        response = requests.get(url)
        bigimg = Image.open(BytesIO(response.content))

        img = bigimg.resize((21, 21))
        img.save(file_path)

        # Delete all other files in the directory
        for filename in os.listdir('img'):
            if filename != f"{name}.jpg":
                print(f"Deleting old file {filename}")
                os.remove(f"img/{filename}")

    return img


def get_spotify_token():
    print("-" * 40)
    print("Attempting to initially get the spotify token")

    url = "https://accounts.spotify.com/api/token"
    client_creds = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    client_creds_b64 = binascii.b2a_base64(client_creds.encode())[:-1].decode()  # remove the newline character
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic " + client_creds_b64
    }
    data = f"grant_type=authorization_code&code={SPOTIFY_MANUAL_AUTH_CODE}&redirect_uri=https://michaelbalsamo.com"

    # data = "grant_type=client_credentials"
    response = requests.post(url, headers=headers, data=data)
    print("API Response from Spotify Token request is:", response.status_code)

    printYellow(response.content)
    token_info = json.loads(response.content)
    print()

    return token_info


def get_current_playing_track(fake = False, retry = True):
    # print("getting spotify current playing song using this token:")

    # printLightPurple(SPOTIFY_ACCESS_TOKEN)

    SPOTIFY_ACCESS_TOKEN = ReadSpotifyFile("access_token")
    url = "https://api.spotify.com/v1/me/player/currently-playing"
    headers = {"Authorization": f"Bearer {SPOTIFY_ACCESS_TOKEN}"}
    response = requests.get(url, headers=headers)
    # printCyan(headers)
    # print("API Response from Spotify Current Song Request is:", response.status_code)
    if response.status_code == 204:
        print("There is no music playing!")
        return "", "", "", 0, 0, False

    if response.status_code == 401 and retry:
        print("API Spotify Current Song Request recieved 401 error code. Going to try to refresh the access token")
        refresh_spotify_token()
        return get_current_playing_track(retry=False)

    data = response.json()

    song_name = data['item']["name"]
    artist_names = [artist['name'] for artist in data['item']['artists']]
    artist_names_string = ', '.join(artist_names)
    images = data['item']['album']['images']
    albumart = min(images, key=lambda x: x['width'] * x['height'])['url']
    duration_ms = data['item']['duration_ms']
    progress_ms = data['progress_ms']
    is_playing = data.get('is_playing', False)
    print("-" * 40)
    print(f"Song :\033[94m {song_name}\033[00m")
    print(f"Artist Names: \033[94m {artist_names_string}\033[00m")
    # print(f"Smallest Album Art URL: {albumart}")
    # print(f"Duration (ms): {duration_ms}")
    # print(f"Progress (ms): {progress_ms}")
    image = GetAlbumArt(albumart)

    return song_name, artist_names_string, image, progress_ms, duration_ms, is_playing


def refresh_spotify_token():
    print("-" * 40)
    print("Attempting to refresh the spotify token with refresh: ")
    
    SPOTIFY_REFRESH_TOKEN = ReadSpotifyFile("refresh_token")
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
        print("A new refresh token was given in response! ")
    else:
        print("We did not recieve a new refresh token. Saving the old one.")
        output['refresh_token'] = SPOTIFY_REFRESH_TOKEN

    with open('spotify_secrets.py', 'w') as file:
        file.write(json.dumps(output, indent=4))

def ReadSpotifyFile(item):
    with open('spotify_secrets.py', 'r') as file:
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
