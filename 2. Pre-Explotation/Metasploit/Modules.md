# Summary: Metasploit Modules, Searching, and Execution

## 🧩 Overview of Metasploit Modules
- **Nature of Modules:** Pre-developed, tested proof-of-concept (PoC) scripts designed for specific pentesting tasks.
- **Role of Automation:** Exploit failures indicate that an exploit needs manual customization or target tuning—not necessarily that the vulnerability doesn't exist. Metasploit serves as a support tool, not a substitute for manual skills.
- **Module Path Syntax:** `<No.> <type>/<os>/<service>/<name>` (e.g., `794   exploit/windows/ftp/scriptftp_list`).

### Module Types
| Type | Description |
| :--- | :--- |
| **Auxiliary** | Scanning, fuzzing, sniffing, and administrative capabilities. |
| **Encoders** | Ensure payloads remain intact to their destination. |
| **Exploits** | Exploit vulnerabilities to facilitate payload delivery. |
| **NOPs** | Keep payload sizes consistent across exploit attempts. |
| **Payloads** | Code that runs remotely and calls back to the attacker machine (shell/meterpreter). |
| **Plugins** | Additional scripts integrated within msfconsole. |
| **Post** | Gathers information, handles pivoting, and post-exploitation tasks. |

---

## 🔍 Searching for Modules
Use the `search` command inside `msfconsole` with custom filters and keywords (e.g., `cve`, `platform`, `type`, `rank`).
- **Examples:**
  - `search eternalromance`
  - `search type:exploit platform:windows cve:2021 rank:excellent microsoft`
- **Helpful Search Options:**
  - `-S <string>`: Filter using regex patterns.
  - `-s <column>`: Sort results (e.g., by rank or date).
  - `-r`: Reverse search results order.

---

## ⚙️ Selecting and Configuring Modules
1. **Selection:** Use `use <index_no>` or `use <module_path>` after running a search (e.g., `use 0`).
2. **Reviewing Options:** Run `options` to see required parameters (marked with `yes` under the **Required** column).
3. **Module Info:** Run `info` to inspect metadata, targets, authors, and references.
4. **Setting Variables:**
   - `set <OPTION> <VALUE>`: Sets configuration for the current module session.
   - `setg <OPTION> <VALUE>`: Globally sets options to persist across module changes until restart (e.g., setting `RHOSTS` or `LHOST`).

---

## 🚀 Execution & Interaction
- **Launch Attack:** Run the `run` or `exploit` command once all parameters (such as `RHOSTS` and `LHOST`) are configured.
- **Session Handling:** Upon successful exploitation, a session (such as a Meterpreter or command shell) opens, allowing direct interaction with the target (e.g., checking privileges via `whoami` returning `nt authority\system`).