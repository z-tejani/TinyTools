import argparse
import requests
import sys

def define_word(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    
    try:
        response = requests.get(url)
        if response.status_code == 404:
            print(f"Word '{word}' not found.")
            return
        response.raise_for_status()
        
        data = response.json()
        
        # Parse and display
        for entry in data:
            print(f"\nWord: {entry.get('word', word)}")
            if 'phonetic' in entry:
                print(f"Phonetic: {entry['phonetic']}")
            
            for meaning in entry.get('meanings', []):
                print(f"\nPart of Speech: {meaning.get('partOfSpeech', 'unknown')}")
                for idx, definition in enumerate(meaning.get('definitions', []), 1):
                    print(f"  {idx}. {definition.get('definition')}")
                    if 'example' in definition:
                        print(f"     Example: \"{definition['example']}\"")
                        
    except Exception as e:
        print(f"Error fetching definition: {e}")

def main():
    parser = argparse.ArgumentParser(description="Get the definition of a word.")
    parser.add_argument("word", help="The word to define")
    
    args = parser.parse_args()
    define_word(args.word)

if __name__ == "__main__":
    main()

