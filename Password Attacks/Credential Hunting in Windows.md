## Overview

Credential hunting is the process of searching a compromised Windows target (via GUI or CLI) through file systems, application data, and memory to discover cleartext or weakly protected credentials. The approach should always be tailored to the role of the system (e.g., an IT administrator workstation vs. a standard user desktop or server).

## High-Level Methodology

1. **Context Analysis:** Determine what the system is used for (e.g., an IT admin workstation likely interacts with administrative tools, scripts, and remote management software).
2. **Targeted Search (CLI/GUI):** Use OS search features or command-line pattern matching with specific high-value keywords.
3. **Automated Harvesting:** Run automated tools like **LaZagne** to extract insecurely stored application, browser, and configuration credentials.
4. **Inspect High-Value Repositories:** Check common misconfiguration storage paths (e.g., configuration files, script shares, unattended installation files).
## Key Terms to Search For

When performing searches across files and configurations, look for variations of these keywords:

- `password`, `pwd`, `passphrase`
- `credentials`, `creds`, `login`
- `username`, `user account`, `users`
- `keys`, `passkeys`
- `config`, `configuration`
- `dbpassword`, `dbcredential`
## Tools and Techniques
### 1. Windows Search (GUI)

- Use the built-in search bar in Windows Explorer or the Start Menu to quickly scan settings and file systems for target files containing your search keywords.
### 2. LaZagne (Automated Credential Recovery)
LaZagne targets third-party and native applications that insecurely store passwords.
- **Execution Command:**
    ```PowerShell
    C:\Users\bob\Desktop> start LaZagne.exe all
    ```
    
- **Key Modules:**
    - `browsers`: Extracts stored credentials from Chrome, Firefox, Edge, Opera (encrypted data can often be decrypted using secondary tools).
    - `chats`: Extracts passwords from chat applications (e.g., Skype).
    - `emails`: Searches mail clients (Outlook, Thunderbird).
    - `sysadmin`: Extracts credentials from admin tools like WinSCP and OpenVPN.
    - `windows`: Targets LSA secrets and Credential Manager.
    - `wifi`: Dumps saved Wi-Fi credentials.
    - `memory`: Targets credentials in memory (KeePass, LSASS).
### 3. Command-Line Pattern Matching (`findstr`)

Use `findstr` to recursively search for password patterns across common configuration and script formats:
```PowerShell
C:\> findstr /SIM /C:"password" *.txt *.ini *.cfg *.config *.xml *.git *.ps1 *.yml
```

## High-Value Storage Locations to Check

Beyond local user directories, always investigate these common locations for exposed credentials:
- **SYSVOL Share:** Passwords or scripts stored in Group Policy Objects or startup scripts.
- **IT Shares & Web Shares:** Plaintext configuration files (`web.config` on dev machines).
- **Unattended Installations:** `unattend.xml` files left over from system deployment.
- **Active Directory:** User or computer account description fields.
- **Database & Document Files:** Files named `pass.txt`, `passwords.docx`, or `passwords.xlsx` on user shares or SharePoint.
- **Password Managers:** KeePass databases (`.kdbx`) if master passwords can be brute-forced or guessed.

> **Engagement Tip:** Always tailor your search paths based on the target environment. On a workstation, focus on user profiles, browser data, and local admin tools; on a server or Domain Controller, prioritize configuration files, SYSVOL, and shared repositories.