# SeDebugPrivilege — Windows PrivEsc

## Background
- `SeDebugPrivilege` may be assigned to a user (via local/domain Group Policy: `Computer Settings > Windows Settings > Security Settings`) instead of adding them to Administrators — often for troubleshooting or app-debugging purposes.
- **By default, only Administrators** have this right, since it enables:
  - Capturing sensitive info from system memory
  - Accessing/modifying kernel and application structures
- Commonly assigned to **developers** debugging system components — should be granted sparingly, as it exposes access to critical OS internals.

### Recon Angle
- During internal pentests, cross-reference captured NTLMv2 hashes (via Responder/Inveigh) against likely high-value targets (e.g. developers) — they're more likely to have `SeDebugPrivilege`.
- This right isn't always visible via remote enumeration tools like **BloodHound**, so worth manually checking `whoami /priv` after RDP access with any obtained credentials, even without other elevated privileges.

### Confirming the Privilege
```cmd
whoami /priv
```
```
Privilege Name           Description        State
SeDebugPrivilege         Debug programs      Disabled
SeChangeNotifyPrivilege  Bypass traverse ... Enabled
```
- Note: shows as **Disabled** by default even when assigned — must be enabled programmatically (no native cmd/PowerShell toggle).

---

## Exploitation Path 1 — LSASS Memory Dump → Credential Theft

### Step 1 — Dump LSASS with ProcDump (Sysinternals)
```cmd
procdump.exe -accepteula -ma lsass.exe lsass.dmp
```
- LSASS stores logged-on user credentials in memory — a prime target.

### Step 2 — Process the dump with Mimikatz
```
mimikatz.exe

mimikatz # log
mimikatz # sekurlsa::minidump lsass.dmp
mimikatz # sekurlsa::logonpasswords
```
> **Tip:** Always run `log` first in Mimikatz to write output to a `.txt` file — especially valuable on servers with many cached credential sets.

**Result:** Exposes NTLM hashes (and sometimes cleartext passwords) for logged-on accounts, including potentially the **local administrator**. If reused across systems (common in large orgs), this enables **pass-the-hash** lateral movement.

### Alternative — No Tool Upload Needed (RDP-only access)
If tools can't be loaded on target but RDP access is available:
1. Open **Task Manager** → **Details** tab
2. Select `lsass.exe` → **Create dump file**
3. Download the resulting dump back to your attack machine
4. Process with Mimikatz as above

---

## Exploitation Path 2 — RCE as SYSTEM via Token Inheritance

### Concept
`SeDebugPrivilege` allows launching a child process that inherits/impersonates the token of a targeted **parent process**. Targeting a SYSTEM-owned process (e.g. `winlogon.exe`, `lsass.exe`) grants SYSTEM-level execution.

### Steps
**1. Transfer a PoC script** (e.g. `psgetsystem` — check GitHub for current usage):
```
https://github.com/decoder-it/psgetsystem
```

**2. Open an elevated PowerShell console** (run as admin, using credentials for the user with `SeDebugPrivilege`).

**3. Identify a SYSTEM-owned process PID:**
```powershell
tasklist
```
- Example target: `winlogon.exe` (PID 612) — known to run as SYSTEM.
- Alternative: use `Get-Process` to grab the PID of `lsass.exe` directly.

**4. Run the PoC targeting that PID:**
```powershell
[MyProcess]::CreateProcessFromParent(<system_pid>,<command_to_execute>,"")
```
> Note: the trailing blank third argument `""` is required for correct operation.

**Result:** Spawns `cmd.exe` (or specified command) running as `NT AUTHORITY\SYSTEM`.

### Adapting for Non-Interactive Access
If you don't have RDP/interactive access (e.g. command injection, webshell, reverse shell as the `SeDebugPrivilege` user), modify the PoC to instead:
- Return a **reverse shell as SYSTEM** to your attack host
- Execute an alternate command (e.g. **add a local admin user**)

---

## Key Takeaway
`SeDebugPrivilege` offers two strong escalation paths:
1. **Credential harvesting** via LSASS memory dump + Mimikatz (works even without tool upload, via Task Manager's built-in dump feature)
2. **Direct SYSTEM code execution** by inheriting a SYSTEM process's token (e.g. via `psgetsystem`-style PoCs)

Both are valuable fallbacks — especially path 2 when LSASS dumping doesn't yield usable credentials, or when only non-interactive RCE is available.