## Overview

Enterprise network shares frequently contain files shared across teams. Due to poor access controls or careless user behavior, these shared folders often become a goldmine for attackers, housing plaintext credentials, database configs, unattended installation files, and setup scripts.

## High-Level Methodology

1. **Target Identification:** Determine high-value shares (e.g., IT, Engineering, or Admin shares over general user/media shares).
2. **Keyword & Pattern Localization:** Use localized keywords (`passw`, `user`, `token`, `key`, `secret`, `config`) and language-specific terms (e.g., _Benutzer_ in German environments).
3. **Automated Internal Scanning (Windows):** Run tools like **Snaffler** or **PowerHuntShares** directly from a domain-joined foothold to locate accessible shares and index sensitive file content.
4. **Remote Scanning (Linux):** Use external or containerized tools like **MANSPIDER** or **NetExec** via SMB to remotely sweep shares using valid credentials.
    
## Common Credential Patterns & File Extensions

- **Extensions to Target:** `.ini`, `.cfg`, `.env`, `.xlsx`, `.ps1`, `.bat`, `.config`, `.xml`
- **Naming Conventions:** Files containing terms like `config`, `cred`, `passw`, `setup`, or `initial`.
- **String Matching:** Search file contents or names for domain-specific references (e.g., `INLANEFREIGHT`) alongside terms like `password`, `secret`, or `apikey`.
    

## Tools and Techniques
### 1. Hunting from Windows
#### Snaffler
A C# program designed to run on domain-joined machines. It identifies readable shares and automatically parses files for sensitive regex patterns (passwords, keys, configs).
- **Basic Execution Command:**
    ```PowerShell
    Snaffler.exe -s
    ```
    
- **Helpful Flags:** `-u` (enumerate Active Directory users for cross-referencing), `-i` / `-n` (include or exclude specific shares).
    

#### PowerHuntShares

A PowerShell script used to automate SMB share enumeration, check permissions, identify high-risk excessive privileges, and generate an HTML summary dashboard.
- **Basic Execution Command:**
    ```PowerShell
    Invoke-HuntSMBShares -Threads 100 -OutputDirectory c:\Users\Public
    ```
    
### 2. Hunting from Linux
#### MANSPIDER
A Python tool (best run via Docker) that crawls SMB shares from Linux and downloads matching files to a local loot directory based on specified content strings.
- **Basic Execution Command:**
    ```Bash
    docker run --rm -v ./manspider:/root/.manspider blacklanternsecurity/manspider <IP> -c 'passw' -u '<username>' -p '<password>'
    ```

#### NetExec (`--spider`)
Leverages NetExec's built-in spidering features to search for patterns or file names across specific shares.
- **Basic Execution Command:**
    ```Bash
    nxc smb <IP> -u <username> -p '<password>' --spider IT --content --pattern "passw"
    ```

> **Engagement Tip:** Automated tools will frequently generate false positives due to broad regex matches. Always filter results by focusing on administrative shares (`IT`, `Finance`, `Sysvol`) first, and manually verify matches before attempting to use extracted credentials.