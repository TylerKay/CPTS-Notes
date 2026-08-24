# Introduction to Active Directory Enumeration & Attacks

## What is Active Directory?
- Directory service for Windows enterprise environments — introduced with Windows Server 2000, incrementally improved since.
- Based on **x.500** and **LDAP** protocols.
- Distributed, hierarchical structure for centralized management of: users, computers, groups, network devices, file shares, Group Policy Objects (GPOs), and trust relationships.
- Provides **authentication, accounting, and authorization** within Windows enterprise environments.

---

## Why AD Matters for Attackers
- AD holds approximately **43% of the enterprise Identity & Access Management market share**.
- Microsoft has had **2,000+ CVEs** reported in just the last two years tied to AD.
- AD's core purpose — making information easy to find and access — makes it inherently difficult to fully harden.
- Common misconfigurations in services and permissions, combined with user/OS vulnerabilities, create ideal attacker conditions.

**Attack techniques covered:**
- Password spraying
- Kerberoasting
- Responder / hash capture
- BloodHound enumeration
- Pass-the-ticket
- DCSync
- Shadow Credentials

---

## Real-World Attack Scenarios

### Scenario 1 — Waiting on an Admin
1. Compromised a domain-joined host → SYSTEM access → domain enumeration.
2. Kerberoasting → retrieved TGS tickets → overnight Hashcat crack with `d3ad0ne` rule → cracked one ticket.
3. Used the cracked account's write access to file shares → dropped SCF files → Responder captured a NetNTLMv2 hash.
4. BloodHound revealed the hash belonged to a **Domain Admin** → full domain compromise.

**Key lessons:** Patience pays off; chained low-priv access through share write permissions + SCF + Responder = DA.

### Scenario 2 — Spraying the Night Away
1. SMB NULL session via **enum4linux** → full user list + password policy.
2. Careful password spraying (staying within lockout threshold) → hit on `Spring@18`.
3. BloodHound → account had local admin on hosts where a DA had active sessions.
4. **Rubeus** → extracted Kerberos TGT for the DA → pass-the-ticket.
5. Bonus: DA group membership was nested into the trusting domain's Administrators group → **cross-domain compromise** with same credentials.

**Key lessons:** Always retrieve password policy before spraying; understand seasonal/common password patterns; BloodHound reveals trust paths.

### Scenario 3 — Fighting in the Dark (No Foothold)
1. Username enumeration via **Kerbrute** + **linkedin2username** + statistically-likely-usernames list → 516 valid users.
2. Careful spray with `Welcome2021` → single hit.
3. BloodHound → all domain users had RDP to one host → logged in → used **DomainPasswordSpray** (removes locked accounts automatically) → spray `Fall2021` → multiple hits.
4. One hit account was in **Help Desk** group → **GenericAll** over Enterprise Key Admins group → GenericAll over a DC.
5. Added account to Enterprise Key Admins → **Shadow Credentials attack** → NT hash for DC machine account.
6. **DCSync** → NTLM hashes for all domain users.

**Key lessons:** Username enumeration before spraying; iterative escalation through group rights (GenericAll chains); Shadow Credentials + DCSync for full domain.

---

## Core Mindset
- **Iterative enumeration** — revisit, adapt, chain findings together.
- **Know the "why"** behind each flaw — makes you a better attacker and enables actionable remediation advice.
- **Living off the land** — must operate effectively with built-in Windows tools and limited toolsets when customized attack VMs aren't available.
- **Both Windows and Linux** — be comfortable enumerating and attacking from either platform.

---

## Lab Setup Notes

**RDP to Windows attack host (MS01):**
```bash
xfreerdp /v:<MS01_IP> /u:htb-student /p:Academy_student_AD!
```

**SSH to Parrot Linux attack host (ATTACK01):**
```bash
ssh htb-student@<ATTACK01_IP>
```

**RDP to ATTACK01 (for BloodHound GUI):**
```bash
xfreerdp /v:<ATTACK01_IP> /u:htb-student /p:HTB_@cademy_stdnt!
```

- Windows tools: `C:\Tools`
- Linux tools: installed in PATH or `/opt`
- Allow 3–5 minutes for labs to fully spawn — click to spawn before reading through the section material.

---

## Key Takeaway
AD's complexity and the ease with which information can be accessed within it make it one of the most target-rich environments in enterprise security. Mastery comes from iterative practice — understanding the fundamentals of authentication, authorization, trusts, and group permissions, then chaining misconfigurations together. No single attack wins the domain; **the chain matters**.