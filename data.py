import adafruit_requests as requests
import os
import busio
import board
from digitalio import DigitalInOut, Direction

import adafruit_esp32spi_socket as socket
from adafruit_ds3231 import adafruit_ds3231

ACCUWEATHER_LOCATION_KEY = os.getenv('ACCUWEATHER_API_KEY')
ACCUWEATHER_API_KEY = os.getenv('ACCUWEATHER_LOCATION_KEY')


esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)

esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

socket.set_interface(esp)
requests.set_socket(socket, esp)



# Initialize a requests object with a socket and esp32spi interface

TEXT_URL = "http://wifitest.adafruit.com/testwifi/index.html"
JSON_GET_URL = "https://httpbin.org/get"
JSON_POST_URL = "https://httpbin.org/post"

print("Fetching text from %s" % TEXT_URL)
response = requests.get(TEXT_URL)
print("-" * 40)

print("Text Response: ", response.text)
print("-" * 40)
response.close()

print("Fetching JSON data from %s" % JSON_GET_URL)
response = requests.get(JSON_GET_URL)
print("-" * 40)

print("JSON Response: ", response.json())
print("-" * 40)
response.close()

data = "31F"
print("POSTing data to {0}: {1}".format(JSON_POST_URL, data))
response = requests.post(JSON_POST_URL, data=data)
print("-" * 40)

json_resp = response.json()
# Parse out the 'data' key from json_resp dict.
print("Data received from server:", json_resp["data"])
print("-" * 40)
response.close()

json_data = {"Date": "July 25, 2019"}
print("POSTing data to {0}: {1}".format(JSON_POST_URL, json_data))
response = requests.post(JSON_POST_URL, json=json_data)
print("-" * 40)

json_resp = response.json()
# Parse out the 'json' key from json_resp dict.
print("JSON Data received from server:", json_resp["json"])
print("-" * 40)
response.close()





# def get_weather():
#     base_url = f"https://dataservice.accuweather.com/currentconditions/v1/{ACCUWEATHER_LOCATION_KEY}"
#     query_params = {'apikey': ACCUWEATHER_API_KEY}
#     response = adafruit_requests.get(base_url, params=query_params)
#     if response.status_code == 200:
#         data = response.json()
#         weather_text = data[0]['WeatherText']
#         temperature = data[0]['Temperature']['Imperial']['Value']
#         return weather_text, temperature
#     else:
#         return f'Error: {response.status_code} - {response.text}'
