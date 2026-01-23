# Image Compressor

A tool that takes an image (or a folder of images) and shrinks its file size using the Pillow library.

## Requirements

- Python 3
- Pillow (`pip install Pillow`)

## Usage

```bash
python3 compressor.py <file_or_directory> [--quality 60]
```

## Features

- Supports JPEG, PNG, WEBP.
- Recursively processes directories.
- Saves compressed files as `filename_compressed.ext` to avoid overwriting originals.
