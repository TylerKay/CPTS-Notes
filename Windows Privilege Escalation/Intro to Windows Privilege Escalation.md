# Introduction to Windows Privilege Escalation

## Goal
Elevate access to **Local Administrator** or **NT AUTHORITY\SYSTEM** (LocalSystem) — though sometimes escalating to just *another* local user is sufficient depending on the objective. This enables:
- Better persistence options
- Access to locally stored sensitive info
- Lateral movement / further network access

## Why Escalate Privileges?
1. Testing a client's gold image workstation/server build for flaws
2. Accessing a local resource (e.g. a database) requiring higher privilege
3. Gaining `NT AUTHORITY\SYSTEM` on a domain-joined machine as a foothold into AD
4. Obtaining credentials to move laterally or escalate further in the network

## Attack Surface Overview
Windows offers many privesc vectors, including:
- Abusing Windows **group** privileges
- Abusing Windows **user** privileges
- Bypassing **User Account Control (UAC)**
- Abusing weak **service/file permissions**
- Leveraging unpatched **kernel exploits**
- **Credential theft**
- **Traffic capture**
- ...and more

> Manual enumeration skill is essential — real engagements often involve locked-down environments (no internet, blocked USB, heavy firewalling) where tooling can't be loaded.

---

## Real-World Scenarios

### Scenario 1 — Overcoming Network Restrictions
- No internet access, blocked USB, network access control in place.
- Found a flaw: printer VLAN allowed outbound traffic on ports 80/443/445.
- Used manual enumeration to find a permissions flaw → performed a manual **LSASS memory dump**.
- Mounted an SMB share (hosted on attack machine) via the printer VLAN to exfil the LSASS dump.
- Used **Mimikatz offline** to extract a domain admin's NTLM hash → cracked it offline → accessed a domain controller.

### Scenario 2 — Pillaging Open Shares
- Locked-down, well-monitored environment with no obvious vulnerabilities.
- Found a wide-open file share hosting VM backups (`.VMDK`/`.VHDX` files).
- Mounted a `.VHDX` as a local drive on a Windows VM → browsed the filesystem.
- Extracted **SYSTEM, SAM, SECURITY** registry hives → moved to Linux attack box.
- Used `secretsdump.py` to extract the local admin password hash.
- Since the org used a **gold image**, this hash worked via **pass-the-hash** against nearly every Windows system in the environment.

### Scenario 3 — Hunting Credentials & Abusing Account Privileges
- Locked-down network, goal: access critical database servers.
- Standard domain user laptop, tools allowed to be loaded.
- Used **Snaffler** to hunt file shares → found `.sql` files with low-priv DB credentials.
- Connected to the DB with an MSSQL client → enabled `xp_cmdshell` → gained local command execution.
- Confirmed **`SeImpersonatePrivilege`** on the service account → leveraged **Juicy Potato** (custom compiled) for local privesc.
- Added a local admin user (not ideal, but reverse shell attempts failed) → remoted in and gained full control of the client's database.

---

## Why Privilege Escalation Happens
No single root cause, but common contributing factors:
- Insufficient personnel/budget for patching, vulnerability management, periodic self-assessments, continuous monitoring
- Deferred larger initiatives: workstation/server upgrades, file share audits (locking down directories, removing scripts/configs with embedded credentials)

---

## Lab Connectivity Notes

**Connect via FreeRDP:**
```bash
xfreerdp /v:<target_ip> /u:htb-student
```
- Expect self-signed cert warnings (`CERTIFICATE NAME MISMATCH`) — accept to proceed (`y`), then enter the provided password.

**Tools location on target hosts:** `C:\Tools`
- Where possible, practice uploading your own tools (via File Transfers techniques) or compiling tools yourself (e.g. via Visual Studio) rather than relying solely on pre-staged binaries.

---

## Key Takeaway
Windows privesc requires both **tool proficiency** and **manual enumeration skill** (PowerShell + cmd-line), since real engagements frequently involve restricted, tool-limited environments. Creative chaining across shares, credentials, VLANs, and privilege abuse (like `SeImpersonatePrivilege`) is often necessary to reach the objective.