### Overview & Objectives

When conducting internal penetration tests with valid domain credentials from a Windows host, enumeration helps uncover misconfigurations, permission issues, and structural domain setups. This data aids in mapping lateral/vertical movement paths, discovering file share credentials, and identifying reporting or security posture improvements.
### Methodology

The objective-driven methodology relies on leveraging built-in administrative tools and advanced PowerShell modules to map the Active Directory landscape stealthily or efficiently.
- **Stealth & Native Access:** Use native Windows mechanisms (like the built-in Active Directory PowerShell module) to blend in with normal administrative traffic.
- **Situational Awareness:** Map users, groups (including nested memberships), computers, organizational units, and domain/forest trust relationships using dedicated toolsets like PowerView.
- **Vulnerability Spotting:** Hunt for specific security indicators such as Service Principal Names (SPNs) for Kerberoasting or over-privileged local group memberships.
    
### Step-by-Step Execution Process
#### Phase 1: Native Active Directory PowerShell Module Enumeration
1. **Check Loaded Modules:** Determine if the Active Directory module is already imported.
    ```PowerShell
    Get-Module
    ```
    
2. **Import Module:** If missing, load the ActiveDirectory module into the PowerShell session.
    ```PowerShell
    Import-Module ActiveDirectory
    ```
    
3. **Enumerate Domain Information:** Extract structural details like domain controllers, functional levels, and the domain SID.
    ```PowerShell
    Get-ADDomain
    ```
    
4. **Hunt for Kerberoastable Accounts:** Filter user objects for populated Service Principal Names (SPNs).
    ```PowerShell
    Get-ADUser -Filter {ServicePrincipalName -ne "$null"} -Properties ServicePrincipalName
    ```
    
5. **Verify Domain Trusts:** Enumerate internal or external forest trust structures.
    ```PowerShell
    Get-ADTrust -Filter *
    ```
6. **Analyze Group Memberships:** List all groups and inspect high-value targets (e.g., Backup Operators) for sensitive accounts.
    ```PowerShell
    Get-ADGroup -Filter * | select name
    Get-ADGroupMember -Identity "Backup Operators"
    ```
#### Phase 2: Advanced Situational Awareness with PowerView

1. **Import PowerView:** Load the script into memory from your working directory.
    ```PowerShell
    Import-Module .\PowerView.ps1
    ```
    
2. **Extract Detailed User Attributes:** Query specific user properties, group memberships, and account control settings.
    ```PowerShell
    Get-DomainUser -Identity mmorgan -Domain inlanefreight.local | Select-Object -Property name,samaccountname,memberof,useraccountcontrol
    ```
    
3. **Perform Recursive Group Membership Analysis:** Uncover nested group relationships to spot hidden inheritance of administrative rights (e.g., Domain Admins).
    ```PowerShell
    Get-DomainGroupMember -Identity "Domain Admins" -Recurse
    ```
    
4. **Map Domain Trust Relationships:** Display detailed trust maps across forests.
    ```PowerShell
    Get-DomainTrustMapping
    ```
    
5. **Test Local Administrator Access:** Check administrative privileges against local or remote systems.
    ```PowerShell
    Test-AdminAccess -ComputerName ACADEMY-EA-MS01
    ```
    
6. **Enumerate SPNs Quickly:** Retrieve accounts tied to service principal names for upcoming attack phases.
    ```PowerShell
    Get-DomainUser -SPN -Properties samaccountname,ServicePrincipalName
    ```
> **Note:** While native modules offer stealth, tools like PowerView and BloodHound dramatically accelerate data collection and simplify complex relationship analysis across large Windows domains.

### Active Directory Credentialed Enumeration from Windows (Part 2: SharpView, Snaffler, and BloodHound)

### Overview & Objectives

Building upon native Active Directory modules and basic PowerView enumeration, this phase expands into advanced reconnaissance tools: **SharpView** (a .NET port of PowerView), **Snaffler** (for automated file and credential hunting across domain shares), and **BloodHound/SharpHound** (for relationship mapping and attack path visualization).

### Methodology

The methodology shifts from manual, individual attribute queries to automated, scale-driven discovery and data correlation:
- **Alternative Tooling ("Living Off The Land" & Alternatives):** Using compiled binaries like SharpView when PowerShell logging or restrictions hinder script execution.
- **Share Pillage & Data Exposure Analysis:** Systematically crawling network shares to detect sensitive information disclosure (e.g., configuration files, private keys, password databases).
- **Graph-Based Correlation:** Ingesting structured enumeration data into BloodHound to uncover hidden attack paths and permission chains.
### Step-by-Step Execution Process
#### Phase 1: Alternative Enumeration with SharpView
1. **View Command Help:** Inspect argument parameters using the `-Help` suffix on compiled binaries.
    ```PowerShell
    .\SharpView.exe Get-DomainUser -Help
    ```
2. **Enumerate Specific Domain Users:** Query user details (such as a controlled account like `forend`) without relying on native PowerShell script execution.
    ```PowerShell
    .\SharpView.exe Get-DomainUser -Identity forend
    ```
#### Phase 2: Automated Share Hunting with Snaffler
1. **Execute Snaffler for Credential & Data Discovery:** Target domain hosts to scan readable directories and files for sensitive strings or extensions (e.g., `.kdb`, `.key`, `.ppk`, `.sqldump`).
    ```Bash
    Snaffler.exe -s -d inlanefreight.local -o snaffler.log -v data
    ```
    _(The `-s` flag streams console output, `-d` defines the domain, `-o` writes results to a log, and `-v data` sets the verbosity level)._

#### Phase 3: Relationship Mapping and Visual Analysis with SharpHound / BloodHound
1. **Review Available Collection Flags:** Check collection options for SharpHound.
    ```PowerShell
    .\SharpHound.exe --help
    ```
    
2. **Execute Full Collection:** Gather comprehensive domain data including groups, local admins, sessions, ACLs, and trusts.
    ```PowerShell
    .\SharpHound.exe -c All --zipfilename ILFREIGHT
    ```
    
3. **Ingest and Analyze in BloodHound:**
    - Open the blBloodHound GUI console (start via `bloodhound` in CMD/PowerShell, authenticating with `neo4j` credentials if prompted).
    - Upload the generated `.zip` dataset via the **Upload Data** option.
    - Search for structural overviews (e.g., search `domain:INLANEFREIGHT.LOCAL`) or leverage pre-built analysis queries (such as _Find Computers with Unsupported Operating Systems_ or _Find Computers where Domain Users are Local Admin_).
> **Engagement Note:** Document all transferred files, logs, and artifacts placed on disk during enumeration to ensure proper deconfliction and cleanup at the conclusion of the assessment.