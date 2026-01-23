import argparse
import datetime
import os

NOTE_FILE = "notes.txt"

def add_note(note):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {note}\n"
    
    # We want notes.txt in the same directory as the script, 
    # or arguably in the user's home dir. 
    # For this standalone tool, let's put it in the script's directory for portability
    # unless otherwise specified.
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, NOTE_FILE)
    
    try:
        with open(file_path, "a") as f:
            f.write(entry)
        print(f"Note added to {file_path}")
    except Exception as e:
        print(f"Error writing note: {e}")

def list_notes():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, NOTE_FILE)
    
    if not os.path.exists(file_path):
        print("No notes found.")
        return

    print(f"--- Notes from {file_path} ---")
    with open(file_path, "r") as f:
        print(f.read())

def main():
    parser = argparse.ArgumentParser(description="Add a quick note to notes.txt.")
    parser.add_argument("note", nargs="?", help="The note content. If omitted, lists notes.")
    
    args = parser.parse_args()
    
    if args.note:
        add_note(args.note)
    else:
        list_notes()

if __name__ == "__main__":
    main()
