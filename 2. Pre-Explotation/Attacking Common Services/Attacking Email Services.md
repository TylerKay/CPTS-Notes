## Overview

- **Function:** Mail servers handle, deliver, and store emails across networks using protocols like SMTP, POP3, and IMAP4.
- **Core Protocols:**
    - **SMTP (Simple Mail Transfer Protocol):** Used for sending/relaying emails between clients and servers (Ports: TCP/25 unencrypted, TCP/465 encrypted, TCP/587 encrypted/STARTTLS).
    - **POP3 (Post Office Protocol v3):** Downloads and typically deletes messages from the server mailbox (Ports: TCP/110 unencrypted, TCP/995 encrypted).
    - **IMAP4 (Internet Message Access Protocol v4):** Keeps messages synchronized on the server to allow access across multiple devices (Ports: TCP/143 unencrypted, TCP/993 encrypted).
## Enumeration & Discovery
### 1. Identifying Mail Servers (MX Records)

Query Mail eXchanger (MX) records to determine whether a target uses cloud providers (e.g., G-Suite, Microsoft 365, Zoho) or self-hosted infrastructure.
- **Using `host`:**
    Bash
    ```
    host -t MX <domain>
    ```
- **Using `dig`:**
    Bash
    ```
    dig mx <domain> | grep "MX" | grep -v ";"
    ```
### 2. Port Scanning (Custom Mail Servers)
Enumerate common unencrypted and encrypted mail service ports using Nmap:
Bash
```
sudo nmap -Pn -sV -sC -p25,143,110,465,587,993,995 <target_ip>
```
## Authentication & User Enumeration

### 1. SMTP Commands

Self-hosted or misconfigured SMTP servers often support commands that reveal valid usernames:
- **`VRFY`:** Checks if a specific email username exists.
    Plaintext
    ```
    VRFY root
    ```
- **`EXPN`:** Reveals all members of an alias or distribution list.
    Plaintext
    ```
    EXPN support-team
    ```
- **`RCPT TO`:** Identifies valid recipients during an email transaction session.
    Plaintext
    ```
    MAIL FROM:test@htb.com
    RCPT TO:john
    ```
- **Automated Tool (`smtp-user-enum`):**
    Bash
    ```
    smtp-user-enum -M RCPT -U userlist.txt -D <domain> -t <target_ip>
    ```
### 2. POP3 User Enumeration
Check if a username exists by supplying the `USER` command:
Plaintext

```
USER john
```
### 3. Cloud User Enumeration (Office 365)

Validate domains and enumerate valid accounts using specialized tooling like `o365spray`:
- **Validate Domain:**
    Bash
    ```
    python3 o365spray.py --validate --domain <domain>
    ```
- **Enumerate Users:**
    Bash
    ```
    python3 o365spray.py --enum -U users.txt --domain <domain>
    ```
## Password Attacks & Spraying
### 1. Traditional Protocols (POP3/IMAP/SMTP)
Use `hydra` to brute-force or password spray standard mail services:
Bash
```
hydra -L users.txt -p '<password>' -f <target_ip> pop3
```
### 2. Cloud Platforms (Office 365)
Perform safe password spraying against cloud targets while avoiding account lockouts:
Bash
```
python3 o365spray.py --spray -U usersfound.txt -p '<password>' --count 1 --lockout 1 --domain <domain>
```

## Protocol-Specific Exploits: SMTP Open Relay

- **Concept:** A misconfigured SMTP server that permits unauthenticated mail relaying from any source, enabling attackers to spoof corporate identities or launch phishing campaigns.
- **Scanning for Open Relays (Nmap):**
    Bash
    ```
    nmap -p25 -Pn --script smtp-open-relay <target_ip>
    ```
- **Sending Spoofed Phishing Emails (`swaks`):**
    Bash
    ```
    swaks --from <spoofed_email@domain.com> --to <victim@domain.com> --header 'Subject: Company Notification' --body 'Please complete the survey: http://phishing-link.com/' --server <target_ip>
    ```