
This document outlines the step-by-step methodology for performing LLMNR and NBT-NS poisoning from a Windows host using the **Inveigh** tool (both PowerShell and C# versions), alongside remediation and detection strategies (MITRE ATT&CK ID: T1557.001).

### Phase 1: Tool Selection & Overview

Inveigh functions similarly to Responder but is natively written in PowerShell and C# (`InveighZero`), making it ideal when operating from a Windows attack host or pivot point. It listens across multiple protocols (IPv4/IPv6, LLMNR, DNS, mDNS, NBNS, DHCPv6, ICMPv6, HTTP, HTTPS, SMB, LDAP, WebDAV, Proxy Auth).

### Phase 2: Execution & Spoofing Setup

#### 1. Using the PowerShell Version

Import the module and inspect available parameters if necessary:
```PowerShell
Import-Module .\Inveigh.ps1
(Get-Command Invoke-Inveigh).Parameters
```

Initiate spoofing with LLMNR and NBNS enabled, outputting directly to the console and writing results to a file:
```PowerShell
Invoke-Inveigh Y -NBNS Y -ConsoleOutput Y -FileOutput Y
```

#### 2. Using the C# Version (InveighZero)

Alternatively, execute the compiled C# binary with default options:
```PowerShell
.\Inveigh.exe
```

### Phase 3: Interacting with Captured Hashes

1. **Access the Interactive Console:** While the tool is running, press the `ESC` key to enter the Inveigh interactive console.
    
2. **Review Available Commands:** Type `HELP` to view management options, log retrievals, and hash extraction commands.
    
3. **Extract Unique Hashes:** Run the following command to retrieve unique captured NTLMv2 hashes:
    
    ```PowerShell
    GET NTLMV2UNIQUE
    ```
    
1. **Enumerate Usernames:** Run the following command to map captured usernames to their respective source IP addresses and hostnames for offline cracking via Hashcat:
    ```PowerShell
    GET NTLMV2USERNAMES
    ```
    

### Phase 4: Remediation & Mitigation

- **Disable LLMNR:** Enforced via Group Policy under `Computer Configuration` -> `Administrative Templates` -> `Network` -> `DNS Client` -> **Turn OFF Multicast Name Resolution**.
- **Disable NBT-NS:** Since NBT-NS cannot be disabled globally via standard GPO settings, deploy a startup script via Group Policy to update the registry across domain hosts:
    ```PowerShell
    $regkey = "HKLM:SYSTEM\CurrentControlSet\services\NetBT\Parameters\Interfaces"
    Get-ChildItem $regkey | foreach { Set-ItemProperty -Path "$regkey\$($_.pschildname)" -Name NetbiosOptions -Value 2 -Verbose }
    ```
    
- **Additional Defenses:** Enforce SMB Signing to prevent NTLM relay attacks and filter UDP ports `5355` (LLMNR) and `137` (NetBIOS-NS) at the network boundary.