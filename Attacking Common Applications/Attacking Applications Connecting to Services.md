
> ⚠️ Recovered credentials from connection strings are prime candidates for **password spraying** across other services on the network — don't just stop at the original DB target.

---
## 1. Concept
- Applications that connect to backend services (databases, APIs, etc.) often embed **connection strings** containing credentials.
- If not properly protected (e.g., encrypted, externalized to a vault), these strings can be recovered by:
    - Reverse engineering compiled binaries (ELF/PE)
    - Decompiling managed assemblies (.NET/Java)
    - Runtime memory/debugger inspection
- Recovered credentials are useful for:
    - Direct access to the connected service (e.g., MS SQL)
    - **Password reuse/spraying** against other accounts/services on the network

---
## 2. Case Study A — ELF Executable (Linux Binary)
### Target: `octopus_checker`
Running it locally shows it attempts a DB connection:

```
Attempting Connection
Connecting ...
01000:1:0:[unixODBC][Driver Manager]Can't open lib 'ODBC Driver 17 for SQL Server' : file not found
connected
```

→ Strongly suggests a hardcoded **SQL connection string** with credentials.
### Step 1 — Load in GDB + PEDA

```bash
gdb ./octopus_checker
```

```
gdb-peda$ set disassembly-flavor intel
gdb-peda$ disas main
```

- PEDA (Python Exploit Development Assistance) extends GDB with better visualization for exploit dev / reverse engineering.
- Disassembly reveals multiple `call` instructions referencing string addresses — fragments of a connection string, but **out of order and byte-reversed** (endianness — byte order differs by CPU architecture).

### Step 2 — Find the Relevant API Call

Look for the call to `SQLDriverConnect` (the ODBC function that actually opens the DB connection):

```assembly
mov    esi,0x0
mov    rdi,rax
call   0x5555555551b0 <SQLDriverConnect@plt>
```

### Step 3 — Breakpoint & Inspect Registers

```
gdb-peda$ b *0x5555555551b0
gdb-peda$ run
```

At the breakpoint, the connection string is visible directly in a register (here, RDX):

```
RDX: 0x7fffffffda70 ("DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost,1401;UID=username;PWD=password;")
```

### Result

Full **DRIVER / SERVER / UID / PWD** connection string recovered directly from memory at the point of use — bypasses the need to manually reconstruct the reversed/fragmented strings from static disassembly.

---

## 3. Case Study B — .NET DLL (Windows Binary)

### Target: `MultimasterAPI.dll`

Identify it's a .NET assembly:

```powershell
Get-FileMetaData .\MultimasterAPI.dll
```

```
.NETFramework,Version=v4.6.1
api/getColleagues
http://localhost:8081 POST
```

Confirms it's a **.NET Framework 4.6.1** assembly exposing an API endpoint (`api/getColleagues`).

### Step 1 — Decompile with dnSpy

- **dnSpy**: debugger + .NET assembly editor — reads, edits, and debugs C#/VB.NET source directly from a compiled DLL.
- Load `MultimasterAPI.dll` into dnSpy.

### Step 2 — Locate the Relevant Controller

Navigate to:

```
MultimasterAPI.Controllers → ColleagueController
```

Inspecting the `Get`/`GetColleagues` methods reveals a **hardcoded database connection string containing the password** directly in the decompiled source.

### Result

Plaintext DB credentials recovered straight from decompiled C# source — no runtime debugging even required, since .NET decompiles very close to original source.

---

## Summary

|Target Type|Tooling|Technique|
|---|---|---|
|**ELF binary (Linux)**|GDB + PEDA|Disassemble `main`, breakpoint at the connection function (`SQLDriverConnect`), read the string from a register at runtime|
|**.NET DLL (Windows)**|dnSpy|Decompile directly to near-original C# source, read hardcoded connection strings in controller/class code|

## Key Takeaways

- **.NET/Java binaries decompile almost to original source** — always try decompilation (dnSpy, JADX, ILSpy) before resorting to raw disassembly; it's far faster when available.
- **Native (ELF/PE) binaries** require disassembly + dynamic analysis — breakpointing the actual API call that consumes the secret (e.g., `SQLDriverConnect`) is more reliable than trying to manually reassemble fragmented/reversed strings from static disassembly.
- Endianness matters when reading strings/values directly from disassembly — byte order can make strings appear reversed or fragmented.
- Always test recovered credentials for **reuse** against other services/accounts on the network, not just the originally targeted database.