# Credential Hunting — Windows

Credentials found during enumeration can lead to local admin access, AD domain footholds, or further privilege escalation within the domain. Check all of the following locations.

---

## 1. Application Configuration Files

Apps frequently store credentials in cleartext config files against best practices.

```powershell
findstr /SIM /C:"password" *.txt *.ini *.cfg *.config *.xml
```

**Key file to check — IIS web.config:**
```
C:\inetpub\wwwroot\web.config
```
May contain DB credentials, API keys, or service account passwords. Search recursively — multiple copies may exist in other locations.

---

## 2. Chrome Dictionary Files

Users may type passwords into browser-based apps/email clients, causing the spell checker to flag them. Adding them to the custom dictionary stores them in plaintext:

```powershell
gc 'C:\Users\<username>\AppData\Local\Google\Chrome\User Data\Default\Custom Dictionary.txt' | Select-String password
```

---

## 3. Unattended Installation Files

Windows unattended installation files can contain auto-logon settings or additional accounts with passwords stored in **plaintext or base64**:

```
C:\Windows\Panther\unattend.xml
C:\Windows\Panther\Unattend\unattend.xml
C:\Windows\system32\sysprep.inf
C:\Windows\system32\sysprep\sysprep.xml
```

Example leak:
```xml
<AutoLogon>
    <Password>
        <Value>local_4dmin_p@ss</Value>
        <PlainText>true</PlainText>
    </Password>
    <Username>Administrator</Username>
</AutoLogon>
```
These should be deleted post-installation but are often left behind on dev/staging images.

---

## 4. PowerShell History File

PowerShell 5.0+ (Windows 10+) saves command history to:
```
C:\Users\<username>\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
```
Commands that pass credentials on the command line (e.g. `wevtutil`, `net use`, etc.) are saved here in plaintext.

**Get current user's history path:**
```powershell
(Get-PSReadLineOption).HistorySavePath
```

**Read current user's history:**
```powershell
gc (Get-PSReadLineOption).HistorySavePath
```

**Read history for ALL users (useful post-escalation):**
```powershell
foreach($user in ((ls C:\users).fullname)){cat "$user\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadline\ConsoleHost_history.txt" -ErrorAction SilentlyContinue}
```

**Example credential leak in history:**
```
wevtutil qe Application "..." /u:WEB02\administrator /p:5erv3rAdmin! /r:WEB02
```

> **Note:** Re-check all history files after escalating privileges — some may have been unreadable before.

---

## 5. PowerShell Credential Objects (Encrypted XML)

Sysadmins often store credentials as encrypted XML via `Export-Clixml` for use in automation scripts. Protected by **DPAPI** — normally only decryptable by the **same user on the same machine** that created them.

**Example automation script pattern:**
```powershell
# Credential was saved with:
# Get-Credential | Export-Clixml -Path 'C:\scripts\pass.xml'

$encryptedPassword = Import-Clixml -Path 'C:\scripts\pass.xml'
$decryptedPassword = $encryptedPassword.GetNetworkCredential().Password
```

**Decrypt if running as the user who created it:**
```powershell
$credential = Import-Clixml -Path 'C:\scripts\pass.xml'
$credential.GetNetworkCredential().username
$credential.GetNetworkCredential().password
```
→ Returns cleartext username and password.

---

## Quick Reference — Where to Look

| Location | What to Find |
|---|---|
| `*.txt`, `*.ini`, `*.cfg`, `*.config`, `*.xml` | Cleartext passwords in app configs |
| `C:\inetpub\wwwroot\web.config` | IIS credentials |
| Chrome Custom Dictionary | Accidentally stored passwords |
| `unattend.xml` / `sysprep.xml` | Auto-logon credentials, local account passwords |
| PowerShell history (`ConsoleHost_history.txt`) | CLI commands with inline credentials |
| `*.xml` credential exports | DPAPI-encrypted but decryptable as the owning user |

---

## Key Takeaway
Credential hunting should be part of every Windows enumeration pass — not an afterthought. Run `findstr` broadly, check PowerShell history for all users post-escalation, and hunt for credential XML files in script directories. A single plaintext password can pivot directly to Domain Admin.