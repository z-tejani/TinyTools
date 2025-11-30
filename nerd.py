#!/usr/bin/env python3

"""
NERD (Network Exploration & Recon Dorks) v3.0
=============================================

The ultimate CLI tool for Google Dorking.

Features:
- Build complex queries manually.
- Use pre-built "recipes" (presets) for common tasks.
- Filter results by date.
- Automatically open results in your default browser.
- Save queries to a file.
- "Explain" mode to learn how the dork works.

Usage:
  nerd --preset sql_dumps --site target.com --open
  nerd "confidential" --filetype pdf --after 2024-01-01 --output dorks.txt
  nerd --preset git_folders --explain
"""

import argparse
import sys
import webbrowser
import urllib.parse
from datetime import datetime

# --- Built-in Dork Recipes ---
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
        "desc": "Finds .env files often used by frameworks (Laravel, Node) to store secrets."
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

def create_dork_query(args):
    """Combines arguments and presets into a Google dork query string."""
    
    query_parts = []

    # 1. Handle Presets
    if args.preset:
        if args.preset in PRESETS:
            # Wrap in parens for safety when combining with other ops
            query_parts.append(f"({PRESETS[args.preset]['dork']})")
        else:
            print(f"Error: Preset '{args.preset}' not found.")
            sys.exit(1)

    # 2. Handle Manual Keywords
    if args.keywords:
        if " " in args.keywords and not '"' in args.keywords:
             query_parts.append(f'"{args.keywords}"')
        else:
            query_parts.append(args.keywords)

    # 3. Add Search Operators
    if args.site: query_parts.append(f"site:{args.site}")
    if args.filetype: query_parts.append(f"filetype:{args.filetype}")
    if args.ext: query_parts.append(f"ext:{args.ext}")
    if args.inurl: query_parts.append(f"inurl:{args.inurl}")
    if args.intitle: query_parts.append(f"intitle:{args.intitle}")
    if args.intext: query_parts.append(f"intext:{args.intext}")
    if args.exclude: query_parts.append(f"-{args.exclude}")

    # 4. Date Filters
    if args.after: query_parts.append(f"after:{args.after}")
    if args.before: query_parts.append(f"before:{args.before}")

    return " ".join(query_parts)

def explain_dork(args, query):
    """Prints a human-readable explanation of the query."""
    print("\n--- Dork Explanation ---")
    
    if args.preset:
        print(f"[*] Base Preset: {args.preset}")
        print(f"    -> {PRESETS[args.preset]['desc']}")
        
    if args.keywords:
        print(f"[*] Keywords: Searching for literal text '{args.keywords}'")
        
    if args.site:
        print(f"[*] Scope: Restricted to domain '{args.site}'")
        
    if args.filetype or args.ext:
        ft = args.filetype if args.filetype else args.ext
        print(f"[*] File Extension: Looking specifically for '{ft}' files")
        
    if args.exclude:
        print(f"[*] Filtering: Removing results containing '{args.exclude}'")
        
    if args.after or args.before:
        print(f"[*] Timeframe: Filtering by date ({args.after or 'Any'} to {args.before or 'Now'})")
        
    print("------------------------\n")

def main():
    parser = argparse.ArgumentParser(
        prog="nerd",
        description="NERD: Network Exploration & Recon Dorks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Presets:
  """ + "\n  ".join([f"{k:<15} : {v['desc']}" for k, v in PRESETS.items()])
    )
    
    # Arguments
    parser.add_argument("keywords", nargs="?", default="", help="Main search terms")
    parser.add_argument("-s", "--site", help="Limit to specific site")
    parser.add_argument("-f", "--filetype", help="Specific file type")
    parser.add_argument("--ext", help="Alias for filetype")
    parser.add_argument("-u", "--inurl", help="String in URL")
    parser.add_argument("-t", "--intitle", help="String in Title")
    parser.add_argument("-i", "--intext", help="String in Body Text")
    parser.add_argument("-e", "--exclude", help="Exclude keyword")
    parser.add_argument("-p", "--preset", help=f"Use a built-in dork recipe")
    parser.add_argument("--after", help="Search after date (YYYY-MM-DD)")
    parser.add_argument("--before", help="Search before date (YYYY-MM-DD)")
    
    # Actions
    parser.add_argument("-o", "--open", action="store_true", help="Open in browser")
    parser.add_argument("--output", help="Save the query to a specific file")
    parser.add_argument("--explain", action="store_true", help="Explain the query logic")

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
        
    args = parser.parse_args()
    
    # Validation
    if not (args.keywords or args.preset or any([args.site, args.filetype, args.ext, args.inurl, args.intitle, args.after])):
         print("Error: You must provide keywords, a preset, or a search operator.")
         sys.exit(1)

    # Build Query
    dork = create_dork_query(args)
    
    # 1. Explain Mode
    if args.explain:
        explain_dork(args, dork)

    # 2. Print Query
    print(f"[NERD Query]: {dork}")
    
    # 3. Save to File
    if args.output:
        try:
            with open(args.output, "a") as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] {dork}\n")
            print(f"[Saved]: Appended to {args.output}")
        except Exception as e:
            print(f"[Error]: Could not save file - {e}")

    # 4. Open in Browser
    if args.open:
        encoded_query = urllib.parse.quote_plus(dork)
        url = f"https://www.google.com/search?q={encoded_query}"
        print(f"[Opening]: {url}")
        webbrowser.open(url)

if __name__ == "__main__":
    main()