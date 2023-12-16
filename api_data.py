import os
import json
import time
import secrets
import requests

ACCUWEATHER_API_KEY_CORE = secrets.ACCUWEATHER_API_KEY_CORE
ACCUWEATHER_LOCATION_KEY = secrets.ACCUWEATHER_LOCATION_KEY
SPOTIFY_CLIENT_ID = secrets.SPOTIFY_CLIENT_ID
SPOTIFY_CLIENT_SECRET = secrets.SPOTIFY_CLIENT_SECRET
spotify_token = secrets.SPOTIFY_ACCESS_TOKEN

def get_weather(fake = False):
    try:
            
        if fake:
            print("Returning fake weather report")
            return "Blue Skies are here", 75
        print("-" * 40)
        print("Attempting to summon the meteorologists for the weather")
        print("api key", ACCUWEATHER_API_KEY_CORE)
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
        print(e)
        return "Err :("




# def DownloadImage(img_url, album_name):
#    print("Preparing to download the image for", album_name)
#    img_path_png = f"img/{album_name}.png"
#    response = requests.get(img_url, stream=True)

#    with open(img_path_png, 'wb') as file:
#        for chunk in response.iter_content(chunk_size=1024):
#            file.write(chunk)

#    # Load the source image
#    source_bitmap, _ = adafruit_imageload.load(img_path_png,
#                                             bitmap=displayio.Bitmap,
#                                             palette=displayio.Palette)

#    # Create a destination bitmap with the desired size
#    dest_bitmap = displayio.Bitmap(32, 32, 1)

#    # Copy the source image to the destination bitmap with scaling
#    bitmaptools.blit(dest_bitmap, source_bitmap, 0, 0, 0, 0, 32, 32, 128, 128)



def get_spotify_token(auth_code):
    print("-" * 40)
    print("Attempting to initially get the spotify token")

    url = "https://accounts.spotify.com/api/token"
    client_creds = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    client_creds_b64 = binascii.b2a_base64(client_creds.encode())[:-1].decode()  # remove the newline character
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic " + client_creds_b64
    }
    data = f"grant_type=authorization_code&code={auth_code}&redirect_uri=https://michaelbalsamo.com"

    # data = "grant_type=client_credentials"
    response = requests.post(url, headers=headers, data=data)
    print("API Response from Spotify Token request is:", response.status_code)
    print(response.content)

    token_info = json.loads(response.content)
    print(token_info)
    print("we got", token_info['access_token'])

    print("going to write to a new environment variable as ", token_info['access_token'])
    os.environ['SPOTIFY_ACCESS_TOKEN'] = token_info['access_token']

    return token_info['access_token']


def get_current_playing_track(access_token, retry = True):
    print("-" * 40)
    print("getting spotify current playing song")

    url = "https://api.spotify.com/v1/me/player/currently-playing"
    headers = {"Authorization": f"Bearer {access_token}"}
    # headers = f"Authorization: Bearer {access_token}"
    response = requests.get(url, headers=headers)

    print("API Response from Spotify Current Song Request is:", response.status_code)
    print(response.json())

    if response.status_code == 401 and retry:
        print("API Spotify Current Song Request recieved 401 error code. Going to try to refresh the access token")
        new_token = refresh_spotify_token(access_token)
        return get_current_playing_track(new_token, retry=False)

    data = response.json()

    artist_names = [artist['name'] for artist in data['item']['artists']]
    artist_names_string = ', '.join(artist_names)
    images = data['item']['album']['images']
    albumart = min(images, key=lambda x: x['width'] * x['height'])['url']
    duration_ms = data['item']['duration_ms']
    progress_ms = data['progress_ms']

    print(f"Artist Names: {artist_names_string}")
    print(f"Smallest Album Art URL: {albumart}")
    print(f"Duration (ms): {duration_ms}")
    print(f"Progress (ms): {progress_ms}")
    song_name = data['item']["name"]
    DownloadImage(albumart, song_name)

    artist_name = data["artists"][0]["name"]
    return song_name, artist_name


def refresh_spotify_token(refresh_token):
    print("-" * 40)
    print("Attempting to refresh the spotify token.")
    url = "https://accounts.spotify.com/api/token"
    client_creds = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    client_creds_b64 = binascii.b2a_base64(client_creds.encode())[:-1].decode()  # remove the newline character
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic " + client_creds_b64
    }
    data = f"grant_type=refresh_token&refresh_token={refresh_token}"
    response = requests.post(url, headers=headers, data=data)
    print(response.json())
    if response.status_code != 200:
        raise Exception(f"Request failed with status {response.status_code}")
    token_info = json.loads(response.content)
    return token_info['access_token']





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
