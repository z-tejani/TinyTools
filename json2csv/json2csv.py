import json
import csv
import argparse
import sys
import os

def json_to_csv(json_file, csv_file=None):
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return

    if not isinstance(data, list):
        print("Error: JSON root must be an array of objects.")
        return
    
    if not data:
        print("JSON array is empty.")
        return

    # Determine headers from all keys in all objects
    headers = set()
    for entry in data:
        if isinstance(entry, dict):
            headers.update(entry.keys())
        else:
            print("Error: JSON array must contain objects.")
            return
    
    headers = sorted(list(headers))

    if not csv_file:
        csv_file = os.path.splitext(json_file)[0] + '.csv'

    try:
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)
        print(f"Converted '{json_file}' to '{csv_file}'")
    except Exception as e:
        print(f"Error writing CSV file: {e}")

def main():
    parser = argparse.ArgumentParser(description="Convert a JSON array of objects to a CSV file.")
    parser.add_argument("json_file", help="Path to the input JSON file")
    parser.add_argument("csv_file", nargs="?", help="Path to the output CSV file (optional)")
    
    args = parser.parse_args()
    json_to_csv(args.json_file, args.csv_file)

if __name__ == "__main__":
    main()
