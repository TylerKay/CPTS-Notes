## Overview

While modern applications rely heavily on TLS encryption, unencrypted or legacy protocols (HTTP, FTP, SNMP, Telnet, POP3, etc.) are still common in enterprise environments. These unencrypted gaps allow attackers to intercept cleartext credentials, session tokens, and sensitive hashes directly from network traffic.

## High-Level Methodology
1. **Capture or Obtain PCAP:** Collect network traffic via live sniffing or packet capture files (`.pcap` / `.pcapng`).
2. **Automated Extraction (`Pcredz`):** Quickly parse packet captures to extract plaintext credentials, NTLM hashes, Kerberos pre-auth hashes, and credit card numbers.
3. **Manual Analysis (`Wireshark`):** Apply targeted display filters to inspect protocol streams, identify cleartext authentication headers, or search for string patterns (e.g., passwords or POST bodies).

## Unencrypted vs. Encrypted Protocols Reference

|**Unencrypted Protocol**|**Encrypted Counterpart**|**Description**|
|---|---|---|
|**HTTP**|HTTPS|Transfers web pages and resources.|
|**FTP**|FTPS / SFTP|Transfers files between client and server.|
|**SNMP** (v1/v2)|SNMPv3|Network device monitoring and management.|
|**POP3 / IMAP / SMTP**|POP3S / IMAPS / SMTPS|Email retrieval and transmission.|
|**LDAP**|LDAPS|Directory service queries (AD integration).|
|**RDP**|RDP with TLS|Windows remote desktop access.|
|**DNS** (Traditional)|DoH (DNS over HTTPS)|Domain name resolution.|
|**SMB** (v1/v2)|SMB over TLS (v3.0)|File and printer sharing.|
|**VNC**|VNC with TLS/SSL|Graphical remote access.|

## Tools and Techniques
### 1. Wireshark (Manual Packet Analysis)
Wireshark features a powerful display filter engine and built-in search functions (`Edit > Find Packet`).

- **Useful Wireshark Display Filters:**
    - `ip.addr == <IP>` — Filter traffic for a specific IP address.
    - `tcp.port == 80` — Filter traffic by port.
    - `http` — Isolate HTTP traffic.
    - `http.request.method == "POST"` — Isolate HTTP POST requests (often contain form credentials).
    - `http contains "passw"` — Search for specific strings in HTTP layers.
    - `tcp.stream eq <ID>` — Track a specific TCP conversation stream.

### 2. Pcredz (Automated Extraction)

`Pcredz` is an automated tool designed to extract credentials, hashes, and sensitive data from live network interfaces or packet capture files.
- **Supported Artifacts:** HTTP Basic/NTLM headers/forms, FTP user/pass, SNMP community strings, POP/SMTP/IMAP creds, NTLMv1/v2 hashes, Kerberos hashes, and credit card numbers.
- **Execution Command:**
    ```Bash
    ./Pcredz -f demo.pcapng -t -v
    ```
    
> **Engagement Tip:** When performing internal network assessments, running a passive packet capture (e.g., using `tcpdump`) while performing other tasks can uncover unencrypted administrative traffic (like cleartext SNMP community strings or legacy FTP logins) without active port scanning.z`