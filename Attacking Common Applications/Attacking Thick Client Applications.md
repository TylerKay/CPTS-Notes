# Attacking Thick Client Applications

> ⚠️ Reverse-engineering steps here (dumping memory, deobfuscating .NET binaries) can trip AV/EDR on the target host — be mindful of noise during live engagements, and always operate within scope.

---
## 1. What Are Thick Clients?

- Applications **installed locally**, unlike thin clients that run remotely and are accessed via browser.
- Don't require internet access to run; better performance (CPU/memory/storage) than thin clients.
- Common in enterprise: project management, CRM, inventory tools, other internal productivity software.
- Usually built in **Java, C++, .NET, or Silverlight**.

### Security Mechanisms (Java example)

- **Sandbox** — isolates untrusted code (e.g., downloaded from the internet) from system resources.
- **Java API restrictions** and **Code Signing** — further harden the runtime.

### Characteristics

- Independent software; works offline
- Stores data locally
- **Less secure** than thin/web clients
- Consumes more resources
- More expensive to deploy/maintain (patches applied locally, machine by machine)

---

## 2. Architecture Types

|Tier|Description|Security Implication|
|---|---|---|
|**Two-tier**|App installed locally, talks **directly** to the database|Less secure — attacker can potentially reach the DB directly|
|**Three-tier**|App installed locally, talks to an **application server** (usually HTTP/HTTPS), which talks to the DB|More secure — DB is not directly reachable by the client/attacker|

---

## 3. Applicable Vulnerabilities

**Not applicable** (these are browser/web-specific): XSS, CSRF, Clickjacking.

**Applicable to thick clients:**
- Improper Error Handling
- Hardcoded sensitive data (creds, keys, tokens)
- DLL Hijacking
- Buffer Overflow
- SQL Injection
- Insecure Storage
- Session Management flaws

---

## 4. Penetration Testing Methodology
### Step 1 — Information Gathering
Identify architecture, languages/frameworks, client vs. server-side tech, entry points, and user inputs.

| Tool                      | Purpose                                   |
| ------------------------- | ----------------------------------------- |
| CFF Explorer              | PE file inspection                        |
| Detect It Easy            | Identify packers/compilers/languages used |
| Process Monitor (ProcMon) | Monitor file/registry/process activity    |
| Strings                   | Extract readable strings from binaries    |

### Step 2 — Client-Side Attacks

- Static analysis: reverse-engineer EXE/DLL/JAR/CLASS/WAR files, look for hardcoded credentials/secrets in source or resources.
- Dynamic analysis: inspect runtime memory — sensitive data (creds, tokens) is often present in memory even if not on disk.
- Client-side attack surface overlaps with web apps: command injection, weak access control, SQL injection (since thick clients still often talk to a backend).

|Tool|Purpose|
|---|---|
|Ghidra / IDA|Static disassembly/decompilation|
|OllyDbg / x64dbg|Dynamic debugging|
|Radare2|Reverse engineering framework|
|dnSpy|.NET decompiler/debugger|
|JADX|Java/Android decompiler|
|Frida|Dynamic instrumentation|

### Step 3 — Network-Side Attacks

Capture and analyze traffic to/from the app (HTTP/HTTPS/TCP/UDP) for sensitive data in transit and to understand app behavior.

|Tool|Purpose|
|---|---|
|Wireshark|Packet capture/analysis|
|tcpdump|CLI packet capture|
|TCPView|Live connection monitoring (Windows)|
|Burp Suite|Intercept/manipulate HTTP(S) traffic|

### Step 4 — Server-Side Attacks

Similar to standard web app testing — focus on OWASP Top Ten-style issues on the backend the thick client talks to.

---

## 5. Case Study — Retrieving Hardcoded Credentials

**Scenario:** Already have SMB access; found `RestartOracle-Service.exe` on the **NETLOGON** share.
### Step 1 — Initial Run (No Visible Output)
```cmd
.\Restart-OracleService.exe
```

Executes silently — no visible window or output.
### Step 2 — Monitor with Process Monitor (ProcMon64)
Reveals the binary creates a temp file under:

```
C:\Users\Matt\AppData\Local\Temp
```

### Step 3 — Prevent Self-Deletion of Temp Artifacts

The dropped files get deleted almost immediately. To capture them, remove **Delete** permissions on the Temp folder:
```
Right-click Temp folder → Properties → Security → Advanced
→ Disable inheritance → Convert to explicit permissions
→ Edit → Show advanced permissions
→ Deselect "Delete subfolders and files" and "Delete"
→ OK → Apply → OK → OK
```
### Step 4 — Re-run and Capture the Dropped File

```cmd
dir C:\Users\cybervaca\AppData\Local\Temp\2
```

```
6F39.bat
6F39.tmp
```

> Filenames are randomized on each run.

### Step 5 — Inspect the Batch File

The `.bat` file:
- Checks `%username%` against an allowlist (`matt`, `frankytech`, `ev4si0n`) before proceeding.
- Writes a huge block of base64 text (via chained `echo` statements) to `c:\programdata\oracle.txt`.
- Generates a PowerShell script (`monta.ps1`) that decodes the base64 into `restart-service.exe`.
- **Deletes both `oracle.txt` and `monta.ps1`** after execution to cover its tracks.

### Step 6 — Defeat the Self-Cleanup

Edit the batch script to **remove the `del` commands**, then re-run it (double-click) to let the intermediate files persist:
```
c:\programdata\oracle.txt      # base64-encoded payload
c:\programdata\monta.ps1       # decoder script
```

### Step 7 — Decode the Payload

```powershell
cat C:\programdata\monta.ps1
```

```powershell
$salida = $null
$fichero = (Get-Content C:\ProgramData\oracle.txt)
foreach ($linea in $fichero) {$salida += $linea}
$salida = $salida.Replace(" ","")
[System.IO.File]::WriteAllBytes("c:\programdata\restart-service.exe", [System.Convert]::FromBase64String($salida))
```

Running it produces the final executable:

```
restart-service.exe
```

### Step 8 — Run and Observe

```powershell
.\restart-service.exe
```

Displays an ASCII banner: _"Restart Oracle created by HelpDesk 2010"_. ProcMon shows only registry queries — nothing conclusive yet.

### Step 9 — Debug with x64dbg

1. Open x64dbg → **Options → Preferences** → uncheck everything except **Exit Breakpoint** (skips DLL loading noise, starts debugging near app exit).
2. **File → Open** → load `restart-service.exe`.
3. In the CPU view, right-click → **Follow in Memory Map**.
4. Look for a memory region of interest — in this case, size `0x3000`, type `MAP`, protection `-RW--` (memory-mapped file region — a common spot for embedded/hardcoded payloads or credentials).
5. Double-click the region — spotting `MZ` magic bytes confirms an embedded **DOS MZ executable** hidden in memory.

### Step 10 — Dump and Analyze the Embedded Executable

Right-click the memory region → **Dump Memory to File**, then run `strings`:

```cmd
strings64.exe .\restart-service_00000000001E0000.bin
```

```
.NETFramework,Version=v4.0,Profile=Client
.NET Framework 4 Client Profile
```

Confirms the embedded blob is itself a **.NET executable**.

### Step 11 — Deobfuscate with de4dot

```cmd
de4dot restart-service_00000000001E0000.bin
```

Produces a cleaned binary with de-obfuscated symbol names:

```
restart-service_00000000001E0000-cleaned.bin
```

### Step 12 — Decompile with dnSpy

Drag the cleaned binary into **dnSpy** to view readable C# source.

### Result

The disclosed source reveals the binary is a **custom `runas.exe`**-style tool that restarts the Oracle service using **hardcoded credentials** embedded in the code — exactly the kind of secret this whole investigation was hunting for.

---

## Summary

|Phase|Tooling|Goal|
|---|---|---|
|Info gathering|CFF Explorer, DiE, ProcMon, Strings|Understand architecture/tech stack|
|Client-side (static)|Ghidra, IDA, dnSpy, JADX, de4dot|Find hardcoded secrets, reverse obfuscation|
|Client-side (dynamic)|x64dbg, OllyDbg, Radare2, Frida|Inspect runtime memory for secrets|
|Network-side|Wireshark, tcpdump, TCPView, Burp|Capture sensitive data in transit|
|Server-side|Standard web methodology|OWASP Top Ten-style backend issues|

## Key Takeaways

- Thick client apps hide surprisingly weak security under the hood — hardcoded creds are common even in "trusted" internal tools distributed via NETLOGON/SYSVOL.
- Self-deleting dropper scripts can be defeated by removing delete permissions on the drop folder or editing out the `del` commands before re-running.
- Memory-mapped regions (`MAP`, `-RW--` protection) in a debugger are a good place to look for embedded payloads/executables.
- .NET obfuscation is often trivially reversible: `de4dot` (deobfuscate) → `dnSpy` (decompile) recovers readable source and hardcoded secrets.