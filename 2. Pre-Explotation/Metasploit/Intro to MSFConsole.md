## 🖥️ Launching MSFconsole
- **Execution:** Type `msfconsole` in your preferred terminal (preinstalled on security distros like Parrot Security and Kali Linux).
- **Startup Options:** 
  - Standard launch displays the iconic ASCII art splash screen and framework statistics.
  - Using `msfconsole -q` launches the console quietly without displaying the banner.
- **Help & Management:** Use the `help` command inside the console to view all available commands.

---

## 🔄 Updating Metasploit
- **Modern Method:** Managed directly via the system package manager using `apt`:
  ```bash
  sudo apt update && sudo apt install metasploit-framework