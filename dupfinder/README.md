# Duplicate File Finder

A script that scans a folder recursively, calculates the SHA-256 hash of each file, and reports any duplicates found.

## Usage

```bash
python3 dupfinder.py [directory_path]
```

## How it works

1. Traverses the directory tree.
2. Calculates the SHA-256 hash for every file.
3. Groups files by hash.
4. Prints groups containing more than one file.
