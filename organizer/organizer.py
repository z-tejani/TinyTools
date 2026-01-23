import os
import shutil
import argparse
import sys

# Define file type categories
FILE_TYPES = {
    'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'],
    'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx', '.csv'],
    'Audio': ['.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a'],
    'Video': ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv'],
    'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
    'Code': ['.py', '.go', '.js', '.html', '.css', '.java', '.c', '.cpp', '.h', '.ts', '.json', '.xml'],
    'Executables': ['.exe', '.msi', '.dmg', '.app', '.deb', '.rpm']
}

def organize_directory(directory):
    directory = os.path.abspath(directory)
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        return

    print(f"Organizing directory: {directory}")

    # Create subdirectories if they don't exist
    for category in FILE_TYPES.keys():
        category_path = os.path.join(directory, category)
        if not os.path.exists(category_path):
            # We delay creation until we actually need to move a file to avoid empty folders
            pass

    items = os.listdir(directory)
    moved_count = 0

    for item in items:
        item_path = os.path.join(directory, item)

        # Skip directories
        if os.path.isdir(item_path):
            continue

        # Skip this script if it's in the folder
        if item == os.path.basename(__file__):
            continue

        _, extension = os.path.splitext(item)
        extension = extension.lower()

        destination_category = None
        for category, extensions in FILE_TYPES.items():
            if extension in extensions:
                destination_category = category
                break
        
        # If no category found, maybe skip or put in 'Others'
        # For this script, we'll skip unknown types or put in 'Others'
        if not destination_category:
            destination_category = 'Others'

        destination_folder = os.path.join(directory, destination_category)
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)

        destination_path = os.path.join(destination_folder, item)

        # Handle duplicate filenames in destination
        if os.path.exists(destination_path):
            base, ext = os.path.splitext(item)
            counter = 1
            while os.path.exists(destination_path):
                new_name = f"{base}_{counter}{ext}"
                destination_path = os.path.join(destination_folder, new_name)
                counter += 1
        
        try:
            shutil.move(item_path, destination_path)
            print(f"Moved: {item} -> {destination_category}/")
            moved_count += 1
        except Exception as e:
            print(f"Error moving {item}: {e}")

    print(f"Done. Organized {moved_count} files.")

def main():
    parser = argparse.ArgumentParser(description="Organize files in a directory by type.")
    parser.add_argument("directory", nargs="?", default=".", help="The directory to organize (default: current directory)")
    
    args = parser.parse_args()
    
    organize_directory(args.directory)

if __name__ == "__main__":
    main()
