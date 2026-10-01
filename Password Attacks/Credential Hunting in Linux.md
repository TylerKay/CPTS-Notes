## Overview

Once access is gained to a Linux system (e.g., via a reverse shell or low-privileged account), credential hunting is a vital step toward local privilege escalation. Sources of credentials are generally categorized into four core areas: **Files**, **History**, **Memory**, and **Key-rings/Browsers**.

## High-Level Methodology

1. **Understand System Context:** Determine the machine's role and purpose in the network (e.g., standard workstation vs. isolated database server).
    
2. **Enumerate Files:** Search configuration files, databases, personal notes, scripts, cron jobs, and SSH keys.
    
3. **Check History & Logs:** Inspect command histories (`.bash_history`) and system log files for hardcoded credentials or accidental command-line secrets.
    
4. **Leverage Memory & Automated Tools:** Use tools like **LaZagne** or **mimipenguin** (with root privileges) to dump secrets stored in memory.
    
5. **Target Application Credential Stores:** Extract browser-saved credentials (e.g., `logins.json` via **Firefox Decrypt**).
    

## 1. Files
Because "everything is a file" in Linux, search systematically through key file categories:
- **Configuration Files (`.conf`, `.config`, `.cnf`):** Contain service settings and sometimes hardcoded credentials.
    ```Bash
    for l in $(echo ".conf .config .cnf"); do echo -e "\nFile extension: " $l; find / -name *$l 2>/dev/null | grep -v "lib\|fonts\|share\|core"; done
    ```
- **Databases:** Search for SQLite or local database files (`.db`, `.sql`).
- **Notes & Text Files:** Look for stray `.txt` files or extension-less notes in user directories.
    ```Bash
    find /home/* -type f -name "*.txt" -o ! -name "*.*"
    ```
- **Scripts:** Inspect custom shell (`.sh`), Python (`.py`), or Perl (`.pl`) scripts that may contain embedded credentials used for automated tasks.
- **Cronjobs:** Inspect system-wide and user-level cron configurations (`/etc/crontab`, `/etc/cron.d/`) where scripts might execute with hardcoded passwords.
    
## 2. History & Logs

- **Shell History:** Check `.bash_history` for cleartext credentials passed via command-line arguments.
    ```Bash
    tail -n5 /home/*/.bash*
    ```
- **Log Files:** Examine important log files in `/var/log/` (e.g., `syslog`, `auth.log`, `messages`) using filters for failed logins, sudo usage, or ssh activity.
## 3. Memory & Cache

- **Mimipenguin:** Can extract cleartext credentials from memory for specific running processes (requires root/sudo).
    
    ```bash
    sudo python3 mimipenguin.py
    ```

## 4. Key-rings & Browser Credentials

- **LaZagne (Linux Version):** Scans for Wi-Fi configurations, git tokens, AWS keys, and browser data.
    
    ```Bash
    sudo python3 laZagne.py all
    ```
- **Browser Profiles (Firefox/Chromium):** Firefox stores encrypted credentials in `logins.json`. Use **Firefox Decrypt** to recover plaintext passwords.
    
    ```Bash
    python3.9 firefox_decrypt.py
    ```

> **Engagement Tip:** Always tailor your search based on the access level you have. Tools like `mimipenguin` and `LaZagne` require administrative or root privileges to yield full results, whereas file and history enumeration can often be performed as a low-privileged user.