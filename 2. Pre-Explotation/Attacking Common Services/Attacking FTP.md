# Attacking FTP (File Transfer Protocol)

## Overview

- **Protocol Function:** Standard network protocol used to transfer files and execute directory/file operations (changing directories, listing, renaming, deleting).
- **Default Port:** TCP/21.
- **Attack Vectors:** Exploiting misconfigurations, excessive privileges, known vulnerabilities, or zero-days.
## Enumeration
### 1. Nmap Scanning

Use default scripts (`-sC`) to check for anonymous login via the `ftp-anon` script, and version detection (`-sV`) to grab the FTP banner.
Bash
```
sudo nmap -sC -sV -p 21 <target_ip>
```
### 2. Manual Interaction
Connect to the service using the native FTP client or Netcat (`nc`).
Bash
```
ftp <target_ip>
nc <target_ip> 21
```
## Common Attacks & Misconfigurations
### 1. Anonymous Authentication
- **Risk:** If misconfigured with incorrect read/write permissions, anonymous users can access sensitive files or upload malicious scripts (e.g., web shells for path traversal attacks).
- **Exploitation:**
    Bash
    ```
    ftp <target_ip>
    # Username: anonymous
    # Password: <blank or any email>
    ```
- **Essential FTP Client Commands:**
    - `ls` / `cd` - Navigate directories.
    - `get` / `mget` - Download single/multiple files.
    - `put` / `mput` - Upload single/multiple files.
    - `help` - View available commands.
### 2. Brute Forcing
- **Use Case:** When anonymous authentication is disabled.
- **Tool (Medusa):**
    Bash
    ```
    medusa -u <username> -P /path/to/wordlist.txt -h <target_ip> -M ftp
    ```
- _Note: Modern applications frequently mitigate brute-forcing; **Password Spraying** is often a more effective alternative._
### 3. FTP Bounce Attack
- **Mechanism:** Abuses the FTP `PORT` command to route traffic and scan internal network devices hidden behind a DMZ (using the public FTP server as a proxy).
- **Exploitation (Nmap):**
    Bash
    ```
    nmap -Pn -v -n -p<port> -b anonymous:password@<ftp_server_ip> <internal_target_ip>
    ```
- _Note: Disabled by default on modern FTP servers, but vulnerabilities persist if explicitly misconfigured._