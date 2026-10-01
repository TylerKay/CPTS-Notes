# Summary: Writing, Importing, and Porting Metasploit Modules

## 📥 Importing External Modules
- **Source Selection:** Search ExploitDB via the web interface (using the `MSF` tag filter) or use the command line tool `searchsploit` (`searchsploit -t <name> --exclude=".py"`).
- **Directory Paths:**
  - System-wide default directory: `/usr/share/metasploit-framework/`
  - Local hidden configuration directory: `~/.msf4/` (create matching folder structures if missing).
- **Naming Conventions:** Always use **snake-case**, alphanumeric characters, and underscores instead of dashes (e.g., `nagios3_command_injection.rb`).
- **Loading Modules in `msfconsole`:**
  - Via command: `loadpath /usr/share/metasploit-framework/modules/`
  - Via command: `reload_all`

---

## 🧩 Porting Scripts to Metasploit Modules
- **Prerequisites:** Basic knowledge of Ruby and the use of hard tabs for indentation.
- **Boilerplate Approach:** Take an existing module from the target category, review its mixins, and adapt it for the custom script.

### Key Ruby Mixins
| Mixin / Class | Purpose |
| :--- | :--- |
| **`Msf::Exploit::Remote::HttpClient`** | Provides HTTP client methods for attacking web servers. |
| **`Msf::Exploit::PhpEXE`** | Generates and handles first-stage PHP payloads. |
| **`Msf::Exploit::FileDropper`** | Manages file transfers and automated clean-up post-session. |
| **`Msf::Auxiliary::Report`** | Reports and logs scan/exploit data directly into the MSF database. |

---

## 📋 Module Anatomy Quick Reference
1. **Metadata & Info Header:** Define the module `Name`, `Description`, `License`, `Author`, `References` (CVE, URL), `Platform`, `Arch`, and `DisclosureDate`.
2. **Options Setup (`register_options`):** Configure required parameters such as `TARGETURI`, user credentials, or file paths (`OptPath`).
3. **Execution Logic:** Implement the custom exploit workflow using Metasploit libraries and classes.