# Share.py - The LAN Dropzone

A zero-dependency HTTP server that supports file uploads via web interface or `curl`.

## Summary
Python's built-in `http.server` is great for sharing files but lacks an upload feature. `share.py` bridges this gap, allowing you to move files between machines on the same network effortlessly.

## Installation
No installation required beyond Python 3.
```bash
chmod +x share.py
```

## Usage
Start the server in the directory you want to share:
```bash
python3 share.py [port]
```

### Uploading Files
1.  **Web Interface:** Open `http://<your-ip>:8000` in any browser and use the upload form.
2.  **CLI (curl):**
    ```bash
    curl -F "file=@yourfile.zip" http://<your-ip>:8000/
    ```
