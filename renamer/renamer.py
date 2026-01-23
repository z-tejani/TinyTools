#!/usr/bin/env python3
"""
Renamer.py - The Mass Labeler
Bulk rename files using search/replace or Regex.

Safety: Defaults to DRY RUN mode. Use --commit to apply changes.
"""

import os
import re
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="Bulk rename files in a directory.")
    parser.add_argument("search", help="The string or regex pattern to look for")
    parser.add_argument("replace", help="The replacement string")
    parser.add_argument("path", nargs="?", default=".", help="Directory to process (default: current)")
    parser.add_argument("-r", "--regex", action="store_true", help="Treat search pattern as a Regular Expression")
    parser.add_argument("-c", "--commit", action="store_true", help="Actually rename the files (omitting this runs in DRY RUN mode)")
    parser.add_argument("-i", "--ignore-case", action="store_true", help="Ignore case during search")
    parser.add_argument("--hidden", action="store_true", help="Include hidden files (starting with .)")

    args = parser.parse_args()

    if not os.path.isdir(args.path):
        print(f"Error: {args.path} is not a valid directory.")
        sys.exit(1)

    # Compile regex if needed
    flags = re.IGNORECASE if args.ignore_case else 0
    
    files = os.listdir(args.path)
    if not args.hidden:
        files = [f for f in files if not f.startswith('.')]
    
    # Filter out directories
    files = [f for f in files if os.path.isfile(os.path.join(args.path, f))]
    files.sort()

    changes = []

    for filename in files:
        new_name = None
        if args.regex:
            try:
                new_name = re.sub(args.search, args.replace, filename, flags=flags)
            except re.error as e:
                print(f"Regex Error: {e}")
                sys.exit(1)
        else:
            if args.ignore_case:
                # Case insensitive literal replace is a bit tricky in Python without regex
                # We'll use regex for it anyway but escape the search string
                pattern = re.escape(args.search)
                new_name = re.sub(pattern, args.replace, filename, flags=re.IGNORECASE)
            else:
                new_name = filename.replace(args.search, args.replace)

        if new_name != filename:
            changes.append((filename, new_name))

    if not changes:
        print("No files match the search pattern.")
        return

    print(f"{'DRY RUN MODE' if not args.commit else 'COMMITTING CHANGES'}")
    print("-" * 60)
    
    for old, new in changes:
        print(f"{old}  ->  {new}")

    print("-" * 60)
    print(f"Total files to rename: {len(changes)}")

    if args.commit:
        confirm = input("Are you sure you want to proceed? (y/N): ")
        if confirm.lower() != 'y':
            print("Aborted.")
            return

        for old, new in changes:
            old_path = os.path.join(args.path, old)
            new_path = os.path.join(args.path, new)
            
            if os.path.exists(new_path):
                print(f"[!] Warning: Skipping '{old}' -> '{new}' (Target already exists)")
                continue
                
            try:
                os.rename(old_path, new_path)
            except Exception as e:
                print(f"[!] Error renaming '{old}': {e}")
        
        print("Done.")
    else:
        print("This was a dry run. Use --commit (and 'y' to confirm) to apply these changes.")

if __name__ == "__main__":
    main()
