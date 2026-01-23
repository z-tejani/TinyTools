import json
import csv
import argparse
import sys
import os

def csv_to_json(csv_file, json_file=None):
    data = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    if not json_file:
        json_file = os.path.splitext(csv_file)[0] + '.json'

    try:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"Converted '{csv_file}' to '{json_file}'")
    except Exception as e:
        print(f"Error writing JSON file: {e}")

def main():
    parser = argparse.ArgumentParser(description="Convert a CSV file to a JSON file.")
    parser.add_argument("csv_file", help="Path to the input CSV file")
    parser.add_argument("json_file", nargs="?", help="Path to the output JSON file (optional)")
    
    args = parser.parse_args()
    csv_to_json(args.csv_file, args.json_file)

if __name__ == "__main__":
    main()
