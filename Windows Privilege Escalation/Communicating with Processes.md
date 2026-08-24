# Communication with Processes — Windows PrivEsc

## Why Processes Matter for PrivEsc
Running processes are one of the best places to look for privilege escalation — even a non-admin process can lead to elevated access.

**Classic example:** Find a web server (IIS, XAMPP) running on the box → drop an `.aspx`/`.php` webshell → gain a shell as the web server's user. That user is usually not an admin, but often holds the **`SeImpersonate`** token — enabling privesc via **Rogue/Juicy/Lonely Potato** to reach SYSTEM.

---

## Access Tokens
- Describe the **security context** of a process or thread (user identity + privileges).
- Assigned after successful authentication (password verified against a security database).
- A **copy of the token** is presented every time a user interacts with a process to determine privilege level.

---

## Enumerating Network Services

Most process interaction happens via network sockets (DNS, HTTP, SMB, etc.). `netstat` reveals what's listening and where.

```cmd
netstat -ano
```

### What to Look For
**Focus on entries bound to loopback addresses (`127.0.0.1` / `::1`)** rather than the host IP (e.g. `10.129.43.8`) or broadcast (`0.0.0.0` / `::/0`).

**Why:** Localhost-bound sockets are frequently left insecure under the assumption "they aren't accessible to the network" — but once you have local shell access, they're fully reachable.

Example from netstat output:
```
TCP    127.0.0.1:14147        0.0.0.0:0              LISTENING       3812
TCP    [::1]:14147            [::]:0                 LISTENING       3812
```
- Port **14147** = FileZilla's **administrative interface**.
- Exploitable to extract stored FTP passwords, and to create an FTP share at `C:\` running as the FileZilla Server user (potentially Administrator).

---

## Other Local Service PrivEsc Examples

### Splunk Universal Forwarder
- Ships logs to Splunk; historically had **no authentication by default**, allowing arbitrary app deployment → code execution.
- Ran as **SYSTEM** by default, not a low-priv account.
- Further reading: *Splunk Universal Forwarder Hijacking*, **SplunkWhisperer2**.

### Erlang Port — 25672
- Erlang nodes join a cluster using a shared secret ("cookie").
- Common weak/default cookies (e.g. RabbitMQ's default: `rabbit`) or poorly protected cookie config files.
- Affected apps: SolarWinds, RabbitMQ, CouchDB.
- Further reading: *Erlang-arce* blog post by Mubix.

---

## Named Pipes

### Concept
- In-memory "files" used for IPC, cleared after being read.
- Two types: **anonymous pipes** and **named pipes** (e.g. `\\.\PipeName\ExampleNamedPipeServer`).
- Client-server model: creator = server, connector = client.
- Modes: **half-duplex** (client writes only) or **duplex** (two-way).
- Each new connection creates a new pipe instance (same name, separate data buffer).

### Cobalt Strike Context
- Uses named pipes for nearly all command execution (except BOFs):
  1. Beacon creates a pipe (e.g. `\.\pipe\msagent_12`)
  2. Spawns a process, injects the command, directs output to the pipe
  3. Server reads pipe output
- Isolates beacon from command execution risk (AV flags/crashes don't kill the beacon).
- Operators often rename pipes to masquerade as legitimate software (e.g. `mojo` mimicking Chrome) — a detection tell if the mimicked app isn't actually installed.

### Enumerating Named Pipes

**Sysinternals PipeList:**
```cmd
pipelist.exe /accepteula
```

**PowerShell:**
```powershell
gci \\.\pipe\
```

### Checking Pipe Permissions (AccessChk)
Named pipes have DACLs defining read/write/execute/modify rights.

**Check a specific pipe (e.g. LSASS):**
```cmd
accesschk.exe /accepteula \\.\Pipe\lsass -v
```
- Example result: only `BUILTIN\Administrators` has `FILE_ALL_ACCESS` — expected/secure.

**Check all pipes for write access:**
```cmd
accesschk.exe -w \pipe\* -v
```

---

## Exploitation Example — WindscribeService Named Pipe

Reference: *WindscribeService Named Pipe Privilege Escalation*

**Step 1 — Search for writable pipes:**
```cmd
accesschk.exe -w \pipe\* -v
```
→ Found `WindscribeService` grants R/W to `Everyone`.

**Step 2 — Confirm access level:**
```cmd
accesschk.exe -accepteula -w \pipe\WindscribeService -v
```
```
\\.\Pipe\WindscribeService
  Medium Mandatory Level (Default) [No-Write-Up]
  RW Everyone
        FILE_ALL_ACCESS
```
- `Everyone` has **full access** — misconfiguration.

**Result:** Lax pipe permissions on a privileged service can be leveraged to escalate to **SYSTEM**.

---

## Key Takeaways
- Always inspect `netstat -ano` for **loopback-only listeners** — these are often forgotten and insecure.
- Access tokens define process-level privilege context — understanding them clarifies why webshell access ≠ admin, but can still lead there via impersonation privileges.
- Named pipes are a core Windows IPC mechanism — enumerate with `pipelist.exe`/`gci \\.\pipe\`, then audit with `accesschk.exe` for overly permissive DACLs (`Everyone` + `FILE_ALL_ACCESS` on a privileged pipe = SYSTEM privesc path).