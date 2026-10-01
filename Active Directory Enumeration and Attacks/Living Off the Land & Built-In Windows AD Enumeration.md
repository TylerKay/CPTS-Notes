**Living Off the Land** refers to the technique of using native operating system tools, binaries, and scripting languages (such as Windows built-in commands, PowerShell, WMI, and DSquery) to perform host and network reconnaissance.

This approach is crucial during engagements where hosts lack internet access, dropping external tools has failed, or stealth is required. Modern enterprise networks deploy robust monitoring (EDRs, IDS/IPS, and baselining sensors); bringing external tools into a network significantly raises the risk of detection. Utilizing native binaries minimizes new log artifacts and helps operators blend in with normal administrative activity.

### Methodology, Step-by-Step Process & Commands
#### Step 1: Initial Host & Environmental Reconnaissance

Before exploring the network, gather basic system configurations, patch levels, and network states from the compromised host.

- **Basic Commands:** Run basic system and environment queries.
    ```DOS
    hostname
    ipconfig /all
    set
    echo %USERDOMAIN%
    echo %logonserver%
    ```
- **Consolidated Summary:** Execute `systeminfo` to collect a complete overview in a single command execution, reducing noise.
    ```DOS
    systeminfo
    ```
- **OS Patches:** Check installed hotfixes.
    ```DOS
    wmic qfe get Caption,Description,HotFixID,InstalledOn
    ```
#### Step 2: Harnessing PowerShell & Operational Security (OpSec)
PowerShell provides deep administrative control over Windows and Active Directory, but modern usage heavily generates Script Block logs.
- **Check Modules & Policy:** Review loaded modules and execution policy scopes.
    ```PowerShell
    Get-Module
    Get-ExecutionPolicy -List
    
    Set-ExecutionPolicy Bypass -Scope Process
    
    ```
    
- **Inspect Environment & History:** Query environment values and check user command histories for exposed credentials or scripts.
    ```PowerShell
    Get-ChildItem Env: | ft Key,Value
    Get-Content $env:APPDATA\Microsoft\Windows\Powershell\PSReadline\ConsoleHost_history.txt
    ```
    
- **Downgrade to PowerShell v2 (Stealth Tactic):** Invoke an older PowerShell instance to bypass Script Block logging (introduced in version 3.0). _Note: The downgrade action itself is logged._
    ```PowerShell
    powershell.exe -version 2
    ```
#### Step 3: Checking Host Defenses
Assess active security controls and firewall boundaries before taking further action.
- **Firewall Status:** Determine if domain, private, or public profiles are active or blocking traffic.
    ```PowerShell
    netsh advfirewall show allprofiles
    ```
- **Windows Defender Status:** Check service health or inspect signature versions and scanning settings.
    ```DOS
    sc query windefend
    ```
    
    ```PowerShell
    Get-MpComputerStatus
    ```
    
- **Active User Check:** Verify if other users are actively logged into the host.
    ```PowerShell
    qwinsta
    ```
    
#### Step 4: Network & Routing Discovery
Map the local segment and identify adjacent networks available for lateral movement.
- **ARP & Routing Tables:** View known local hosts and IPv4/IPv6 routing tables to highlight potential network paths or adjacent subnets for pivoting.
    ```PowerShell
    arp -a
    route print
    ```
#### Step 5: Windows Management Instrumentation (WMI) Queries
Leverage the WMI scripting engine via `wmic` to query local and remote domain information.
- **Domain Structure:** Discover child domains and forest trusts.
    ```PowerShell
    wmic ntdomain get Caption,Description,DnsForestName,DomainName,DomainControllerAddress
    ```
- **System & Account Enumeration:** List local and cached domain accounts.
    ```PowerShell
    wmic computersystem get Name,Domain,Manufacturer,Model,Username,Roles /format:List
    wmic useraccount list /format:list
    ```
#### Step 6: Native Net Commands & EDR Evasion
Query domain groups, users, and shares using native utilities.
- **Domain Queries:** Map out high-privilege groups and user memberships.
    ```PowerShell
    net group /domain
    net group "Domain Admins" /domain
    net user <account_name> /domain
    ```
    
- **EDR Bypass Trick:** If security solutions flag monitoring alerts for `net.exe`, use `net1` instead to execute the exact same queries without triggering specific string-based signatures.
    ```PowerShell
    net1 group /domain
    ```

#### Step 7: Advanced Object Discovery with Dsquery
Utilize `dsquery` (backed by `dsquery.dll` on modern systems) to run precise Active Directory object searches and LDAP filters.
- **Basic Searches:** List objects or use wildcard searches.
    ```PowerShell
    dsquery user
    dsquery computer
    dsquery * "CN=Users,DC=INLANEFREIGHT,DC=LOCAL"
    ```
    
- **LDAP Filtering:** Use custom LDAP queries with Object Identifiers (OIDs) and logical operators to locate specific attributes (e.g., searching for user account control bitmasks like password requirements or domain controller indicators).
    ```PowerShell
    dsquery * -filter "(&(objectCategory=person)(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=32))" -attr distinguishedName userAccountControl
    dsquery * -filter "(userAccountControl:1.2.840.113556.1.4.803:=8192)" -limit 5 -attr sAMAccountName
    ```
    
> **Note:** Always document your native enumeration findings carefully. They not only validate your access and potential lateral movement paths but also provide critical visibility for your clients to remediate unmonitored misconfigurations.


#### OID match strings

OIDs are rules used to match bit values with attributes, as seen above. For LDAP and AD, there are three main matching rules:

1. `1.2.840.113556.1.4.803`

When using this rule as we did in the example above, we are saying the bit value must match completely to meet the search requirements. Great for matching a singular attribute.

2. `1.2.840.113556.1.4.804`

When using this rule, we are saying that we want our results to show any attribute match if any bit in the chain matches. This works in the case of an object having multiple attributes set.

3. `1.2.840.113556.1.4.1941`

This rule is used to match filters that apply to the Distinguished Name of an object and will search through all ownership and membership entries.


Other:

Get user that has disabled account and has admin access
```PowerShell
Get-ADUser -LDAPFilter "(&(userAccountControl:1.2.840.113556.1.4.803:=2)(adminCount=1))" -Properties adminCount, userAccountControl | 
Select-Object Name, SamAccountName, UserAccountControl
```
