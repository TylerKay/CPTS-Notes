# Windows Initial Enumeration (Manual PrivEsc Recon)

## Escalation Targets
Depending on system config and findings, escalation may land on one of:
1. **`NT AUTHORITY\SYSTEM`** (LocalSystem) — more privileged than local admin, runs most Windows services
2. **Built-in local Administrator account** — often not disabled, frequently reused across systems
3. **Another local account in the Administrators group** — same privileges as built-in admin
4. **A standard domain user in the local Administrators group**
5. **A domain admin who happens to be in the local Administrators group** — highly privileged in AD

## Why Enumeration Matters
Gaining situational awareness after initial shell access is essential — OS version, patch level, installed software, current privileges, and group memberships all shape the escalation path. Manual technique proficiency matters when tools can't be loaded (network restrictions, no internet, active protections).

> Reference: Windows commands cheat sheets are widely available for manual enumeration tasks.

## Key Data Points to Gather
- **OS name** — workstation vs. server, version (Win 7/10, Server 2008–2019) → indicates available tooling (e.g. PowerShell version) and possible public exploits.
- **Version/build** — specific public exploits may target specific Windows versions. ⚠️ Exploits can cause instability/crashes — use caution on production systems.
- **Running Services** — especially those running as `NT AUTHORITY\SYSTEM` or admin-level accounts; misconfigured/vulnerable ones = easy privesc wins.

---

## System Information

### Running Processes/Services
```cmd
tasklist /svc
```
- Learn standard processes (`smss.exe`, `csrss.exe`, `winlogon.exe`, `lsass.exe`, `svchost.exe`) to quickly spot **non-standard** ones.
- Example: a `FileZilla Server.exe` process stands out → check version for known vulns/misconfigs (e.g. FTP anonymous access).
- AV/EDR processes (e.g. `MsMpEng.exe` = Windows Defender) reveal protections to evade/bypass.

### Environment Variables
```cmd
set
```
- **PATH** — check for non-standard additions (e.g. Python, Java). If a PATH folder is **writable**, potential DLL injection vector.
  - ⚠️ Windows checks CWD first, then PATH left-to-right — a writable entry placed *before* `C:\Windows\System32` is more dangerous than one after.
- **HOMEDRIVE** — often an enterprise file share; browsing it may reveal sensitive shared directories (e.g. an "IT Directory" with credential spreadsheets).
- Roaming profiles mean planted startup items (`USERPROFILE\AppData\Microsoft\Windows\Start Menu\Programs\Startup`) execute wherever the user logs in next.

### Detailed System Config
```cmd
systeminfo
```
Key fields:
- **Hotfix(s)** — Google installed KBs to gauge patch timeline (may be hidden from non-admins)
- **System Boot Time / OS Version** — proxy for patch level; 6+ months uptime often = unpatched
- **Network Card(s)** — dual-homed indicator (though enterprises often grant multi-network access via firewall rules, not physical NICs)

**Alternative hotfix enumeration:**
```cmd
wmic qfe
```
```powershell
Get-HotFix | ft -AutoSize
```

### Installed Software
```cmd
wmic product get name
```
```powershell
Get-WmiObject -Class Win32_Product | select Name, Version
```
- Look for exploitable/outdated software.
- Found FileZilla/PuTTY/etc? → run **LaZagne** to check for stored credentials.
- Some installed software runs as a vulnerable service.

### Active Network Connections
```powershell
netstat -ano
```
- Reveals listening ports both locally and externally exposed.
- May surface a service **only bound to localhost** — exploitable once you have a local shell even if unreachable remotely.

---

## User & Group Information

### Logged-In Users
```cmd
query user
```
- Shows active/idle state and logon time — useful for targeting or for OPSEC awareness on evasive engagements.

### Current User Context
```cmd
echo %USERNAME%
```
- Always check first — you might already be SYSTEM-equivalent or have abusable privileges like `SeImpersonatePrivilege` (→ Juicy Potato) if running as a service account.

### Current User Privileges
```cmd
whoami /priv
```
- Enabled/disabled privileges directly inform available privilege-abuse escalation paths.

### Current User Group Membership
```cmd
whoami /groups
```
- Reveals inherited rights via groups; relevant for both local and AD-domain privilege context.

### All Local Users
```cmd
net user
```
- Look for naming patterns hinting at privilege (e.g. `bob` vs `bob_adm`) — test for credential reuse.
- Check accessible user profile dirs (Desktop/Documents/Downloads) for scripts with passwords, SSH keys, etc.

### All Local Groups
```cmd
net localgroup
```
- Non-standard groups hint at host purpose or reveal misconfigurations (e.g. Domain Users in local admin/RDP groups).

### Group Membership Details
```cmd
net localgroup administrators
```
- Occasionally reveals credentials/hints in group descriptions.
- May surface non-admin users who are members of a privileged group — a lead for privesc.

### Password Policy & Account Settings
```cmd
net accounts
```
- Lockout threshold/duration, password age/length settings — informs feasibility of password spraying without lockout risk.

---

## Key Takeaway
This is not exhaustive — enumeration tools (winPEAS, Seatbelt, etc.) cover far more data points automatically. But mastering these manual commands ensures full enumeration capability even in restricted, tool-blocked environments. Build a personal command cheat sheet from this list for quick reference during engagements.