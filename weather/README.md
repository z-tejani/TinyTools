# Quick Weather CLI

A CLI tool that takes a city or zip code and uses the OpenWeatherMap API to display the current temperature and conditions.

## Requirements

- Python 3
- `requests` (`pip install requests`)
- OpenWeatherMap API Key

## Setup

1. Get a free API key from [OpenWeatherMap](https://openweathermap.org/).
2. Set the environment variable:
   ```bash
   export OPENWEATHER_API_KEY='your_api_key_here'
   ```

## Usage

```bash
python3 weather.py <city_name>
```

Example:
```bash
python3 weather.py London
```
