# Summary: Metasploit Databases and Data Management

## 🗄️ Overview of Databases in Metasploit
- **Purpose:** Built-in PostgreSQL support helps organize complex assessments, keeping track of scan results, discovered hosts, open ports, extracted credentials, and loot.
- **Workflow Benefits:** Allows importing/exporting scan data (e.g., Nmap XML), running built-in scans via `db_nmap`, and dynamically feeding target data directly into exploit parameters.

---

## ⚙️ Initializing and Managing the Database
1. **Check Service Status:**
   ```bash
   sudo service postgresql status
   # OR
   sudo msfdb status
   ```

2. **Start PostgreSQL & Initialize MSF Database:**
    
    Bash
    
    ```
    sudo systemctl start postgresql
    sudo msfdb init
    ```
    
3. **Launch MSFconsole with Database Integration:**
    
    Bash
    
    ```
    sudo msfdb run
    ```
    
4. **Verify Connection Inside MSF:**
    
    Plaintext
    
    ```
    msf6 > db_status
    ```
    

## 📁 Organizing with Workspaces

Workspaces act like project folders to separate findings by IP, subnet, or network.

- **List Workspaces:** `workspace`
    
- **Add a Workspace:** `workspace -a <name>`
    
- **Switch Workspace:** `workspace <name>`
    
- **View Help Options:** `workspace -h`
    

## 🔍 Importing and Scanning Data
- **Import Nmap Scans:**
    Plaintext
    ```
    msf6 > db_import Target.xml
    ```
- **Run Nmap Directly from MSF:**
    Plaintext
    ```
    msf6 > db_nmap -sV -sS 10.10.10.8
    ```
- **Backup/Export Data:**
    Plaintext
    ```
    msf6 > db_export -f xml backup.xml
    ```
## 📋 Core Database Commands Reference

| **Command**    | **Description**                                                                                                                  |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| **`hosts`**    | Lists discovered hosts; supports flags for searching, filtering (`-S`), setting `RHOSTS` (`-R`), and tagging.                    |
| **`services`** | Lists open ports and services across targets; allows filtering by port (`-p`) or protocol (`-r`).                                |
| **`creds`**    | Manages harvested credentials, hashes (NTLM, MD5), and SSH keys. Supports manual addition and filtering (e.g., `creds -t NTLM`). |
| **`loot`**     | Manages captured files, hash dumps, and local data artifacts gathered during post-exploitation.                                  |
```
msf6 > creds -h
msf6 > loot -h
```