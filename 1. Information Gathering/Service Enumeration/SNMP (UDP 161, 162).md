# SNMP (UDP 161, 162)

---

## Overview

`Simple Network Management Protocol` (`SNMP`) was created to **monitor network devices** — and can also handle configuration tasks / change settings remotely. SNMP-enabled hardware includes routers, switches, servers, IoT devices, and more.

|**Port**|**Direction**|**Purpose**|
|---|---|---|
|`UDP 161`|Client → Server|Requests (GET) and control commands (SET) via agents — set values, change options/settings|
|`UDP 162`|Server → Client|**Traps**: unsolicited data packets sent when a specific event occurs on the server-side|

Unlike classical client-server communication (client always actively requests), traps let the server *push* notifications without being asked.

## MIB & OID

For client/server to exchange values, every SNMP object needs a unique address known to both sides:

- **MIB** (`Management Information Base`) — independent format for storing device information; a text file listing all queryable SNMP objects of a device in a standardized tree hierarchy. Written in ASN.1-based ASCII. Each entry contains at least one **OID** with its unique address, name, type, access rights, and description.
	- ⚠️ MIBs contain **no data** — they explain *where* to find which information, what the return values look like, and which data type is used.
- **OID** (`Object Identifier`) — a node in a hierarchical namespace, identified by a dot-notation sequence of integers (e.g. `.1.3.6.1.2.1.1.5.0`). The longer the chain, the more specific the information. Many nodes are just references to nodes below them. Many MIB→OID mappings are searchable in the Object Identifier Registry.

## Versions

|**Version**|**Security**|**Notes**|
|---|---|---|
|**v1**|❌ No authentication, ❌ no encryption|Anyone on the network can read/modify data; all plain text. Still common in small networks.|
|**v2c** ("community-based")|❌ Same as v1|Extended functionality; community string transmitted in **plain text**. Still widely deployed.|
|**v3**|✅ Username/password auth, ✅ transmission encryption (pre-shared key)|Much higher security, but also much higher configuration complexity — the main reason many orgs stay on v2c.|

#### Community Strings

Community strings act as **passwords** deciding whether requested information may be viewed. Because migrating to v3 is complex while services must stay active, many organizations remain on v2 — meaning community strings cross the network unencrypted and **can be intercepted and read** every time they're sent.

## Default Configuration

Daemon config defines IP addresses, ports, MIBs, OIDs, authentication, and community strings:

```
tylapcheong@htb[/htb]$ cat /etc/snmp/snmpd.conf | grep -v "#" | sed -r '/^\s*$/d'
```

```
sysLocation    Sitting on the Dock of the Bay
sysContact     Me <me@example.org>
sysServices    72
master  agentx
agentaddress  127.0.0.1,[::1]
view   systemonly  included   .1.3.6.1.2.1.1
view   systemonly  included   .1.3.6.1.2.1.25.1
rocommunity  public default -V systemonly
rocommunity6 public default -V systemonly
rouser authPrivUser authpriv -V systemonly
```

Note the default read-only community string `public`. All available options are described in the manpage — worth labbing this on a VM.

## Dangerous Settings

|**Setting**|**Description**|
|---|---|
|`rwuser noauth`|Provides access to the full OID tree **without authentication**.|
|`rwcommunity <community string> <IPv4 address>`|Provides access to the full OID tree **regardless of where the requests were sent from**.|
|`rwcommunity6 <community string> <IPv6 address>`|Same as `rwcommunity`, but for IPv6.|

## Footprinting the Service

Three main tools:
- `snmpwalk` – queries OIDs with their information (full walk)
- `onesixtyone` – brute-forces community string names (admins can name them arbitrarily; strings may be bound to specific sources, so identification can take time)
- `braa` – brute-forces individual OIDs once a community string is known

#### SNMPwalk

```
tylapcheong@htb[/htb]$ snmpwalk -v2c -c public 10.129.14.128
```

With a working community string on v1/v2c (no auth required), a misconfigured service dumps internal system information:

|**OID suffix**|**Reveals**|
|---|---|
|`.1.3.6.1.2.1.1.1.0`|Kernel/OS version (`Linux htb 5.11.0-34-generic ... x86_64`)|
|`.1.3.6.1.2.1.1.4.0`|Contact email (`mrb3n@inlanefreight.htb`) → usernames/domain intel|
|`.1.3.6.1.2.1.1.5.0`|Hostname (`htb`)|
|`.1.3.6.1.2.1.1.6.0`|Location string|
|`.1.3.6.1.2.1.25.1.4.0`|Boot/kernel cmdline incl. disk UUID|
|`.1.3.6.1.2.1.25.6.3.1.2.*`|**Full list of installed packages** (software inventory → exploit matching)|

#### OneSixtyOne — Community String Bruteforce

```
tylapcheong@htb[/htb]$ sudo apt install onesixtyone
tylapcheong@htb[/htb]$ onesixtyone -c /opt/useful/seclists/Discovery/SNMP/snmp.txt 10.129.14.128

Scanning 1 hosts, 3220 communities
10.129.14.128 [public] Linux htb 5.11.0-37-generic ...
```

- When community strings are bound to specific IPs they're often named after the **hostname**, sometimes with symbols added to hinder guessing.
- In large networks (100+ servers) the names follow a **pattern** → build custom wordlists with rules using `crunch`.

#### Braa — OID Bruteforce

Syntax: `braa <community string>@<IP>:.1.3.6.*`

```
tylapcheong@htb[/htb]$ sudo apt install braa
tylapcheong@htb[/htb]$ braa public@10.129.14.128:.1.3.6.*
```

Returns OID:value pairs rapidly (with response times), e.g. sysDescr, contact, hostname — useful for enumerating large OID trees quickly once the community string is known.

## Workflow Cheat Sheet

1. Port scan for UDP 161 (SNMP is UDP — easy to miss with TCP-only scans!)
2. Bruteforce community strings → `onesixtyone -c <wordlist> <IP>`
3. Full enumeration → `snmpwalk -v2c -c <string> <IP>`
4. Fast targeted OID brute-force → `braa <string>@<IP>:.1.3.6.*`
5. Harvest: OS/kernel version, hostname, contact emails (usernames!), location, installed packages → map software versions to public exploits
