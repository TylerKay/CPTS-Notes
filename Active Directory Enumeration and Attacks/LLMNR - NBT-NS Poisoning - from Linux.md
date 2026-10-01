## Overview & Purpose
LLMNR and NBT-NS poisoning are Man-in-the-Middle (MITM) techniques used during internal penetration tests to capture NetNTLMv1/v2 password hashes. By intercepting failed DNS lookups, an attacker can spoof name resolution services, force victim machines to authenticate against a rogue host, and capture authentication hashes for offline cracking or SMB relay attacks to gain an initial foothold.

---
![[Pasted image 20260905143827.png|513]]
## Core Concepts

* **LLMNR (Link-Local Multicast Name Resolution):** A protocol based on DNS formats allowing hosts on the same local link to perform name resolution when DNS fails. Uses **UDP port 5355**.
* **NBT-NS (NetBIOS Name Service):** Identifies systems on a local network by their NetBIOS name when DNS/LLMNR fails. Uses **UDP port 137**.
* **The Vulnerability:** When these protocols are used, *any* host on the network can respond to broadcast queries. Attackers can reply authoritatively, tricking the victim host into sending an authentication request containing a username and NetNTLMv1/v2 password hash.

---

## Common Poisoning Tools

| Tool | Description |
| :--- | :--- |
| **Responder** | A purpose-built Python tool designed to poison LLMNR, NBT-NS, and MDNS, featuring built-in rogue servers (SMB, HTTP, WPAD, etc.). |
| **Inveigh** | A cross-platform MITM tool written in C# and PowerShell used for spoofing and poisoning. |
| **Metasploit** | Contains built-in auxiliary scanners and spoofing modules for network poisoning. |

---

## Methodology & Step-by-Step Process

Tools such as Responder are great for establishing a foothold that we can later expand upon through further enumeration and attacks.
### Step 1: Passive Reconnaissance (Analyze Mode)
* **Action:** Run Responder in analysis mode first to observe network traffic without sending poisoned responses.
```bash
  sudo responder -I ens224 -A
```

- **Verification:** Monitor traffic for active LLMNR/NBT-NS/mDNS queries to ensure the network is active before launching the attack.
    

### Step 2: Configure and Launch Responder

- **Action:** Start Responder with active poisoning, WPAD rogue proxy server (`-w`), and OS fingerprinting (`-f`) flags enabled. Ensure required ports (such as UDP 137, 5355, and TCP 80, 445) are free.
    ```Bash
    sudo responder -I ens224 -wf
    ```
    
- **Verification:** Observe the console output for incoming requests and captured NetNTLMv2 hashes.
    

### Step 3: Locate and Extract Captured Hashes

- **Action:** Check the Responder log directory for generated hash files per host/protocol.
    ```Bash
    ls /usr/share/responder/logs/
    ```
- **Verification:** Confirm files matching formats like `SMB-NTLMv2-SSP-<IP>.txt` contain valid NetNTLMv2 hash strings.
    

### Step 4: Offline Hash Cracking with Hashcat

- **Action:** Feed the captured NetNTLMv2 hash into Hashcat using mode `5600` alongside a wordlist (e.g., `rockyou.txt`) to crack weak passwords offline.
    ```Bash
    hashcat -m 5600 <hash_file> /usr/share/wordlists/rockyou.txt
    ```
    
- **Verification:** Check Hashcat output for a **Cracked** status to retrieve the cleartext password (e.g., matching a user account like `FOREND`), providing a valid credentialed foothold for subsequent domain enumeration.