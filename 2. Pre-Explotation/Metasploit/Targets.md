# Summary: Metasploit Targets & Target Selection

## 🎯 Overview of Targets
- **Definition:** Targets are unique operating system identifiers derived from specific OS versions, service packs, or application variants that adapt an exploit module to run successfully on a specific system.
- **Commands:** 
  - `show targets`: Displays all available vulnerable targets for a specific exploit module (must be run *inside* an active module context).
```
msf6 exploit(windows/browser/ie_execcommand_uaf) > show targets
```


  - `set target <index_no>`: Manually selects a specific target profile (e.g., `set target 6` for IE 9 on Windows 7).
- **Automatic Detection:** Leaving the target set to `0 (Automatic)` prompts MSF to perform service detection on the target before executing the attack.

---

## 🔍 Best Practices & Module Auditing
- **The `info` Command:** Always run `info` on a new module before execution to inspect functionality, author credentials, required settings, and potential artifacts.
- **Code Safety:** Auditing code helps assure a safe, clean working environment and confirms there are no unwanted behaviors or hidden artifacts.

---

## ⚙️ Target Mechanics & Variables
- **Why Targets Vary:** Return addresses and parameters change based on factors such as:
  - Operating system versions and Service Packs.
  - Language packs (which shift memory addresses).
  - Software updates or hooked functions.
- **Return Address Types:** May utilize instructions like `jmp esp` or `pop/pop/ret` (commonly covered in stack-based buffer overflow modules).
- **Manual Target Identification:** When dealing with custom or unlisted environments, a pentester may need to:
  1. Obtain a copy of the target binaries.
  2. Use `msfpescan` to locate a suitable return address.