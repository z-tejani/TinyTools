import argparse
import requests
import os
import sys

def get_weather(query, api_key):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': query,
        'appid': api_key,
        'units': 'metric' # Default to metric, could add flag
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        city = data['name']
        temp = data['main']['temp']
        desc = data['weather'][0]['description']
        humidity = data['main']['humidity']
        wind = data['wind']['speed']
        
        print(f"Weather in {city}:")
        print(f"  Temperature: {temp}°C")
        print(f"  Condition:   {desc.capitalize()}")
        print(f"  Humidity:    {humidity}%")
        print(f"  Wind Speed:  {wind} m/s")
        
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            print("Error: City not found.")
        elif response.status_code == 401:
            print("Error: Invalid API Key.")
        else:
            print(f"HTTP Error: {e}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Get current weather for a city.")
    parser.add_argument("city", nargs="+", help="City name or Zip code")
    
    args = parser.parse_args()
    query = " ".join(args.city)
    
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        print("Error: OPENWEATHER_API_KEY environment variable not set.")
        print("Please get an API key from https://openweathermap.org/ and set it.")
        print("export OPENWEATHER_API_KEY='your_key'")
        sys.exit(1)
        
    get_weather(query, api_key)

if __name__ == "__main__":
    main()
