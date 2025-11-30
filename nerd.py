#!/usr/bin/env python3

"""
NERD (Network Exploration & Recon Dorks)
========================================

A CLI tool for building complex Google dork queries for educational,
security research, and defensive OSINT purposes.

Usage:
  ./nerd.py "admin login" --site example.com
  ./nerd.py "passwords" --filetype sql --inurl "db/"
  ./nerd.py "confidential" --site company.com --ext pdf -e "internal"

Disclaimer:
This tool is intended for legal and ethical use only. Users are responsible
for their own actions.
"""

import argparse
import sys

def create_dork_query(args):
    """Combines argparse arguments into a Google dork query string."""
    
    query_parts = []

    # Handle main keywords
    if args.keywords:
        if " " in args.keywords:
            query_parts.append(f'"{args.keywords}"')
        else:
            query_parts.append(args.keywords)

    # Add search operators
    if args.site:
        query_parts.append(f"site:{args.site}")
        
    if args.filetype:
        query_parts.append(f"filetype:{args.filetype}")

    if args.ext:
        query_parts.append(f"ext:{args.ext}")
        
    if args.inurl:
        query_parts.append(f"inurl:{args.inurl}")
        
    if args.intitle:
        query_parts.append(f"intitle:{args.intitle}")
        
    if args.intext:
        query_parts.append(f"intext:{args.intext}")
        
    if args.exclude:
        query_parts.append(f"-{args.exclude}")

    return " ".join(query_parts)

def main():
    """Main function to parse arguments and print the query."""
    
    parser = argparse.ArgumentParser(
        prog="nerd",  # Sets the name in the help output
        description="NERD: Network Exploration & Recon Dorks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example Uses:
  # Find PDF files on a specific site
  nerd --site example.com --filetype pdf
  
  # Find pages with "admin" in the title and "login" in the URL
  nerd --intitle "admin" --inurl "login"
  
  # Search for "config" files, excluding "default"
  nerd "config" --filetype ini --exclude "default"
"""
    )
    
    # --- Positional Argument ---
    parser.add_argument(
        "keywords",
        nargs="?",
        default="",
        help="The main keywords to search for."
    )
    
    # --- Optional Arguments ---
    parser.add_argument("-s", "--site", help="Search within a specific site")
    parser.add_argument("-f", "--filetype", help="Search for a specific file type")
    parser.add_argument("--ext", help="Alias for --filetype")
    parser.add_argument("-u", "--inurl", help="Search for a string within the URL")
    parser.add_argument("-t", "--intitle", help="Search for a string within the title")
    parser.add_argument("-i", "--intext", help="Search for a string within the body text")
    parser.add_argument("-e", "--exclude", help="Exclude a keyword")

    # If no arguments are provided at all (including help), print help
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
        
    args = parser.parse_args()
    
    # Generate and print the query
    query = create_dork_query(args)
    
    if not query:
        print("Error: Please provide at least one search term or operator.")
        sys.exit(1)

    print("\n[NERD Query]:")
    print(query)

if __name__ == "__main__":
    main()