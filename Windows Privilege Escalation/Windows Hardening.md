# Windows Hardening — Key Measures

## 1. Secure Clean OS Installation
- Build a **custom image** for your environment using a clean OS ISO + Windows Deployment Services (WDS) or SCCM.
- The base image should include: required apps, pre-tested security configurations, and current updates.
- Eliminates vendor bloatware, ensures consistent baseline across all hosts, and simplifies troubleshooting/updates.

---

## 2. Updates and Patching
- **Windows Update Orchestrator** handles background downloads and installation based on configured settings.
- Hosts check in with Microsoft Update servers or a local **WSUS server** (preferred in enterprise — prevents individual hosts from all hitting update servers directly).
- Updates are staged in temp, manifests checked, then installed by the installer agent — **a reboot is required to finalize**.
- **Best practice:** Test updates in a dev/staging environment on a small subset of hosts before enterprise-wide rollout — avoids breaking critical apps.
- Manage via **WSUS** or **Group Policy**.

---

## 3. Configuration Management
- Use **Group Policy** (via GPMC or PowerShell) to centrally manage user/computer settings and preferences.
- Applicable in AD environments (optimal) and local computer/user settings (local group policy).
- Covers everything from browser settings and wallpapers to Windows Defender scan schedules and update behavior.
- Plan and test any new GPO creation or modification carefully — group policy changes can have broad impact.

---

## 4. User Management

- Limit the number of user and admin accounts on each system.
- Log and monitor all login attempts (valid and invalid).
- Enforce a **strong password policy** via Group Policy:
```
  Computer Configuration\Windows Settings\Security Settings\Account Policies\Password Policy
```
  Key settings: enforce password history, minimum length, complexity, maximum age, lockout thresholds.
- Enable **Two-Factor Authentication (2FA)** — requires something you *know* (password/PIN) + something you *have* (token/authenticator code). Significantly reduces account compromise risk.
- **Do not over-assign groups** — regular users should not have Domain Admin or other excessive rights unnecessary for their role.
- Enforce login restrictions on administrator accounts.
- Rotate passwords periodically and prevent reuse of old passwords.

---

## 5. Audit

- Perform **periodic security and configuration reviews** of all systems.
- Reference security baselines such as:
  - [DISA STIGs](https://public.cyber.mil/stigs/) — detailed per-OS hardening checklists
  - [Microsoft Security Compliance Toolkit](https://www.microsoft.com/en-us/download/details.aspx?id=55319)
- Compliance frameworks for organizational guidance: **ISO 27001, PCI-DSS, HIPAA**.
- Use baselines as *reference guides*, not as a complete security program — tailor controls to your organization's specific operating environment and data types.
- Audits and config reviews **supplement** but do not replace penetration tests and vulnerability scans.

---

## 6. Logging

### Sysmon (Sysinternals)
- Enhances Windows event logging — detailed process creation, network connections, file reads/writes, login events, and more.
- Persistent on host — starts logging at boot.
- Logs stored at: `Applications and Service Logs\Microsoft\Windows\Sysmon\Operational`
- Ship to a **SIEM** for correlation and analysis.
- Reference: [Sysmon documentation](https://docs.microsoft.com/en-us/sysinternals/downloads/sysmon)

### Network/Host Monitoring
- **PacketBeat**, **Security Onion** (IDS/IPS sensors), and other network monitoring tools complete the visibility picture.
- Collect and forward network traffic logs to SIEM for correlation.

---

## 7. Key Hardening Measures (Quick Reference)

- Enable **Secure Boot** and **BitLocker** disk encryption.
- Audit writable files/directories and binaries that can launch other apps.
- Scheduled tasks and scripts running with elevated privileges must use **absolute paths** for all binaries.
- Never store credentials in cleartext in world-readable files or shared drives.
- Clean up **home directories** and **PowerShell history**.
- Prevent low-privileged users from modifying custom libraries called by programs.
- Remove unnecessary packages and services (reduce attack surface).
- Enable **Device Guard** and **Credential Guard** (Windows 10 / modern Server).
- Use **Group Policy** to enforce configuration changes consistently across all systems.

---

## Key Takeaway
Proper hardening eliminates most local privilege escalation opportunities. The combination of:

1. Clean, consistent OS images
2. Regular patching (tested before rollout)
3. Centralized configuration management via Group Policy
4. Least-privilege user management + 2FA
5. Periodic audits against STIG/compliance baselines
6. Comprehensive logging (Sysmon + SIEM)

...closes the vast majority of vectors covered throughout the PrivEsc module. Hardening should be tailored to the organization — don't blindly apply enterprise-wide changes without understanding business impact. Test in staging, validate with hands-on assessments, and keep staff trained on emerging vulnerabilities.