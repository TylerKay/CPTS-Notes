# Situational Awareness (Windows PrivEsc)

Orienting yourself on a newly-landed host is critical before proceeding — understanding network position and active protections shapes which tools/techniques will actually work.

## Why It Matters
- Identifies other reachable hosts (potential lateral movement / dual-homed hosts)
- Reveals protections that need bypassing
- Flags tools that won't work against this specific target
- Informs whether to escalate here or pivot elsewhere first

---

## Network Information

### Key Concept: Dual-Homed Hosts
A host belonging to **two or more networks** (multiple NICs) may open lateral movement paths not previously accessible from the attack position.

### Interfaces, IPs, DNS
```cmd
ipconfig /all
```
- Reveals all interfaces, IP addresses, DNS servers, DHCP status, DNS suffix (useful for spotting AD domain membership).

### ARP Cache
```cmd
arp -a
```
- Shows recently-contacted hosts per interface.
- Useful hint for identifying hosts admins frequently connect to (e.g. via RDP/WinRM) — valuable for lateral movement planning post-credential-theft.

### Routing Table
```cmd
route print
```
- Shows local network routes, gateways, and reachable subnets (IPv4 + IPv6).
- Helps map out what other network segments this host can reach.

### Additional Domain Info (if AD-joined)
- Also worth gathering: domain controller IPs, local domain name — useful for later AD-focused attacks.

---

## Enumerating Protections

### Why Enumerate First
Modern environments typically run AV/EDR that can interfere with enumeration and block common privesc tools/PoCs. Knowing what's in place before running tools helps you:
- Avoid detection/blocking
- Decide when to modify/obfuscate a tool before use
- Understand whether specific binaries (e.g. `net.exe`, `tasklist`) are restricted or flagged

### Check Windows Defender Status
```powershell
Get-MpComputerStatus
```
Key fields to review:
- `AntivirusEnabled`, `RealTimeProtectionEnabled`, `BehaviorMonitorEnabled`, `IoavProtectionEnabled`, `OnAccessProtectionEnabled`
- All `False` in the above (as in the example) indicates weakened/disabled real-time protections — favorable for tool usage.

### Application Whitelisting (AppLocker)
Used by orgs to restrict which apps/file types users can execute (e.g. blocking `cmd.exe`/`powershell.exe` for non-admins).

**List effective AppLocker policy:**
```powershell
Get-AppLockerPolicy -Effective | select -ExpandProperty RuleCollections
```
- Shows rule collections: publisher conditions, path conditions, allow/deny actions, and which group (`UserOrGroupSid`) each rule applies to.
- Default rules commonly allow: signed packaged apps, anything in `%PROGRAMFILES%`, anything in `%WINDIR%`, and (for local Administrators) everything.

**Test whether a specific action would be blocked:**
```powershell
Get-AppLockerPolicy -Local | Test-AppLockerPolicy -path C:\Windows\System32\cmd.exe -User Everyone
```
Example result:
```
FilePath                    PolicyDecision MatchingRule
--------                    -------------- ------------
C:\Windows\System32\cmd.exe         Denied c:\windows\system32\cmd.exe
```
- Confirms `cmd.exe` is blocked for the `Everyone` group under this policy — informs whether an AppLocker bypass is needed before proceeding.

---

## Key Takeaway
Before diving into privesc technique enumeration, always establish:
1. **Network context** — interfaces, routes, ARP cache, dual-homing potential
2. **Protection posture** — AV/EDR status, AppLocker rules and whether specific binaries/paths are blocked

This context determines which tools are safe/viable to use and whether a bypass step is required first.