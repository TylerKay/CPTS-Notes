
> ⚠️ Always confirm with the client that any discovered trusts are in scope before enumerating/attacking across them — going outside the Rules of Engagement is a real risk here.

---

## 1. Why Trusts Matter

Organizations set up **trust relationships** between domains/forests to avoid re-migrating objects during mergers, acquisitions, or business unit integration. This is convenient but often introduces **unintended attack paths**:

- Trusts are frequently set up for ease-of-use and never security-reviewed afterward.
- M&A activity can create bidirectional trusts with acquired companies whose security posture is unknown/untested.
- Attackers can pivot through a **softer target** (e.g., an acquired subsidiary) to reach the principal domain.
- Common real-world pattern: Kerberoasting a user in a _trusted_ domain (external or linked domain) who happens to have admin rights in the _principal_ domain (main internal domain) — no foothold needed in the primary domain at all.

> 💡 Note trust relationships for the report even if not exploited — orgs are frequently unaware a trust exists at all.

---

## 2. Trust Types

|Type|Description|
|---|---|
|**Parent-Child**|Two+ domains in the same forest; two-way transitive trust (e.g., `corp.inlanefreight.local` ↔ `inlanefreight.local`)|
|**Cross-link**|Trust between child domains to speed up authentication|
|**External**|Non-transitive trust between two separate domains in separate (not already forest-trusted) forests; uses SID filtering|
|**Tree-root**|Two-way transitive trust between forest root domain and a new tree root domain; created automatically when a new tree root is added|
|**Forest**|Transitive trust between two forest root domains|
|**ESAE**|Bastion forest used to manage AD (administrative tier isolation)|

---

## 3. Transitivity

|Transitive|Non-Transitive|
|---|---|
|Shared, 1-to-many|Direct trust only|
|Extended to everyone in the forest|Not extended to child domains|
|Forest, tree-root, parent-child, cross-link trusts|Typical for external / custom trust setups|

- **Transitive:** If A trusts B, and B trusts C, then A automatically trusts C.
- **Non-transitive:** Only the direct domain in the relationship is trusted.

> 📦 **Analogy:** Transitive = anyone in your household can sign for your package. Non-transitive = only you can sign; no one else in the house counts.

---

## 4. Trust Direction

|Direction|Behavior|
|---|---|
|**One-way**|Users in the _trusted_ domain can access resources in the _trusting_ domain — not vice versa|
|**Bidirectional (two-way)**|Users in both domains can access resources in the other domain|

Example: A bidirectional trust between `INLANEFREIGHT.LOCAL` and `FREIGHTLOGISTICS.LOCAL` lets users from either domain access resources in the other.

> If you can't authenticate across a trust, you can't enumerate or attack across it — direction matters for planning.

---

## 5. Enumerating Trusts

### Built-in: `Get-ADTrust`

powershell

```powershell
Import-Module activedirectory
Get-ADTrust -Filter *
```

Key fields to check:

- `IntraForest` — `True` = parent/child trust within the same forest
- `ForestTransitive` — `True` = forest or external trust
- `Direction` — `BiDirectional` / one-way
- `TGTDelegation` — whether TGT delegation is allowed across the trust (relevant for cross-forest Printer Bug attacks)

```
Direction        : BiDirectional
Name             : LOGISTICS.INLANEFREIGHT.LOCAL
ForestTransitive : False
IntraForest      : True
```

```
Direction        : BiDirectional
Name             : FREIGHTLOGISTICS.LOCAL
ForestTransitive : True
IntraForest      : False
```

### PowerView: `Get-DomainTrust`

```powershell
Get-DomainTrust
```

```
SourceName      : INLANEFREIGHT.LOCAL
TargetName      : LOGISTICS.INLANEFREIGHT.LOCAL
TrustAttributes : WITHIN_FOREST
TrustDirection  : Bidirectional

SourceName      : INLANEFREIGHT.LOCAL
TargetName      : FREIGHTLOGISTICS.LOCAL
TrustAttributes : FOREST_TRANSITIVE
TrustDirection  : Bidirectional
```

### PowerView: `Get-DomainTrustMapping`

Maps trusts recursively (both directions, across all discoverable domains) — useful once you have a foothold and want the full trust picture.

```powershell
Get-DomainTrustMapping
```

### Enumerate Users in a Trusted/Child Domain

```powershell
Get-DomainUser -Domain LOGISTICS.INLANEFREIGHT.LOCAL | select SamAccountName
```

```
samaccountname
--------------
htb-student_adm
Administrator
Guest
lab_adm
krbtgt
```

### Built-in: `netdom`

```cmd
netdom query /domain:inlanefreight.local trust
netdom query /domain:inlanefreight.local dc
netdom query /domain:inlanefreight.local workstation
```

- `trust` → lists trust relationships
- `dc` → lists domain controllers
- `workstation` → lists workstations/servers in the domain

### BloodHound

Use the built-in **"Map Domain Trusts"** pre-built query to visualize trust direction and type at a glance.

---

## Summary

|Tool|Best For|
|---|---|
|`Get-ADTrust`|Built-in-tools-only environments; detailed trust attributes (SID filtering, TGT delegation, encryption)|
|`Get-DomainTrust` (PowerView)|Quick listing of trusts from current domain|
|`Get-DomainTrustMapping` (PowerView)|Full recursive trust map across all reachable domains|
|`netdom`|Built-in CLI alternative; also lists DCs/workstations|
|BloodHound|Visual trust mapping ("Map Domain Trusts" query)|

## Key Takeaways

- Trusts can be **transitive/non-transitive** and **one-way/bidirectional** — both properties determine what's actually exploitable.
- A trust relationship = a potential attack path in either direction (if bidirectional).
- Weaknesses in a trusted (even seemingly "less important") domain can lead straight to the principal domain.
- Always verify **scope** before enumerating or attacking across a discovered trust.

## Up Next

- Attacks against **child → parent** domain trusts
- Attacks across **bidirectional forest trusts**


Notes:
- In Active Directory, ==a **forest transitive trust** connects two separate forests so that users in one forest can access resources across the entire trusted forest, whereas a **within-forest trust** (intra-forest) describes the automatic, two-way transitive relationship between parent, child, and tree domains inside a single forest==