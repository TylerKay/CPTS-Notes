# Legacy Operating Systems — Windows PrivEsc Context

## Why Legacy Systems Matter
Large organizations (universities, hospitals, insurance, utilities, local/state government) frequently run end-of-life Windows systems due to cost, personnel constraints, or mission-critical software tied to unsupported OS versions. These systems are often wide-open to unpatched RCE and local privesc vulnerabilities — but always verify with the client that a system is not fragile/mission-critical before attacking it.

---

## Windows Desktop — EOL Dates

| Version | EOL Date |
|---|---|
| Windows XP | April 8, 2014 |
| Windows Vista | April 11, 2017 |
| Windows 7 | January 14, 2020 |
| Windows 8 | January 12, 2016 |
| Windows 8.1 | January 10, 2023 |
| Windows 10 (1507) | May 9, 2017 |
| Windows 10 (1703) | October 9, 2018 |
| Windows 10 (1809) | November 10, 2020 |
| Windows 10 (1903) | December 8, 2020 |
| Windows 10 (1909) | May 11, 2021 |
| Windows 10 (2004) | December 14, 2021 |
| Windows 10 (20H2) | May 10, 2022 |

## Windows Server — EOL Dates

| Version | EOL Date |
|---|---|
| Windows Server 2003 | April 8, 2014 |
| Windows Server 2003 R2 | July 14, 2015 |
| Windows Server 2008 | January 14, 2020 |
| Windows Server 2008 R2 | January 14, 2020 |
| Windows Server 2012 | October 10, 2023 |
| Windows Server 2012 R2 | October 10, 2023 |
| Windows Server 2016 | January 12, 2027 |
| Windows Server 2019 | January 9, 2029 |

> Full EOL list including Exchange, SQL Server, and Office: [Microsoft Lifecycle Policy](https://docs.microsoft.com/en-us/lifecycle/)

---

## Impact of EOL Systems

| Issue | Description |
|---|---|
| Software support ends | Browsers and essential apps may stop working |
| Hardware issues | Newer hardware components stop functioning |
| **Security flaws** | No security updates released — RCE and privesc vulnerabilities remain permanently unpatched |

**Notable examples of severe unpatched legacy flaws:**
- [CVE-2020-1350 (SIGRed)](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2020-1350) — wormable DNS vulnerability
- [CVE-2017-0144 (EternalBlue / MS17-010)](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2017-0144) — wormable SMBv1 RCE, affected hospitals and critical infrastructure worldwide

---

## Practical Assessment Notes

- **Server 2003 and 2008** hosts are still commonly encountered — often vulnerable to multiple RCE and local privesc flaws, and useful as footholds into the environment.
- **Windows XP / Server 2000** are rare but exist — especially in medical and government settings.
- Legacy systems often run older OS versions because vendor support for a critical application ended — the org is stuck until they can migrate.
- **Recommended client guidance when found:** strict network segmentation to isolate legacy systems until they can be properly retired or upgraded.
- Legacy systems lack many security protections present in modern Windows versions, making privesc significantly easier.

> ⚠️ Always confirm with the client before attacking legacy hosts — they may be running mission-critical workloads where a crash or instability could cause a major outage.