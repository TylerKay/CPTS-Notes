# Windows Privileges Overview

## Core Concepts

**Privileges** vs **Access Rights**:
- **Privileges** = rights granted to an account to perform system-level operations (manage services, load drivers, shut down system, debug applications, etc.)
- **Access rights** = used by the system to grant/deny access to specific securable objects (files, folders, etc.)

- User/group privileges are stored in a database and granted via an **access token** at logon.
- An account can have different privileges on different systems (varies by local vs. domain context).
- Every privileged action triggers a check against the access token: is the privilege **assigned**, and if so, is it **enabled**?
- **Most privileges are disabled by default** — some require an elevated console, others need manual enabling.

---

## Windows Authorization Process

**Security principals** = anything the OS can authenticate (user/computer accounts, processes running in a security context, security groups).
- Every security principal has a unique, permanent **Security Identifier (SID)**.

### Access Control Flow
1. User attempts to access a securable object (e.g. a file share folder).
2. Their **access token** (user SID, group SIDs, privilege list, extra access info) is compared against the object's **security descriptor**.
3. Security descriptor contains: Object Owner SID, Group SID, **SACL** (audit rules), **DACL** (Access Control Entries defining who can access what).
4. System checks ACEs until a match is found → grants or denies access.

> This process is where privesc attacks insert themselves — abusing rights or manipulating this comparison to gain unauthorized access.

---

## High-Value Windows Groups

Membership in these groups can lead to Domain Admin, local admin, or SYSTEM privileges:

| Group | Abuse Potential |
|---|---|
| **Default Administrators** (Domain Admins / Enterprise Admins) | "Super" groups — full control |
| **Server Operators** | Modify services, access SMB shares, backup files |
| **Backup Operators** | Local logon to DCs — effectively Domain Admin. Can shadow-copy SAM/NTDS, remotely read registry, access DC filesystem via SMB |
| **Print Operators** | Local DC logon — can trick Windows into loading a malicious driver |
| **Hyper-V Administrators** | If virtual DCs exist, treat as Domain Admin equivalent |
| **Account Operators** | Modify non-protected accounts/groups in the domain |
| **Remote Desktop Users** | No inherent perms by default, but often granted RDP login rights — lateral movement vector |
| **Remote Management Users** | Can PSRemote into DCs |
| **Group Policy Creator Owners** | Create new GPOs (needs additional delegation to link them) |
| **Schema Admins** | Modify AD schema — can backdoor future GPOs/groups via default object ACLs |
| **DNS Admins** | Can load a DLL on a DC (persistence via reboot-triggered load); more reliable exploit = creating a **WPAD record** |

---

## Key User Rights Assignments

Local (or domain-applied) rights granted via group membership or Group Policy. Ref: Microsoft's User Rights Assignment docs.

| Setting Constant | Setting Name | Standard Assignment | Description |
|---|---|---|---|
| `SeNetworkLogonRight` | Access this computer from the network | Administrators, Authenticated Users | Governs network-based connections (SMB, NetBIOS, CIFS, COM+) |
| `SeRemoteInteractiveLogonRight` | Allow log on through RDP | Administrators, Remote Desktop Users | Controls RDP login screen access |
| `SeBackupPrivilege` | Back up files and directories | Administrators | Bypass file/registry/object permissions for backup purposes |
| `SeSecurityPrivilege` | Manage auditing and security log | Administrators | Set audit options (SACLs); view/clear Security event log |
| `SeTakeOwnershipPrivilege` | Take ownership of files/objects | Administrators | Take ownership of any securable object |
| `SeDebugPrivilege` | Debug programs | Administrators | Attach to/open **any** process — access to sensitive OS components |
| `SeImpersonatePrivilege` | Impersonate a client after authentication | Administrators, Local Service, Network Service, Service | Allows programs to impersonate a user/account — **key privesc target (Potato exploits)** |
| `SeLoadDriverPrivilege` | Load and unload device drivers | Administrators | Drivers run as highly privileged code |
| `SeRestorePrivilege` | Restore files and directories | Administrators | Bypass permissions when restoring; can set security principals as object owner |
| `SeTcbPrivilege` | Act as part of the operating system | Administrators, Local Service, Network Service, Service | Assume identity of any user — reserved for legitimate service accounts (AV/backup tools) |

---

## Checking Your Privileges

```powershell
whoami /priv
```
- Lists all privileges assigned to the current user and their state (**Enabled**/**Disabled**).
- Some privileges only appear/are usable in an **elevated** console (UAC-restricted).
- A privilege shown as **Disabled** means it's assigned but not currently usable — no built-in Windows command enables it; requires scripting (custom PowerShell scripts exist for adjusting token privileges).

### Example — Elevated Local Admin
```
whoami
# winlpe-srv01\administrator

whoami /priv
```
Shows the **full privilege set** available to admins when running elevated — including `SeDebugPrivilege`, `SeBackupPrivilege`, `SeTakeOwnershipPrivilege`, `SeImpersonatePrivilege` (Enabled), etc.

### Example — Standard User
```
whoami
# winlpe-srv01\htb-student

whoami /priv
```
```
Privilege Name                State
SeChangeNotifyPrivilege       Enabled
SeIncreaseWorkingSetPrivilege Disabled
```
- Drastically fewer rights than admin.

### Example — Backup Operators Group Member
```
Privilege Name          State
SeShutdownPrivilege     Disabled
SeChangeNotifyPrivilege Enabled
```
- Notably has `SeShutdownPrivilege` — if logged onto a **domain controller locally** (not RDP/WinRM), this user could shut it down, causing a major service outage.

---

## Detection Notes
- **Event 4672**: "Special privileges assigned to new logon" — fires when sensitive privileges are assigned to a new logon session.
- Can be tuned to alert on:
  - Privileges that should **never** be assigned
  - Privileges assigned to accounts that **shouldn't** have them

---

## Key Takeaway
Group membership and assigned user rights are a major, often-overlooked privesc and lateral movement surface. It's common to find low-privileged users unintentionally added to powerful groups (Backup Operators, DNS Admins, etc.). Both attackers and defenders should regularly audit membership in these groups and correlate against `whoami /priv` output to catch dangerous misconfigurations.