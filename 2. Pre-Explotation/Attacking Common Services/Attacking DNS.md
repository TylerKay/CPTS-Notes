# Attacking DNS (Domain Name System)
## Overview
- **Protocol Function:** Translates human-readable domain names (e.g., `hackthebox.com`) into numerical IP addresses (e.g., `104.17.42.72`).
- **Ports & Protocol:** Primarily uses UDP/53, but relies on TCP/53 for zone transfers or oversized packets exceeding single UDP limits.
- **Enumeration (Nmap):**
    Bash
    ```
    nmap -p53 -Pn -sV -sC <target_ip>
    ```
## DNS Zone Transfers (AXFR)
- **Concept:** DNS servers use zone transfers to replicate database portions to other nameservers. Misconfigured servers allow unauthenticated users to dump the entire namespace.
- **Exploitation (`dig`):**
    Bash
    ```
    dig AXFR @<nameserver> <domain>
    ```
- **Enumeration Tool (`Fierce`):**
    Bash
    ```
    fierce --domain <domain>
    ```

## Subdomain Enumeration & Domain Takeovers
### 1. Subdomain Enumeration Tools
- **Subfinder:** Scrapes public sources (e.g., DNSdumpster, AlienVault).
    Bash
    ```
    ./subfinder -d <domain> -v
    ```
- **Subbrute:** Useful for internal networks or offline environments via custom resolvers.
    Bash
    ```
    ./subbrute.py <domain> -s ./names.txt -r ./resolvers.txt
    ```
### 2. Subdomain Takeover

- **Mechanism:** Occurs when a subdomain points to a third-party service (e.g., AWS S3, GitHub, Azure) via a CNAME record, but the underlying service resource has been deleted or expired. Attackers can claim the dangling resource to control the subdomain.
- **Verification (`host`):**
    Bash
    ```
    host <subdomain>
    ```

## DNS Spoofing (Cache Poisoning & Local MitM)

- **Concept:** Redirecting traffic by tampering with DNS records or feeding false DNS responses to victims.
- **Local Network Attack (Ettercap):**
    1. Configure target mappings in `/etc/ettercap/etter.dns`:
        Plaintext
        ```
        <target_domain>      A   <attacker_ip>
        *.<target_domain>    A   <attacker_ip>
        ```
        
    2. Launch Ettercap, scan for live hosts, set **Target 1** (victim IP) and **Target 2** (default gateway IP), and activate the `dns_spoof` plugin under **Plugins > Manage Plugins**.