After securing an initial foothold, mapping out defensive controls and host-level security configurations is essential before choosing tools for deeper Active Directory enumeration, exploitation, or post-exploitation.

### 1. Windows Defender
Windows Defender blocks common offensive tooling (like PowerView) by default. Inspect its status to see if real-time monitoring is active:

```PowerShell
PS C:\htb> Get-MpComputerStatus
```
- **Key Field:** `RealTimeProtectionEnabled : True` confirms that active scanning is running, requiring attackers to utilize evasion techniques or living-off-the-land binaries (LotL).

### 2. AppLocker (Application Whitelisting)
AppLocker enforces software restrictions to dictate which files, scripts, or executables users can run. Organizations frequently block primary entry points like `powershell.exe`, but misconfigurations often leave alternative paths or related binaries (like `PowerShell_ISE.exe` or alternate paths in `SysWOW64`) accessible.

- **Inspect AppLocker Policy:**
    ```PowerShell
    PS C:\htb> Get-AppLockerPolicy -Effective | select -ExpandProperty RuleCollections
    ```
### 3. PowerShell Constrained Language Mode

When active, Constrained Language Mode severely limits PowerShell functionality by blocking COM objects, unauthorized .NET types, classes, and workflows.

- **Check Language Mode:**
    ```PowerShell
    PS C:\htb> $ExecutionContext.SessionState.LanguageMode
    ```
- **Result:** A response of `ConstrainedLanguage` indicates restrictions are in place, whereas `FullLanguage` allows standard administrative capabilities.

### 4. Microsoft LAPS (Local Administrator Password Solution)
LAPS randomizes and rotates local administrator passwords across domain hosts to prevent credential reuse and lateral movement. Using tools like **LAPSToolkit**, operators can discover which groups or accounts possess read permissions over LAPS passwords:

- **Find Delegated Groups:**
    ```PowerShell
    PS C:\htb> Find-LAPSDelegatedGroups
    ```
    
- **Check Extended Rights (finding users with explicit read rights):**
    ```PowerShell
    PS C:\htb> Find-AdmPwdExtendedRights
    ```
    
- **Retrieve LAPS Passwords (if permissions permit):**
    ```PowerShell
    PS C:\htb> Get-LAPSComputers
    ```
### Summary Checklist for Post-Foothold Environment Checks
1. **Defenders:** Is Windows Defender or an EDR solution actively blocking scripts?
2. **Execution Restrictions:** Are AppLocker rules blocking standard paths or tools? What is the PowerShell `LanguageMode`?
3. **Privilege & LAPS:** Are local admin passwords rotated via LAPS, and do current privileges allow reading them?