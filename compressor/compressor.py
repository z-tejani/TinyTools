import os
import argparse
from PIL import Image

# Supported image formats for Pillow
SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff']

def compress_image(file_path, quality=60):
    """Compresses a single image file."""
    try:
        with Image.open(file_path) as img:
            # Check if it's actually an image we want to process
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in SUPPORTED_FORMATS:
                return

            original_size = os.path.getsize(file_path)
            
            # Construct new filename
            filename = os.path.basename(file_path)
            name, ext = os.path.splitext(filename)
            new_filename = f"{name}_compressed{ext}"
            output_path = os.path.join(os.path.dirname(file_path), new_filename)

            # Save with reduced quality
            # Optimize flag helps for PNGs and JPEGs
            if ext in ['.jpg', '.jpeg']:
                img.save(output_path, "JPEG", quality=quality, optimize=True)
            elif ext == '.png':
                # PNG quality is different, usually uses 'optimize=True' and P_QUANTIZE
                # For simplicity in this script, we'll try to optimize.
                # Reducing colors is another way but changes content.
                # We will just optimize.
                img.save(output_path, "PNG", optimize=True)
            elif ext == '.webp':
                img.save(output_path, "WEBP", quality=quality)
            else:
                img.save(output_path)

            new_size = os.path.getsize(output_path)
            savings = original_size - new_size
            if savings > 0:
                print(f"Compressed {filename}: {original_size/1024:.2f}KB -> {new_size/1024:.2f}KB (Saved {savings/1024:.2f}KB)")
            else:
                print(f"Processed {filename}: No size reduction.")
                
    except Exception as e:
        print(f"Error compressing {file_path}: {e}")

def process_path(path, quality):
    path = os.path.abspath(path)
    if os.path.isfile(path):
        compress_image(path, quality)
    elif os.path.isdir(path):
        print(f"Processing directory: {path}")
        for root, _, files in os.walk(path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in SUPPORTED_FORMATS:
                    compress_image(os.path.join(root, file), quality)
    else:
        print(f"Error: {path} not found.")

def main():
    parser = argparse.ArgumentParser(description="Compress images in a file or directory.")
    parser.add_argument("path", help="File or directory to compress")
    parser.add_argument("--quality", type=int, default=60, help="Quality for JPEG/WEBP (1-100), default 60.")
    
    args = parser.parse_args()
    
    # Check for Pillow
    try:
        import PIL
    except ImportError:
        print("Error: Pillow library is not installed.")
        print("Please install it using: pip install Pillow")
        sys.exit(1)

    process_path(args.path, args.quality)

if __name__ == "__main__":
    import sys
    main()
