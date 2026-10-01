# ACL Enumeration — Active Directory

## Why Targeted Enumeration Matters
`Find-InterestingDomainAcl` returns massive, unfilterable output — not practical during a time-boxed assessment. Instead, **start with a user you control** and enumerate outward from there.

---

## PowerView — Targeted ACL Enumeration

### Step 1 — Get the SID of the controlled user
```powershell
Import-Module .\PowerView.ps1
$sid = Convert-NameToSid wley
```

### Step 2 — Find all domain objects that user has rights over
```powershell
Get-DomainObjectACL -ResolveGUIDs -Identity * | ? {$_.SecurityIdentifier -eq $sid}
```
Always use **`-ResolveGUIDs`** — without it, `ObjectAceType` shows raw GUIDs (e.g. `00299570-246d-11d0-a768-00aa006e0529`) instead of human-readable names like `User-Force-Change-Password`.

### Manual GUID lookup (alternative to -ResolveGUIDs)
```powershell
$guid = "00299570-246d-11d0-a768-00aa006e0529"
Get-ADObject -SearchBase "CN=Extended-Rights,$((Get-ADRootDSE).ConfigurationNamingContext)" -Filter {ObjectClass -like 'ControlAccessRight'} -Properties * | Select Name,DisplayName,DistinguishedName,rightsGuid | ?{$_.rightsGuid -eq $guid} | fl
```

---

## Without PowerView — Native Cmdlets

### Create a list of all domain users
```powershell
Get-ADUser -Filter * | Select-Object -ExpandProperty SamAccountName > ad_users.txt
```

### Loop through and check ACLs for a specific identity
```powershell
foreach($line in [System.IO.File]::ReadLines("C:\Users\htb-student\Desktop\ad_users.txt")) {
    get-acl "AD:\$(Get-ADUser $line)" | Select-Object Path -ExpandProperty Access | Where-Object {$_.IdentityReference -match 'INLANEFREIGHT\\wley'}
}
```
> Much slower than PowerView but useful when restricted to client-provided systems with no custom tools available. GUIDs in output still require manual resolution.

---

## Full Enumeration Chain — Example

### Controlled user: wley
```powershell
$sid = Convert-NameToSid wley
Get-DomainObjectACL -ResolveGUIDs -Identity * | ? {$_.SecurityIdentifier -eq $sid}
```
**Finding:** `wley` has `User-Force-Change-Password` (ExtendedRight) over `damundsen`


> Asterisk * can be replaced with a search of the group. So for instance:
```
> Get-DomainObjectAcl -ResolveGUIDs -Identity "GPO Management" | ? {$_.SecurityIdentifier -eq $sid}
```

### Pivot to damundsen
```powershell
$sid2 = Convert-NameToSid damundsen
Get-DomainObjectACL -ResolveGUIDs -Identity * | ? {$_.SecurityIdentifier -eq $sid2} -Verbose
```
**Finding:** `damundsen` has `GenericWrite` over `Help Desk Level 1` group

### Check group nesting
```powershell
Get-DomainGroup -Identity "Help Desk Level 1" | select memberof
```
**Finding:** `Help Desk Level 1` is nested inside `Information Technology` group

### Check IT group's rights
```powershell
$itgroupsid = Convert-NameToSid "Information Technology"
Get-DomainObjectACL -ResolveGUIDs -Identity * | ? {$_.SecurityIdentifier -eq $itgroupsid} -Verbose
```
**Finding:** `Information Technology` has `GenericAll` over user `adunn`

### Check what adunn can do
```powershell
$adunnsid = Convert-NameToSid adunn
Get-DomainObjectACL -ResolveGUIDs -Identity * | ? {$_.SecurityIdentifier -eq $adunnsid} -Verbose
```
**Finding:** `adunn` has `DS-Replication-Get-Changes` + `DS-Replication-Get-Changes-In-Filtered-Set` on the domain object → **DCSync attack**

---

## Full Attack Chain Summary

```
wley (cracked from Responder capture)
  └─ ForceChangePassword → damundsen
       └─ GenericWrite → Help Desk Level 1
            └─ Nested into Information Technology
                 └─ GenericAll → adunn
                      └─ DS-Replication-Get-Changes(-All) → DCSync → full domain compromise
```

---

## BloodHound — ACL Enumeration (Much Faster)

### Identify rights for a controlled user
1. Set `wley` as the starting node
2. Go to **Node Info** tab → **Outbound Control Rights**
3. Check:
   - **First Degree Object Control** → direct rights
   - **Transitive Object Control** → full ACL attack path count

### Right-click edges for abuse guidance
Each edge in BloodHound provides a **Help menu** with:
- Explanation of the right
- Tools and commands to exploit it
- OPSEC considerations
- External references

### Useful pre-built queries
- **"Find Principals with DCSync Rights"** → confirms `adunn` has `GetChanges` + `GetChangesAll`

### Custom Cypher for WinRM access
```cypher
MATCH p1=shortestPath((u1:User)-[r1:MemberOf*1..]->(g1:Group)) MATCH p2=(u1)-[:CanPSRemote*1..]->(c:Computer) RETURN p2
```

---

## Key Takeaways
- Always enumerate ACLs **starting from a controlled user's SID** — not blindly with `Find-InterestingDomainAcl`
- Always use **`-ResolveGUIDs`** with PowerView to get human-readable ACE types
- **Nested group membership** multiplies the impact of any single ACL right — always check `memberof` for interesting groups
- BloodHound makes this chain trivially visible; PowerView enumeration is the backup for when BloodHound isn't available
- `GenericAll` = full control; `GenericWrite` = modify most attributes; `ForceChangePassword` = reset password without knowing current