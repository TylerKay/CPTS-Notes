## What is the Double Hop Problem?
When authenticating via **WinRM/PSRemoting**, the user's **TGT (Ticket Granting Ticket) is not forwarded** to the remote session — only a TGS for the specific service (WinRM/HTTP) is sent. This means that from the remote session, there is no way to prove identity to a third host (e.g. a DC), so further lateral movement or AD queries fail.

**Contrast with password/NTLM auth (e.g. PSExec, SMB):** When a password is used, the NTLM hash is stored in memory on the remote host and can be used for subsequent authentication — no double hop problem.

**Scenario:** Attack Host → (evil-winrm) → DEV01 → (wants to query) → DC01

When evil-winrm connects to DEV01, only a TGS for the HTTP service is cached. Attempting to run PowerView (which needs to communicate with DC01) fails because the TGT is not present.

### Verify with klist
```powershell
klist
# Via evil-winrm: only one cached ticket (for HTTP service on target)
# Via RDP: full TGT + multiple TGS tickets cached — no double hop issue
```

### Confirmation via Mimikatz
Running `sekurlsa::logonpasswords` after a WinRM session shows the connecting user's credentials are blank — their NTLM hash is not stored in memory.

---

## Workaround 1 — PSCredential Object (works with evil-winrm)

Pass credentials explicitly with every command/tool call by creating a PSCredential object and supplying it via `-Credential`.

```powershell
$SecPassword = ConvertTo-SecureString '!qazXSW@' -AsPlainText -Force
$Cred = New-Object System.Management.Automation.PSCredential('INLANEFREIGHT\backupadm', $SecPassword)
```

**Use with PowerView:**
```powershell
get-domainuser -spn -credential $Cred | select samaccountname
```
- Without `-Credential`: fails with "An operations error occurred"
- With `-Credential`: succeeds — credentials are explicitly forwarded

**Limitation:** Must be added to every command. Not compatible with tools that don't support `-Credential`.

---

## Workaround 2 — Register PSSession Configuration (requires Windows GUI/RDP)

Creates a named PSSession configuration that impersonates the target user at the local machine level, so all requests to the remote host are made with a full set of cached Kerberos tickets.

### Step 1 — Register the configuration (from a Windows host with GUI/elevated PS)
```powershell
Register-PSSessionConfiguration -Name backupadmsess -RunAsCredential inlanefreight\backupadm
```

### Step 2 — Restart WinRM (kicks out current session)
```powershell
Restart-Service WinRM
```

### Step 3 — Connect using the named configuration
```powershell
Enter-PSSession -ComputerName DEV01 -Credential INLANEFREIGHT\backupadm -ConfigurationName backupadmsess
```

### Step 4 — Verify tickets (full TGT now present)
```powershell
klist
# krbtgt ticket now cached — DC is directly accessible
```

### Step 5 — Run tools normally (no -Credential needed)
```powershell
get-domainuser -spn | select samaccountname
```

**Limitations:**
- Cannot be used from an evil-winrm session (requires credential popup + elevated PS)
- Does not work well from Linux PowerShell hosts (Kerberos credential limitations)
- Best suited for Windows attack hosts or compromised Windows jump hosts with RDP access

---

## Other Workarounds (not covered in depth)
- **CredSSP** — enables credential delegation but weakens security
- **Port forwarding** — tunnel the DC port to your attack host
- **Process injection** — inject into a process running in the target user's context

---

## Key Takeaways

| Method | Works from evil-winrm? | Works from Windows? | Limitation |
|---|---|---|---|
| PSCredential object | ✓ | ✓ | Must pass `-Credential` to every command |
| Register-PSSessionConfiguration | ✗ | ✓ | Requires GUI/elevated PS; Windows-only |
| RDP (just use RDP instead) | N/A | ✓ | Full ticket cache, no double hop issue |

The double hop problem is encountered frequently during AD assessments. Always check `klist` when a WinRM session unexpectedly can't reach a DC or other resources — it's almost always this issue.