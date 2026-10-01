## Overview & Assessment Setup

The initial internal Active Directory (AD) enumeration phase begins by establishing a foothold or gathering baseline information within the target network (`172.16.5.0/23`). In this scenario, the assessment parameters include:
* **Approach:** Grey box testing with no prior detailed network map.
* **Credentials:** Unauthenticated standpoint initially, backed by a standard domain user account (`htb-student`) for the Windows attack host.
* **Execution Style:** Non-evasive testing.
* **Environment Setup:** Custom pentest Linux VM within the internal network with reverse SSH access, alongside a Windows host for tool loading.

---

## Key Data Points to Discover

* **Active Directory Users:** Valid accounts targeted for subsequent password spraying.
* **Domain-Joined Computers:** Identification of Domain Controllers (DCs), file servers, SQL servers, web servers, and Exchange mail servers.
* **Key Services:** Kerberos, NetBIOS, LDAP, and DNS.
* **Vulnerable Hosts & Services:** Outdated operating systems or misconfigurations that allow for quick wins.

---

## Methodology & Step-by-Step Process

### Step 1: Passive Traffic Analysis (Listening to the Wire)
* **Action:** Capture and analyze local network traffic using tools like Wireshark, `tcpdump`, or passive monitoring. Look for ARP requests/replies, mDNS, and broadcast traffic to map out active IP addresses.
* **Verification:** Correlate detected IP addresses (e.g., `172.16.5.5`, `172.16.5.25`, `172.16.5.50`) and hostname broadcasts (such as `ACADEMY-EA-WEB01`) to construct an initial target list.

### Step 2: Passive Analysis via Responder
* **Action:** Run Responder in **Analyze mode** (`-A`) on the local network interface to passively listen for LLMNR, NBT-NS, and mDNS traffic without sending poisoned packets.
* **Verification:** Identify unique hosts and DNS hostnames appearing in the traffic stream to expand the internal target inventory.

### Step 3: Active ICMP Discovery Sweep
* **Action:** Execute an active ping sweep across the target CIDR range using `fping` to check for live hosts quickly and efficiently.
```
 bash
  fping -asgq 172.16.5.0/23
```


- **Verification:** Compile the list of live IP addresses responding to ICMP echoes to distinguish active systems from unreachable targets.
    

### Step 4: Service Port Enumeration via Nmap
- **Action:** Perform targeted Nmap scans against the discovered live hosts to identify open ports, operating systems, and critical domain services (DNS, SMB, LDAP, Kerberos, RPC).
    Bash
    ```
    sudo nmap -v -A -iL hosts.txt -oN /home/htb-student/Documents/host-enum
    ```
    
- **Verification:** Analyze output flags and service banners (e.g., detecting Domain Controllers like `ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL` or legacy hosts running Windows Server 2008 R2) to prioritize targets for further enumeration. _Always confirm explicit client permission before actively scanning or testing legacy/industrial equipment._

```
sudo nmap -A -v -Pn -T5 -oG ./nmapOutput 172.16.5.0/23
```
    

### Step 5: Internal AD Username Enumeration via Kerbrute

- **Action:** Use Kerbrute to perform stealthy username enumeration against the primary Domain Controller via Kerberos Pre-Authentication.
    
    Bash
    ```
    kerbrute userenum -d INLANEFREIGHT.LOCAL --dc 172.16.5.5 jsmith.txt -o valid_ad_users
    ```
    
- **Verification:** Review the output file (`valid_ad_users`) to ensure a verified list of active domain user accounts is generated for subsequent password spraying or credential-stuffing attacks.