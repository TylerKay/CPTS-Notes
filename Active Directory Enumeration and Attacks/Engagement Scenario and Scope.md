# AD Enumeration & Attacks — Engagement Scenario & Scoped

## Engagement Context
Simulated internal penetration test against **Inlanefreight** for CAT-5 Security.

**Assessment goals (from tasking email):**
1. Domain enumeration
2. Credential discovery
3. Lateral movement
4. Privilege escalation
5. Acquiring Domain Admin credentials

**Two assessment phases:**
1. Starting from an **external breach position** (simulating an external attacker who gained initial access)
2. Starting from an **attack box inside the internal network** (simulating an insider/already-breached position)

---

## Scope

### In Scope
| Range/Domain | Description |
|---|---|
| `INLANEFREIGHT.LOCAL` | Primary customer domain (AD + web services) |
| `LOGISTICS.INLANEFREIGHT.LOCAL` | Customer subdomain |
| `FREIGHTLOGISTICS.LOCAL` | Subsidiary company; external forest trust with INLANEFREIGHT.LOCAL |
| `172.16.5.0/23` | In-scope internal subnet |

### Out of Scope
- Any other subdomains of `INLANEFREIGHT.LOCAL`
- Any subdomains of `FREIGHTLOGISTICS.LOCAL`
- Phishing or social engineering attacks
- Any IPs/domains/subdomains not explicitly listed
- Active attacks against the real-world `inlanefreight.com` website (passive enumeration only)

---

## Authorized Methods

### External Information Gathering (Passive Only)
- Passive OSINT from an **anonymous, unauthenticated internet perspective**.
- No advance information beyond what's in scope documentation.
- Open-source enumeration only — no active scans, no port scanning, no attacks against internet-facing IPs or `https://www.inlanefreight.com`.

### Internal Testing
- Starts from **no credentials, anonymous position** on the internal network.
- Goal: obtain domain user credentials → enumerate the domain → gain foothold → lateral + vertical movement → full compromise of all in-scope internal domains.
- **No intentional disruption** of computer systems or network operations during the test.

### Password Testing
- Captured password files may be loaded offline for cracking.
- Cracked passwords and captured hashes are not to be shared outside the assessment team.
- All data stored securely on CAT-5-owned systems for the retention period defined in the contract.

---

## Key Concepts Covered in This Module
- Core AD enumeration (manual + automated)
- Common AD attack techniques in depth
- Tool proficiency: BloodHound, Responder, Kerbrute, CrackMapExec, Impacket, Mimikatz, Rubeus, etc.
- Interpreting gathered data to make critical decisions and advance the assessment
- Primer for more advanced AD-focused topics (covered in later modules)

---

## Lab Connectivity

**RDP to Windows attack host (MS01):**
```bash
xfreerdp /v:<MS01_IP> /u:htb-student /p:Academy_student_AD!
```

**SSH to Parrot Linux attack host (ATTACK01):**
```bash
ssh htb-student@<ATTACK01_IP>
```

**RDP to ATTACK01 (BloodHound GUI):**
```bash
xfreerdp /v:<ATTACK01_IP> /u:htb-student /p:HTB_@cademy_stdnt!
```

> Allow 3–5 minutes for labs to fully spawn. Spawn the lab first, then read through the material.