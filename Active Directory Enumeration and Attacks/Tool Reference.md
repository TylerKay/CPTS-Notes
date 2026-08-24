# Active Directory Enumeration & Attack — Tool Reference

## Enumeration Tools

| Tool | Description |
|---|---|
| **PowerView** | PowerShell tool for enumerating AD environments — users, groups, trusts, ACLs, and more |
| **SharpView** | C# port of PowerView |
| **BloodHound** | GUI tool using graph theory to visualize AD attack paths and privilege escalation routes |
| **BloodHound.py** | Python-based BloodHound ingestor (Impacket-based); runs from non-domain-joined Linux hosts |
| **Kerbrute** | Go tool using Kerberos Pre-Authentication for AD user enumeration, password spraying, and brute-forcing |
| **Impacket toolkit** | Python collection for interacting with network protocols — includes many AD enumeration/attack scripts |
| **CrackMapExec (CME)** | Enumeration, attack, and post-exploitation toolkit; abuses SMB, WMI, WinRM, MSSQL |
| **enum4linux** | Enumerate information from Windows and Samba systems |
| **enum4linux-ng** | Rework of enum4linux with different functionality |
| **ldapsearch** | Built-in interface for interacting with LDAP |
| **windapsearch** | Python script for AD user/group/computer enumeration via LDAP queries |
| **rpcclient** | Samba suite tool for AD enumeration tasks via remote RPC service |
| **rpcinfo** | Query RPC program status or enumerate available RPC services on a remote host |
| **rpcdump.py** | Impacket RPC endpoint mapper |
| **smbmap** | SMB share enumeration across a domain |
| **adidnsdump** | Enumerate and dump DNS records from a domain (similar to DNS Zone Transfer) |
| **LAPSToolkit** | PowerShell functions leveraging PowerView to audit/attack environments using Microsoft LAPS |
| **Snaffler** | Find credentials and interesting files on AD computers with accessible file shares |
| **Active Directory Explorer** | AD viewer/editor; browse AD database, view object properties, save/compare offline snapshots |
| **PingCastle** | Audit AD security posture using a risk assessment/maturity framework |
| **Group3r** | Audit and find misconfigurations in AD Group Policy Objects (GPOs) |
| **ADRecon** | Extract AD environment data — outputs to Excel with summary views for analysis |
| **setspn.exe** | Add, read, modify, and delete Service Principal Names (SPNs) for AD service accounts |
| **lookupsid.py** | Impacket SID brute-forcing tool |

---

## Credential Attacks & Hash Operations

| Tool | Description |
|---|---|
| **Responder** | Poison LLMNR, NBT-NS, and MDNS to capture NetNTLM hashes |
| **Inveigh.ps1** | PowerShell tool for network spoofing and poisoning attacks (similar to Responder) |
| **C# Inveigh (InveighZero)** | C# Inveigh with semi-interactive console for managing captured hashes |
| **Hashcat** | Hash cracking and password recovery |
| **Mimikatz** | Pass-the-hash, plaintext password extraction, Kerberos ticket extraction from memory |
| **secretsdump.py** | Remotely dump SAM and LSA secrets from a host |
| **gpp-decrypt** | Extract usernames and passwords from Group Policy Preferences files |
| **DomainPasswordSpray.ps1** | PowerShell password spraying tool against domain users |

---

## Kerberos Attacks

| Tool | Description |
|---|---|
| **Rubeus** | C# tool for Kerberos abuse (roasting, ticket extraction, pass-the-ticket, etc.) |
| **GetUserSPNs.py** | Impacket tool for finding SPNs tied to normal user accounts (Kerberoasting) |
| **GetNPUsers.py** | Impacket tool for ASREPRoasting — list/obtain AS-REP hashes for users without Kerberos pre-auth required |
| **ticketer.py** | Create and customize TGT/TGS tickets — Golden Ticket creation, child-to-parent trust attacks |
| **gettgtpkinit.py** | Manipulate certificates and TGTs |
| **getnthash.py** | Use existing TGT to request a PAC for the current user via U2U |
| **raiseChild.py** | Automated child-to-parent domain privilege escalation (Impacket) |

---

## Lateral Movement & Execution

| Tool | Description |
|---|---|
| **psexec.py** | Impacket Psexec-like semi-interactive shell |
| **wmiexec.py** | Impacket command execution over WMI |
| **evil-winrm** | Interactive shell over WinRM protocol |
| **mssqlclient.py** | Impacket tool for interacting with MSSQL databases |
| **smbserver.py** | Simple SMB server for file transfers within a network |
| **ntlmrelayx.py** | Impacket SMB relay attacks |

---

## Exploit-Specific Tools

| Tool | CVE | Description |
|---|---|---|
| **noPac.py** | CVE-2021-42278 + CVE-2021-42287 | Impersonate Domain Admin from a standard domain user account |
| **CVE-2021-1675.py** | CVE-2021-1675 | PrintNightmare Python PoC |
| **PetitPotam.py** | CVE-2021-36942 | Coerce Windows hosts to authenticate to attacker machines via MS-EFSRPC |