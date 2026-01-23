import argparse
import requests
import sys

def shorten_url(long_url):
    api_url = f"https://tinyurl.com/api-create.php?url={long_url}"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error shortening URL: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Shorten a URL using TinyURL.")
    parser.add_argument("url", help="The long URL to shorten")
    
    args = parser.parse_args()
    
    short_url = shorten_url(args.url)
    
    if short_url:
        print(f"Shortened URL: {short_url}")

if __name__ == "__main__":
    main()
