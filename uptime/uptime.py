import argparse
import requests
import os
import sys

def check_uptime(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return

    try:
        with open(file_path, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    if not urls:
        print("No URLs found in file.")
        return

    print(f"Checking {len(urls)} websites...\n")
    
    down_count = 0

    for url in urls:
        if not url.startswith("http"):
            url = "http://" + url
        
        try:
            response = requests.get(url, timeout=5)
            if 200 <= response.status_code < 400:
                print(f"UP   : {url} ({response.status_code})")
            else:
                print(f"DOWN : {url} (Status: {response.status_code})")
                down_count += 1
        except requests.exceptions.RequestException as e:
            print(f"DOWN : {url} (Error: {e})")
            down_count += 1
            
    print(f"\nCheck complete. {down_count} sites reported down.")

def main():
    parser = argparse.ArgumentParser(description="Check uptime of websites from a file.")
    parser.add_argument("file", nargs="?", default="urls.txt", help="File containing list of URLs (default: urls.txt)")
    
    args = parser.parse_args()
    check_uptime(args.file)

if __name__ == "__main__":
    main()
