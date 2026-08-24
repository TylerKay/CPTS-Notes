Beyond config files and PowerShell history, credentials hide in many unexpected places. In AD environments, use [Snaffler](https://github.com/SnaffCon/Snaffler) to crawl network shares for interesting extensions (`.kdbx`, `.vmdk`, `.vhdx`, `.ppk`, etc.) automatically. Manual techniques below cover what tools may miss.

---

## Manual File System Searches

**Search file contents for "password" (cmd):**
```cmd
cd c:\Users\htb-student\Documents & findstr /SI /M "password" *.xml *.ini *.txt
```
```cmd
findstr /si password *.xml *.ini *.txt *.config
```
```cmd
findstr /spin "password" *.*
```

**Search file contents (PowerShell):**
```powershell
select-string -Path C:\Users\htb-student\Documents\*.txt -Pattern password
```

**Search by filename/extension (cmd):**
```cmd
dir /S /B *pass*.txt == *pass*.xml == *pass*.ini == *cred* == *vnc* == *.config*
```
```cmd
where /R C:\ *.config
```

**Search by extension (PowerShell):**
```powershell
Get-ChildItem C:\ -Recurse -Include *.rdp, *.config, *.vnc, *.cred -ErrorAction Ignore
```

---

## Sticky Notes

Users frequently save passwords in Windows Sticky Notes without realizing it stores data in a SQLite database — not a text file.

**Database location:**
```
C:\Users\<user>\AppData\Local\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\plum.sqlite
```

**Query with PowerShell + PSSQLite module:**
```powershell
Set-ExecutionPolicy Bypass -Scope Process
Import-Module .\PSSQLite.psd1
$db = 'C:\Users\<user>\AppData\Local\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\plum.sqlite'
Invoke-SqliteQuery -Database $db -Query "SELECT Text FROM Note" | ft -wrap
```

**Alternative — copy files to attack box and use strings:**
```bash
strings plum.sqlite-wal
```
Copy all three files (`plum.sqlite`, `plum.sqlite-shm`, `plum.sqlite-wal`) and open with [DB Browser for SQLite](https://sqlitebrowser.org/):
```sql
select Text from Note;
```
Can also be done remotely via WinRM.

---

## Network Share Hunting

In AD environments, employee home folders on file shares (e.g. `\\FILE01\users\bjones`) often have overly permissive ACLs — all Domain Users readable. Users frequently store sensitive data in these folders unaware they're network-accessible. Common finds:

- `.kdbx` (KeePass databases)
- `.vmdk` / `.vhdx` (virtual hard drives — mount and extract local admin hashes)
- `.ppk` (PuTTY SSH private keys)
- Excel/Word documents, OneNote notebooks with embedded credentials
- `passwords.txt` or similar

---

## Other High-Value File Locations

```
%SYSTEMDRIVE%\pagefile.sys
%WINDIR%\debug\NetSetup.log
%WINDIR%\repair\sam
%WINDIR%\repair\system
%WINDIR%\repair\software
%WINDIR%\repair\security
%WINDIR%\iis6.log
%WINDIR%\system32\config\AppEvent.Evt
%WINDIR%\system32\config\SecEvent.Evt
%WINDIR%\system32\config\default.sav
%WINDIR%\system32\config\security.sav
%WINDIR%\system32\config\software.sav
%WINDIR%\system32\config\system.sav
%WINDIR%\system32\CCM\logs\*.log
%USERPROFILE%\ntuser.dat
%USERPROFILE%\LocalS~1\Tempor~1\Content.IE5\index.dat
%WINDIR%\System32\drivers\etc\hosts
C:\ProgramData\Configs\*
C:\Program Files\Windows PowerShell\*
```

---

## Key Takeaway
Enumeration scripts catch most of these, but manual knowledge is essential for restricted environments and for finding files scripts don't include. A single password found on a share has led to initial access or full domain compromise on many real engagements — treat file-based credential hunting as a high-priority step, not an afterthought.