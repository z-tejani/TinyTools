import argparse
import sys
import requests
import re
import os

def strip_tags(html):
    """
    Strips HTML tags using BeautifulSoup if available, otherwise basic regex.
    """
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        # get_text with separator handles things like <br> better
        return soup.get_text(separator=' ', strip=True)
    except ImportError:
        print("Warning: BeautifulSoup4 not found. Using regex fallback (less accurate).")
        # Remove scripts and styles
        clean = re.sub(r'<(script|style).*?>.*?</\1>', '', html, flags=re.DOTALL)
        # Remove tags
        clean = re.sub(r'<.*?>', ' ', clean)
        # Collapse whitespace
        return ' '.join(clean.split())

def process_source(source):
    content = ""
    
    # Check if URL
    if source.startswith("http://") or source.startswith("https://"):
        try:
            print(f"Fetching {source}...")
            response = requests.get(source)
            response.raise_for_status()
            content = response.text
        except Exception as e:
            print(f"Error fetching URL: {e}")
            return
    # Check if file
    elif os.path.exists(source):
        try:
            with open(source, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return
    else:
        # Treat as raw string? No, instructions say URL or HTML file.
        print(f"Error: '{source}' is not a valid file or URL.")
        return

    text = strip_tags(content)
    print("\n--- Extracted Text ---\
")
    print(text)

def main():
    parser = argparse.ArgumentParser(description="Extract plain text from HTML file or URL.")
    parser.add_argument("source", help="URL or path to HTML file")
    
    args = parser.parse_args()
    
    # Check for requests
    try:
        import requests
    except ImportError:
        print("Error: 'requests' library is needed for URL fetching.")
        print("pip install requests")
        if not os.path.exists(args.source): # If it's a file, we might get away without requests, but code structure imports it top level.
             sys.exit(1)

    process_source(args.source)

if __name__ == "__main__":
    main()
