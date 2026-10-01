
This document covers methods for pulling Active Directory domain password policies from both **Linux** and **Windows** attack hosts (with and without credentials), followed by an analytical breakdown of how to evaluate a policy for password spraying.

### Phase 1: Credentialed & Unauthenticated Enumeration from Linux

#### 1. Credentialed Enumeration (CrackMapExec)

If valid domain credentials are available, extract the password policy remotely:
```Bash

crackmapexec smb 172.16.5.5 -u avazquez -p Password123 --pass-pol
```

#### 2. Unauthenticated SMB NULL Sessions

Legacy or misconfigured Domain Controllers may permit anonymous/NULL sessions, allowing retrieval of domain information and policies without credentials.

- **Using `rpcclient`:**
    ```Bash
    rpcclient -U "" -N 172.16.5.5
    rpcclient $> querydominfo 
    rpcclient $> getdompwinfo
    ```
    
- **Using `enum4linux` / `enum4linux-ng`:**
    ```Bash
    enum4linux -P 172.16.5.5
    enum4linux-ng -P 172.16.5.5 -oA ilfreight
    ```
    
| Tool      | Ports                                             |
| --------- | ------------------------------------------------- |
| nmblookup | 137/UDP                                           |
| nbtstat   | 137/UDP                                           |
| net       | 139/TCP, 135/TCP, TCP and UDP 135 and 49152-65535 |
| rpcclient | 135/TCP                                           |
| smbclient | 445/TCP                                           |
#### 3. LDAP Anonymous Bind

If the domain permits anonymous LDAP queries, extract password policy attributes via `ldapsearch`:

```Bash
ldapsearch -h 172.16.5.5 -x -b "DC=INLANEFREIGHT,DC=LOCAL" -s sub "*" | grep -m 1 -B 10 pwdHistoryLength
```

### Phase 2: Enumeration from Windows Hosts

#### 1. Built-in Windows Commands
When operating from a Windows host without third-party tool transfer capability:
- **Establish a NULL Session:**
    
    ```DOS
    net use \\DC01\ipc$ "" /u:""
    ```
    
- **Query Domain Accounts and Policy:**
    ```DOS
    net accounts
    ```

#### 2. PowerShell Utilities (PowerView)
If authenticated within a PowerShell session:

```PowerShell
Import-Module .\PowerView.ps1
Get-DomainPolicy
```

### Phase 3: Policy Analysis & Strategic Takeaways

|**Policy Attribute**|**Sample Value**|**Spraying Impact & Security Risk**|
|---|---|---|
|**Minimum Password Length**|8 Characters|Weak; permits common default strings like `Welcome1` or `Password1`.|
|**Account Lockout Threshold**|5 Attempts|Allows short multi-attempt windows; safety buffer dictates limiting attempts to 2-3 per window.|
|**Lockout Duration / Reset**|30 Minutes|Accounts auto-unlock after 30 minutes, lowering catastrophic lockout risk.|
|**Password Complexity**|Enabled (3/4 criteria)|Requires uppercase, lowercase, numbers, or symbols (e.g., `Welcome1` satisfies this).|

#### Safe Spraying Rules of Thumb
- **When Policy is Known:** Spray 2–3 common passwords while pacing attempts safely below the lockout threshold, respecting the reset window.
- **When Policy is Unknown:** Exercise extreme caution. Restrict testing to 1–2 high-probability attempts (or a single "hail mary" attempt) and wait at least 1 hour between attempts, or coordinate directly with the client. Avoid becoming the tester who locks out production accounts.