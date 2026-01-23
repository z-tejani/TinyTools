import os
import hashlib
import argparse

def calculate_hash(file_path, chunk_size=8192):
    """Calculates the SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(chunk_size)
                if not data:
                    break
                sha256.update(data)
        return sha256.hexdigest()
    except OSError as e:
        print(f"Error reading {file_path}: {e}")
        return None

def find_duplicates(directory):
    directory = os.path.abspath(directory)
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        return

    print(f"Scanning for duplicates in: {directory}")
    
    hashes = {} # Map hash -> list of file paths
    
    for root, _, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            
            # Skip empty files (optional, but usually desired)
            if os.path.getsize(file_path) == 0:
                continue

            file_hash = calculate_hash(file_path)
            
            if file_hash:
                if file_hash in hashes:
                    hashes[file_hash].append(file_path)
                else:
                    hashes[file_hash] = [file_path]

    duplicates_found = False
    for file_hash, file_list in hashes.items():
        if len(file_list) > 1:
            duplicates_found = True
            print(f"\nDuplicate found (Hash: {file_hash[:8]}...):")
            for path in file_list:
                print(f"  - {path}")

    if not duplicates_found:
        print("\nNo duplicate files found.")

def main():
    parser = argparse.ArgumentParser(description="Find duplicate files in a directory.")
    parser.add_argument("directory", nargs="?", default=".", help="The directory to scan (default: current directory)")
    
    args = parser.parse_args()
    find_duplicates(args.directory)

if __name__ == "__main__":
    main()
