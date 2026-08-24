# Hyper-V Administrators — Windows PrivEsc

## Background
- Full access to all **Hyper-V features**.
- **If Domain Controllers are virtualized**, Hyper-V Administrators should be treated as **Domain Admins** — they can:
  - Clone a live DC
  - Mount its virtual disk offline
  - Extract `NTDS.dit`
  - Pull NTLM hashes for every domain user

---

## Exploit — Hyper-V Admin to SYSTEM (Hard Link Abuse)

### Root Cause
- Well documented on [decoder.cloud](https://decoder.cloud/2020/01/20/from-hyper-v-admin-to-system/).
- When a VM is **deleted**, `vmms.exe` attempts to restore original file permissions on the corresponding `.vhdx` file.
- Critically, it does this **as `NT AUTHORITY\SYSTEM`**, and **does not impersonate the user** during the operation.
- **Abuse:** Delete the `.vhdx` file, then create a **native hard link** pointing that path to a **protected SYSTEM file** — `vmms.exe`'s permission-restore logic then grants full permissions on the linked (target) file to the attacker.

### Related CVEs
If the target OS is vulnerable to either of these, they can be leveraged directly for SYSTEM privileges:
- **CVE-2018-0952**
- **CVE-2019-0841**

If not vulnerable to those, target an **installed application with a SYSTEM-context service that unprivileged users can start**.

---

## Exploitation Walkthrough — Mozilla Maintenance Service Example

### Target File
```
C:\Program Files (x86)\Mozilla Maintenance Service\maintenanceservice.exe
```
- Firefox installs the **Mozilla Maintenance Service**, which runs as SYSTEM and is startable by unprivileged users — a good hard-link target.

### Step 1 — Run the hard link PoC
Use/update the PoC script (NT hard link technique) to grant your current user **full permissions** on the target file:
```
https://raw.githubusercontent.com/decoder-it/Hyper-V-admin-EOP/master/hyperv-eop.ps1
```

### Step 2 — Take ownership of the file
```cmd
takeown /F "C:\Program Files (x86)\Mozilla Maintenance Service\maintenanceservice.exe"
```

### Step 3 — Replace the file and trigger execution
Replace `maintenanceservice.exe` with a malicious binary, then start the service:
```cmd
sc.exe start MozillaMaintenance
```
→ Executes the malicious binary **as SYSTEM**.

---

## ⚠️ Patch Status
This vector has been **mitigated by the March 2020 Windows security updates**, which changed hard link behavior. Verify patch level before assuming this technique will work.

---

## Key Takeaway
Hyper-V Administrators is a high-value group: direct **Domain Admin equivalence** if DCs are virtualized (clone + extract NTDS.dit offline), and a **local SYSTEM privesc path** via `vmms.exe`'s unsafe hard-link permission-restore behavior when deleting a `.vhdx` — targetable against any SYSTEM-context service binary an unprivileged user can start (e.g. Mozilla Maintenance Service), unless patched post–March 2020.