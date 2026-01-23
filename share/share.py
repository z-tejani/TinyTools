#!/usr/bin/env python3
"""
Share.py - The LAN Dropzone
A zero-dependency HTTP server that supports file uploads.

Usage:
    python3 share.py [port]

Features:
    - Serves files from current directory (like python -m http.server)
    - Accepts file uploads via POST
    - Simple drag-and-drop web interface
"""

import http.server
import socketserver
import os
import sys
import cgi
import shutil
import io

# Default port
PORT = 8000
if len(sys.argv) > 1:
    try:
        PORT = int(sys.argv[1])
    except ValueError:
        print(f"Invalid port: {sys.argv[1]}")
        sys.exit(1)

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """Serve files or the upload interface."""
        # Check if asking for the special upload page if directory listing is disabled or just as a convenience
        # For this tool, we inject the upload form into directory listings or serve it at /upload
        
        # We will intercept the directory listing to inject our upload form
        if self.path == '/upload':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(self.get_upload_page().encode())
            return
            
        return super().do_GET()

    def list_directory(self, path):
        """Helper to produce a directory listing (absent index.html).
        We override this to inject the upload form at the top of the listing.
        """
        try:
            list = os.listdir(path)
        except OSError:
            self.send_error(404, "No permission to list directory")
            return None
        
        list.sort(key=lambda a: a.lower())
        r = []
        try:
            displaypath = cgi.escape(self.path, quote=True)
            enc = sys.getfilesystemencoding()
            title = 'Directory listing for %s' % displaypath
            r.append('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">')
            r.append('<html>\n<head>')
            r.append('<meta http-equiv="Content-Type" content="text/html; charset=%s">' % enc)
            r.append('<title>%s</title>\n</head>' % title)
            r.append('<body>\n<h1>%s</h1>' % title)
            
            # --- INJECT UPLOAD FORM ---
            r.append(self.get_upload_form_html())
            r.append('<hr>\n<ul>')
            
            for name in list:
                fullname = os.path.join(path, name)
                displayname = linkname = name
                # Append / for directories or @ for symbolic links
                if os.path.isdir(fullname):
                    displayname = name + "/"
                    linkname = name + "/"
                if os.path.islink(fullname):
                    displayname = name + "@"
                    # Note: a link to a directory displays with @ and links with /
                
                r.append('<li><a href="%s">%s</a></li>' % (
                    cgi.escape(linkname, quote=True),
                    cgi.escape(displayname, quote=True)))
            
            r.append('</ul>\n<hr>\n</body>\n</html>\n')
        except Exception as e:
            # Fallback if something breaks in our injection
            print(f"Error generating listing: {e}")
            return super().list_directory(path)
            
        encoded = ''.join(r).encode(enc, 'surrogateescape')
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=%s" % enc)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)
        return None

    def do_POST(self):
        """Handle file uploads."""
        r, info = self.deal_post_data()
        
        f = io.BytesIO()
        if r:
            f.write(b"Success\n")
            self.send_response(200)
        else:
            f.write(b"Failed\n")
            self.send_response(500)
            
        length = f.tell()
        f.seek(0)
        
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        if f:
            self.copyfile(f, self.wfile)
            f.close()

    def deal_post_data(self):
        """Process the POST request to save the file."""
        content_type = self.headers['content-type']
        if not content_type:
            return (False, "Content-Type header doesn't contain boundary")
        
        boundary = content_type.split("=")[1].encode()
        remainbytes = int(self.headers['content-length'])
        line = self.rfile.readline()
        remainbytes -= len(line)
        if not boundary in line:
            return (False, "Content NOT begin with boundary")
        
        line = self.rfile.readline()
        remainbytes -= len(line)
        fn = None
        
        # Parse headers to find filename
        while len(line) > 0 and line.strip():
            decoded_line = line.decode()
            if "Content-Disposition" in decoded_line:
                if "filename=" in decoded_line:
                    fn = decoded_line.split('filename=')[1]
                    if fn[0] == '"' or fn[0] == "'வுகளை:":
                        fn = fn[1:-1] # Strip quotes
                    fn = fn.strip()
            line = self.rfile.readline()
            remainbytes -= len(line)

        if not fn:
            return (False, "Can't find out file name...")
        
        # Sanitize filename
        fn = os.path.basename(fn)
        fn = os.path.join(os.getcwd(), fn)
        
        try:
            out = open(fn, 'wb')
        except IOError:
            return (False, "Can't create file to write, do you have permission to write?")
            
        # Read the file data
        # Note: The original simple approach might be buggy with binary data if not careful
        # We need to read until the boundary
        
        # A simple way to handle this without complex multipart parsing library is reading line by line
        # but that is slow for binary.
        # However, for a "Tiny Tool", we can try a slightly robust read loop.
        
        preline = self.rfile.readline()
        remainbytes -= len(preline)
        while remainbytes > 0:
            line = self.rfile.readline()
            remainbytes -= len(line)
            if boundary in line:
                preline = preline[0:-1]
                if preline.endswith(b'\r'):
                    preline = preline[0:-1]
                out.write(preline)
                out.close()
                return (True, "File '%s' upload success!" % fn)
            else:
                out.write(preline)
                preline = line
                
        return (False, "Unexpect Ends of data.")

    def get_upload_form_html(self):
        return """
        <div style="background: #f0f0f0; padding: 15px; border-radius: 5px; margin-bottom: 20px; border: 1px dashed #999;">
            <h3>Upload File</h3>
            <form ENCTYPE="multipart/form-data" method="post">
                <input name="file" type="file"/>
                <input type="submit" value="Upload"/>
            </form>
            <p style="font-size: small; color: #666;">Or use curl: <code>curl -F "file=@filename" http://host:port/</code></p>
        </div>
        """
        
    def get_upload_page(self):
        return """
        <html>
        <head><title>Upload</title></head>
        <body>
            <h1>File Upload</h1>
            %s
            <a href="/">Back to files</a>
        </body>
        </html>
        """ % self.get_upload_form_html()


def run(server_class=http.server.HTTPServer, handler_class=CustomHTTPRequestHandler):
    server_address = ('', PORT)
    httpd = server_class(server_address, handler_class)
    
    # Get local IP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()

    print(f"[-] Share.py is running.")
    print(f"[-] Serving at http://{IP}:{PORT}")
    print(f"[-] Uploads are saved to: {os.getcwd()}")
    print(f"[-] Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.socket.close()

if __name__ == '__main__':
    import socket
    run()
