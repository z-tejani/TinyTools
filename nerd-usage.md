# NERD: Network Exploration & Recon Dorks
The "Swiss Army Knife" of Reconnaissance
Welcome to NERD. This tool helps you uncover information using both Passive (Google Dorking) and Active (Direct Connection) reconnaissance techniques.


## ⚠️ IMPORTANT DISCLAIMER & LIABILITY
Usage of this tool is strictly at your own risk.
The author and contributors of NERD assume no responsibility or liability for any misuse, damage, or illegal activities resulting from the use of this tool. It is provided specifically for educational purposes and authorized personal security testing only.
### Strict Usage Guidelines:
Non-Nefarious Use Only: This tool must never be used for malicious purposes, unauthorized reconnaissance, cyberstalking, or illegal data extraction.
User Responsibility: You are solely responsible for your actions and for ensuring that your use of this tool complies with all local, state, and federal laws.
Non-Corporate Use: This tool is not intended for use in corporate, enterprise, or commercial environments without explicit written authorization from the network owner.
Active Recon Warning: Using the --active flag creates traffic logs on the target server. This is not silent.


## Getting Started
Ensure you have Python 3 installed. Make the script executable:
`chmod +x nerd.py`



## Active Reconnaissance
Active Recon means the tool directly connects to the target server. This allows you to gather real-time data that Google might not have, but it leaves a footprint.
### Features:
- DNS Resolution: Finds the server's IP address.
- Header Analysis: Identifies the server software (e.g., Apache, Nginx) and technology stack (e.g., PHP, ASP.NET).
- Robots.txt Extraction: Finds paths the admin has explicitly hidden from search engines.

Command:
`./nerd.py --site example.com --active`

### Example Output:
```
[!] INITIATING ACTIVE RECON ON: example.com
[!] WARNING: This interaction is being logged by the target.
--------------------------------------------------
[*] DNS Resolution : example.com -> 93.184.216.34
[*] Server Header  : ECS (dcb/7F83)
[*] Technology     : Not Found
[*] Robots.txt     : FOUND
    -> Found 2 hidden paths:
       Disallow: /private/
       Disallow: /admin-console/
--------------------------------------------------
```


## Passive Recon (Google Dorking)
Passive Recon does not touch the target server. It queries search engines (Google, Bing, etc.) as data they have already indexed. It is generally quieter.
### Manual Searching
Build specific search queries without memorizing complex syntax.
```
# Find PDF files on nasa.gov
./nerd.py "confidential" --site nasa.gov --filetype pdf

```

### Using Presets (Recipes)
Use built-in recipes for common tasks.
```
# Find exposed .env files
./nerd.py --preset env_files --site example.com

# Find open directory listings
./nerd.py --preset index_of --site example.com
```


## Automation
Speed up your workflow.
```
# Open results directly in your browser
./nerd.py --preset sql_dumps --site target.com --open

# Copy results to clipboard (for use in Tor Browser/Reports)
./nerd.py --preset login_pages --site target.com --copy
```


## Full Command Reference
| Flag / Option | Description |
|---------------|-------------|
| Active Recon | |
| --active | Performs direct connection (DNS, Headers, Robots). Requires --site. |
| Passive Search | |
| keywords | Main search terms. |
| -s, --site | Limit results to a specific domain. |
| -f, --filetype | Search for a specific file extension (pdf, sql, etc). |
| -p, --preset | Use a pre-built dork "recipe" (see help menu). |
| Logic | |
| --after / --before | Filter results by date. |
| --exclude | Exclude specific terms. |
| --engine | Select search engine (google, bing, duckduckgo). |
| Output | |
| -o, --open | Open in browser. |
| --copy | Copy to clipboard. |
| --output | Save to file. |
| --json | Output machine-readable JSON. |
