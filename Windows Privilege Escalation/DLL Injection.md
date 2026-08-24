# DLL Injection & DLL Hijacking

## DLL Injection Overview
Inserting a DLL into a running process so the injected code runs within that process's context — accessing its resources and influencing its behavior. Legitimate uses include **hot patching** (e.g. Azure's live server updates without downtime). Abused by attackers to inject malicious code into trusted processes to evade detection.

---

## DLL Injection Methods

### 1. LoadLibrary
Uses the `LoadLibrary` Windows API to load a DLL into a target process's address space by:
1. Opening a handle to the target process (`OpenProcess`)
2. Allocating memory in that process for the DLL path (`VirtualAllocEx`)
3. Writing the DLL path into that memory (`WriteProcessMemory`)
4. Getting the address of `LoadLibraryA` from `kernel32.dll` (`GetProcAddress`)
5. Creating a remote thread in the target starting at `LoadLibraryA` pointing to the DLL path (`CreateRemoteThread`)

**Limitation:** `LoadLibrary` usage is commonly monitored by security/anti-cheat solutions.

### 2. Manual Mapping
Advanced technique that avoids `LoadLibrary` entirely to evade detection:
1. Load DLL as raw data into the injecting process
2. Map DLL sections into the target process manually
3. Inject shellcode into the target — shellcode handles relocation, import fixing, TLS callbacks, and calls `DllMain`

### 3. Reflective DLL Injection
The DLL loads **itself** by implementing a minimal PE loader internally (`ReflectiveLoader` function). Process:
1. DLL is written into an arbitrary memory location in the host process
2. Execution transfers to the DLL's exported `ReflectiveLoader` function (via `CreateRemoteThread` or shellcode)
3. `ReflectiveLoader` calculates its own memory location and parses its own headers
4. Parses host's `kernel32.dll` exports to find `LoadLibraryA`, `GetProcAddress`, `VirtualAlloc`
5. Allocates a continuous memory region and loads its own image there
6. Processes its own import table — loads additional libraries, resolves function addresses
7. Processes its own relocation table
8. Calls its own `DllMain` with `DLL_PROCESS_ATTACH`

**Key advantage:** Minimal footprint, no dependency on `LoadLibrary`, avoids standard detection hooks.

Reference: [Stephen Fewer's ReflectiveDLLInjection](https://github.com/stephenfewer/ReflectiveDLLInjection)

---

## DLL Hijacking

### How It Works
Exploits the Windows DLL search order — if an app loads a DLL without specifying the full path, an attacker can plant a malicious DLL earlier in the search order.

### DLL Search Order

**Safe DLL Search Mode ENABLED (default):**
1. Directory the application loaded from
2. System directory (`C:\Windows\System32`)
3. 16-bit system directory
4. Windows directory
5. Current directory
6. `%PATH%` directories

**Safe DLL Search Mode DISABLED:**
1. Directory the application loaded from
2. **Current directory** ← moves up, making it more dangerous
3. System directory
4. 16-bit system directory
5. Windows directory
6. `%PATH%` directories

**Toggle via registry:**
`HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager`
→ `SafeDllSearchMode` = `1` (enabled) / `0` (disabled)

### Finding Hijack Targets
Use **Process Monitor (procmon)** or **Process Explorer**:
- Filter for the target process name
- Filter `Operation = Load Image` → see what DLLs are loaded and from where
- Filter `Path ends with .dll` + `Result = NAME NOT FOUND` → find DLLs the app searches for but can't find

---

## Exploitation Techniques

### Method 1 — DLL Proxying (Tampering with a Loaded DLL)
Plant a fake DLL that:
1. Loads the **original** DLL (renamed, e.g. `library.o.dll`)
2. Calls the original function
3. Modifies/tampers with the result
4. Returns the tampered result to the calling application

**Steps:**
- Rename original `library.dll` → `library.o.dll`
- Compile and place your proxy as `library.dll`

Example proxy code structure:
```c
DLL_EXPORT int Add(int a, int b) {
    HMODULE originalLibrary = LoadLibraryA("library.o.dll");
    AddFunc originalAdd = (AddFunc)GetProcAddress(originalLibrary, "Add");
    int result = originalAdd(a, b);
    result += 1;  // tamper
    return result;
}
```

### Method 2 — Replacing a Missing DLL (Invalid Library Hijack)
If procmon shows the app searching for a DLL that **doesn't exist** anywhere (result: `NAME NOT FOUND`), plant a malicious DLL at the first searched location (typically the app's directory).

The DLL just needs to be valid — it doesn't need to implement any specific functions. The `DllMain` entry point runs automatically when loaded:

```c
BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved) {
    switch (ul_reason_for_call) {
    case DLL_PROCESS_ATTACH:
        // payload executes here
        printf("Hijacked!\n");
        break;
    }
    return TRUE;
}
```

**Steps:**
- Identify missing DLL name and which directory is checked first
- Compile malicious DLL with that name, place in that directory
- Next time the app runs, your code executes in its context

---

## Key Takeaway
| Technique | Detection Difficulty | Use Case |
|---|---|---|
| LoadLibrary injection | Easily detected (monitored API) | Quick PoC |
| Manual Mapping | High evasion | Targeted/advanced attacks |
| Reflective DLL | Very high evasion | In-memory only, minimal footprint |
| DLL Proxying | Medium | Tamper with existing functionality |
| Missing DLL replacement | Low (depends on path) | Easy, no function signature needed |

For hijacking: always check `procmon` for `NAME NOT FOUND` on `.dll` files and writable directories early in the search order — these are the lowest-effort, highest-impact hijack opportunities.