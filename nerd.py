#!/usr/bin/env python3

"""
NERD (Network Exploration & Recon Dorks)
https://github.com/z-tejani/TinyTools/blob/main/nerd.py
========================================

The "Swiss Army Knife" of Reconnaissance.
Now supports PASSIVE (Dorks) and ACTIVE (Direct) reconnaissance.

Usage:
  nerd --preset sql_dumps --site target.com --open
  nerd --site target.com --active
"""

import argparse
import sys
import webbrowser
import urllib.parse
import urllib.request
import urllib.error
import socket
import json
import subprocess
from datetime import datetime

ENGINES = {
    "google": "https://www.google.com/search?q=",
    "bing": "https://www.bing.com/search?q=",
    "duckduckgo": "https://duckduckgo.com/?q=",
    "yahoo": "https://search.yahoo.com/search?p=",
    "ask": "https://www.ask.com/web?q="
}

PRESETS = {
    "login_pages": {
        "dork": 'inurl:login OR inurl:signin OR intitle:"Login" OR intitle:"Sign In"',
        "desc": "Finds common login portals."
    },
    "sql_dumps": {
        "dork": 'filetype:sql "INSERT INTO" ("pass" OR "password" OR "passwd")',
        "desc": "Finds exposed SQL database exports containing passwords."
    },
    "index_of": {
        "dork": 'intitle:"index of" "parent directory"',
        "desc": "Finds open directories (servers allowing file browsing)."
    },
    "config_files": {
        "dork": 'ext:xml OR ext:conf OR ext:cnf OR ext:reg OR ext:inf OR ext:rdp OR ext:cfg',
        "desc": "Finds configuration files that may contain keys or secrets."
    },
    "env_files": {
        "dork": 'ext:env OR filetype:env "DB_PASSWORD"',
        "desc": "Finds .env files often used by frameworks (Laravel, Node)."
    },
    "wordpress_users": {
        "dork": 'inurl:/wp-json/wp/v2/users',
        "desc": "Enumerates WordPress users via the API."
    },
    "public_cameras": {
        "dork": 'intitle:"webcam 7" OR inurl:"/view/index.shtml" OR inurl:"/view/view.shtml"',
        "desc": "Finds publicly accessible IP cameras."
    },
    "log_files": {
        "dork": 'ext:log OR ext:txt "password" OR "username"',
        "desc": "Finds text log files that might contain credentials."
    },
    "cloud_buckets": {
        "dork": 'site:s3.amazonaws.com OR site:blob.core.windows.net OR site:googleapis.com',
        "desc": "Searches for public cloud storage buckets."
    },
    "git_folders": {
        "dork": 'inurl:".git" intitle:"Index of"',
        "desc": "Finds exposed .git repositories."
    },
    "php_errors": {
        "dork": 'filetype:php "Warning" "on line"',
        "desc": "Finds PHP error messages leaking server paths."
    },
    "exposed_docs": {
        "dork": 'ext:doc OR ext:docx OR ext:pdf OR ext:xls OR ext:xlsx OR ext:ppt OR ext:pptx',
        "desc": "Finds public office documents and PDFs."
    }
}

def perform_active_recon(target):
    """
    Performs direct connection to the target to gather intelligence.
    WARNING: This creates traffic logs on the target server.
    """
    print(f"\n[!] INITIATING ACTIVE RECON ON: {target}")
    print("[!] WARNING: This interaction is being logged by the target.")
    print("-" * 50)
    
    results = {}

    domain = target.replace("https://", "").replace("http://", "").split("/")[0]
    results['domain'] = domain

    try:
        ip_address = socket.gethostbyname(domain)
        print(f"[*] DNS Resolution : {domain} -> {ip_address}")
        results['ip'] = ip_address
    except socket.gaierror:
        print(f"[!] DNS Resolution : FAILED (Could not resolve {domain})")
        results['ip'] = None

    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) NERD-Security-Tool/5.0'
    headers = {'User-Agent': user_agent}
    
    target_url = f"http://{domain}"
    
    try:
        req = urllib.request.Request(target_url, headers=headers, method="HEAD")
        with urllib.request.urlopen(req, timeout=5) as response:
            server_header = response.headers.get('Server', 'Unknown')
            x_powered_by = response.headers.get('X-Powered-By', 'Not Found')
            print(f"[*] Server Header  : {server_header}")
            print(f"[*] Technology     : {x_powered_by}")
            
            results['server'] = server_header
            results['tech'] = x_powered_by
            results['status'] = response.status

    except urllib.error.URLError as e:
        print(f"[!] HTTP Check     : FAILED ({e})")
        results['http_error'] = str(e)
    except Exception as e:
        print(f"[!] Error          : {e}")

    robots_url = f"http://{domain}/robots.txt"
    try:
        req = urllib.request.Request(robots_url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            content = response.read().decode('utf-8', errors='ignore')
            print(f"[*] Robots.txt     : FOUND")
            
            disallowed = [line.strip() for line in content.split('\n') if "Disallow:" in line]
            if disallowed:
                print(f"    -> Found {len(disallowed)} hidden paths (showing first 5):")
                for entry in disallowed[:5]:
                    print(f"       {entry}")
            else:
                print("    -> No 'Disallow' entries found.")
            
            results['robots_found'] = True
            results['hidden_paths'] = disallowed
            
    except urllib.error.HTTPError:
        print(f"[*] Robots.txt     : NOT FOUND (404)")
        results['robots_found'] = False
    except Exception:
        print(f"[*] Robots.txt     : UNREACHABLE")

    print("-" * 50)
    return results

def copy_to_clipboard(text):
    try:
        if sys.platform == "darwin":
            process = subprocess.Popen('pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
            process.communicate(text.encode('utf-8'))
        elif sys.platform == "win32":
            subprocess.run(['clip'], input=text.strip().encode('utf-16'), check=True)
        else:
            try:
                subprocess.run(['xclip', '-selection', 'clipboard'], input=text.encode('utf-8'), check=True)
            except FileNotFoundError:
                try:
                    subprocess.run(['xsel', '--clipboard', '--input'], input=text.encode('utf-8'), check=True)
                except FileNotFoundError:
                    print("[!] Error: xclip or xsel not found. Cannot copy to clipboard.")
                    return False
        return True
    except Exception as e:
        print(f"[!] Clipboard Error: {e}")
        return False

def create_dork_query(args):
    query_parts = []

    if args.preset:
        if args.preset in PRESETS:
            query_parts.append(f"({PRESETS[args.preset]['dork']})")
        else:
            print(f"Error: Preset '{args.preset}' not found.")
            sys.exit(1)

    if args.keywords:
        if " " in args.keywords and not '"' in args.keywords:
             query_parts.append(f'"{args.keywords}"')
        else:
            query_parts.append(args.keywords)

    if args.site: query_parts.append(f"site:{args.site}")
    if args.filetype: query_parts.append(f"filetype:{args.filetype}")
    if args.ext: query_parts.append(f"ext:{args.ext}")
    if args.inurl: query_parts.append(f"inurl:{args.inurl}")
    if args.intitle: query_parts.append(f"intitle:{args.intitle}")
    if args.intext: query_parts.append(f"intext:{args.intext}")
    if args.exclude: query_parts.append(f"-{args.exclude}")

    if args.after: query_parts.append(f"after:{args.after}")
    if args.before: query_parts.append(f"before:{args.before}")

    return " ".join(query_parts)

def explain_dork(args, query):
    print("\n--- Dork Explanation ---")
    if args.preset: print(f"[*] Preset: {args.preset} -> {PRESETS[args.preset]['desc']}")
    if args.site: print(f"[*] Scope: Restricted to '{args.site}'")
    print(f"[*] Engine: {args.engine.capitalize()}")
    print("------------------------\n")

def main():
    parser = argparse.ArgumentParser(
        prog="nerd",
        description="NERD v5.0: Network Exploration & Recon Dorks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Supported Engines:
  google, bing, duckduckgo, yahoo, ask

Presets:
  """ + "\n  ".join([f"{k:<15} : {v['desc']}" for k, v in PRESETS.items()])
    )
    
    parser.add_argument("keywords", nargs="?", default="", help="Search terms")
    parser.add_argument("-s", "--site", help="Target domain")
    parser.add_argument("-f", "--filetype", help="File extension")
    parser.add_argument("--ext", help="Alias for filetype")
    parser.add_argument("-u", "--inurl", help="URL pattern")
    parser.add_argument("-t", "--intitle", help="Title pattern")
    parser.add_argument("-i", "--intext", help="Body text pattern")
    parser.add_argument("-e", "--exclude", help="Exclude terms")
    parser.add_argument("-p", "--preset", help="Use built-in dork")
    parser.add_argument("--after", help="Date: After (YYYY-MM-DD)")
    parser.add_argument("--before", help="Date: Before (YYYY-MM-DD)")
    
    parser.add_argument("--engine", default="google", choices=ENGINES.keys(), help="Select search engine")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--copy", action="store_true", help="Copy generated URL to clipboard")
    
    parser.add_argument("-o", "--open", action="store_true", help="Open in browser")
    parser.add_argument("--output", help="Save to file")
    parser.add_argument("--explain", action="store_true", help="Explain logic")
    
    parser.add_argument("--active", action="store_true", help="Performs active recon (DNS, Headers, Robots.txt)")

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
        
    args = parser.parse_args()
    
    if args.active:
        if not args.site:
            print("[!] Error: Active recon requires a target site via --site (e.g., --site example.com)")
            sys.exit(1)
        
        active_data = perform_active_recon(args.site)
        
        if args.json:
            print(json.dumps(active_data, indent=2))
        
        if args.output:
            try:
                with open(args.output, "a") as f:
                    f.write(f"[{datetime.now()}] [ACTIVE] {json.dumps(active_data)}\n")
                print(f"[Saved]: {args.output}")
            except Exception as e:
                print(f"[Error]: {e}")
        
        sys.exit(0)

    if not (args.keywords or args.preset or any([args.site, args.filetype, args.ext, args.inurl, args.intitle])):
         print("Error: Provide keywords, a preset, or an operator.")
         sys.exit(1)

    dork = create_dork_query(args)
    base_url = ENGINES[args.engine]
    encoded_query = urllib.parse.quote_plus(dork)
    full_url = f"{base_url}{encoded_query}"

    if args.json:
        data = {
            "timestamp": datetime.now().isoformat(),
            "engine": args.engine,
            "dork": dork,
            "url": full_url,
            "target": args.site if args.site else "global"
        }
        print(json.dumps(data, indent=2))
        sys.exit(0)

    if args.explain:
        explain_dork(args, dork)

    print(f"[NERD Query]: {dork}")
    print(f"[Engine]: {args.engine}")
    print(f"[Link]: {full_url}")

    if args.copy:
        if copy_to_clipboard(full_url):
            print("[Success]: Link copied to clipboard!")

    if args.output:
        try:
            with open(args.output, "a") as f:
                f.write(f"[{datetime.now()}] ({args.engine}) {dork}\n")
            print(f"[Saved]: {args.output}")
        except Exception as e:
            print(f"[Error]: {e}")

    if args.open:
        print(f"[Opening]: {full_url}")
        webbrowser.open(full_url)

if __name__ == "__main__":
    main()