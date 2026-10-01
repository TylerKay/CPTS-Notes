
**Kerberoasting** is an Active Directory lateral movement and privilege escalation technique that targets accounts configured with **Service Principal Names (SPNs)**.

Because standard service accounts run in the context of domain user accounts (rather than `NT AUTHORITY\LOCAL SERVICE`) to overcome network authentication limits, any domain user can request a Kerberos ticket (TGS-REP) for them. Although obtaining the ticket doesn't grant immediate execution rights, the ticket is encrypted with the service account's NTLM hash. If the service account utilizes a weak password, operators can subject the ticket to an **offline brute-force attack** (e.g., using Hashcat) to recover the cleartext password. Successful cracking often yields high privileges, such as local administrator access across multiple servers or outright Domain Admin rights.

> **Note:** A prerequisite to performing Kerberoasting attacks is either domain user credentials (cleartext or just an NTLM hash if using Impacket), a shell in the context of a domain user, or account such as SYSTEM. Once we have this level of access, we can start. We must also know which host in the domain is a Domain Controller so we can query it.

### Methodology & Step-by-Step Process
#### Step 1: Install Impacket Toolkit

Ensure you have the Impacket toolkit installed on your Linux attack host to utilize its built-in Active Directory utilities. We can grab from [Here](https://github.com/SecureAuthCorp/impacket).
- Clone or update Impacket and install it:
    ```bash
    sudo python3 -m pip install .
    ```
#### Step 2: Enumerate SPN Accounts (`GetUserSPNs.py`)
Query the domain controller using valid domain user credentials to identify accounts associated with SPNs and inspect their group memberships.
- Run discovery against the target domain controller:
    ```bash
    GetUserSPNs.py -dc-ip 172.16.5.5 INLANEFREIGHT.LOCAL/forend
    ```
#### Step 3: Request and Save TGS Tickets
Request the TGS tickets for all eligible SPN accounts or a targeted service account, saving the output directly into a file for offline cracking.
- Request a single target account ticket and write it to a file:
    ```bash
    GetUserSPNs.py -dc-ip 172.16.5.5 INLANEFREIGHT.LOCAL/forend -request-user sqldev -outputfile sqldev_tgs
    ```

#### Step 4: Crack the Ticket Offline (`Hashcat`)
Use Hashcat with the appropriate hash mode (`13100` for Kerberos 5 TGS-REP etype 23) alongside a wordlist to recover the account's cleartext password.
- Execute Hashcat against the saved ticket:
    ```bash
    hashcat -m 13100 sqldev_tgs /usr/share/wordlists/rockyou.txt
    ```
#### Step 5: Validate Recovered Credentials
Confirm the validity and privilege level of the cracked credentials against the domain controller.
- Test authentication and check for administrative rights (`Pwn3d!`):
    ```bash
    sudo crackmapexec smb 172.16.5.5 -u sqldev -p database!
    ```
> **Note:** Kerberoasting efficacy heavily depends on password strength. If an organization enforces strong, complex passwords, tickets may remain uncrackable even after extensive GPU brute-forcing, requiring adjustments to the finding's risk rating in your report.