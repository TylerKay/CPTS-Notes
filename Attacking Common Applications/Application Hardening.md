
> 💡 This is defensive/blue-team-facing content — useful both for writing remediation sections in pentest reports and for understanding what a well-hardened target looks like during an assessment.

---

## 1. Foundation — Application Inventory

- **First step for any org:** build a detailed, accurate inventory of **all** internal and external-facing applications.
- Can't protect what you don't know exists.
- Budget-friendly tools: **Nmap** + **EyeWitness** (also useful from the offensive side — same tools attackers use to map the estate).
- Benefits of a good inventory:
    - Surfaces **shadow IT** (unauthorized/unknown installs)
    - Identifies **deprecated apps** no longer needed
    - Catches subtle issues — e.g., a Splunk trial silently reverting to a free tier that **no longer requires authentication**

---

## 2. General Hardening Measures

|Measure|Details|
|---|---|
|**Secure authentication**|Enforce strong passwords; change/disable default admin accounts (create custom ones instead); mandate 2FA for admins where supported|
|**Access controls**|Restrict login pages from external access unless justified; lock down file/folder permissions to block unauthorized uploads/deployments|
|**Disable unsafe features**|E.g., disable PHP code editing in WordPress to prevent RCE if compromised|
|**Regular updates**|Apply vendor patches promptly|
|**Backups**|Configure regular website + DB backups for fast recovery|
|**Security monitoring**|Use monitoring tools/plugins; consider a **WAF** as an added layer (not a silver bullet — only effective on top of the other measures)|
|**LDAP/AD integration (SSO)**|Centralizes auth, improves auditing (esp. with Azure sync), reduces password sprawl, enables fine-grained password policy control|

### Universal Checklist (Applies to Every App)

- MFA for admins and users wherever possible
- Rename/change default admin account names
- Limit number of admin accounts
- Restrict admin access paths (not reachable from the open internet)
- Enforce **principle of least privilege** throughout
- Regular updates/patching
- Regular backups to a **secondary location**
- Security monitoring for brute-force and other malicious activity
- **Minimize internet exposure** — ask: does this GitLab repo need to be public? Does the ticketing system need to be internet-facing?

### Ongoing Process

- Periodically **re-audit the application inventory** — catch apps no longer needed or with severe unpatched flaws.
- Run **regular security assessments** for vulnerabilities, misconfigurations, and sensitive data exposure.
- Actually **follow through** on pentest remediation recommendations, and re-check for recurrence.
- Some fixes are **process/mindset shifts**, not just technical patches — building a security-conscious culture matters.

---

## 3. Application-Specific Hardening Tips

|Application|Category|Recommendation|
|---|---|---|
|**WordPress**|Security monitoring|Use a plugin like **WordFence** — monitoring, suspicious activity blocking, country blocking, 2FA|
|**Joomla**|Access controls|Use **AdminExile** to require a secret key to reach `/administrator` (e.g., `?thisismysecretkey`)|
|**Drupal**|Access controls|Disable, hide, or relocate the admin login page|
|**Tomcat**|Access controls|Restrict Manager/Host-Manager to **localhost**; if external access is required, enforce IP whitelisting + strong non-standard username/password|
|**Jenkins**|Access controls|Use the **Matrix Authorization Strategy** plugin for granular permissions|
|**Splunk**|Regular updates|Change default password; ensure proper licensing so authentication stays enforced|
|**PRTG Network Monitor**|Secure authentication|Keep up to date; change the default PRTG password|
|**osTicket**|Access controls|Limit internet-facing access where possible|
|**GitLab**|Secure authentication|Enforce sign-up restrictions (admin approval for new accounts, allowed/denied email domains)|

---

## Summary

|Category|Core Idea|
|---|---|
|Inventory|Know what exists before trying to protect it|
|Authentication|Strong passwords, no default creds, MFA for admins|
|Access control|Minimize internet exposure, restrict admin paths|
|Maintenance|Patch promptly, back up regularly, re-audit inventory|
|Monitoring|Detect brute-force/malicious activity; WAF as a supplement, not a replacement|
|Integration|LDAP/AD SSO for centralized, auditable credential management|

## Key Takeaways

- Most real-world compromises in this module's applications trace back to **weak/default credentials** and **overexposed admin interfaces** — not necessarily exotic 0-days.
- A WAF is only meaningful **after** the fundamentals (patching, auth, access control) are already in place — it's a supplement, not a fix for weak hardening.
- The application inventory is the single most foundational control — everything else depends on actually knowing what's running.
- From an offensive perspective: assume any org skipping these basics (default creds, exposed admin panels, unpatched known CVEs) is exactly where a real assessment will find its foothold — this list doubles as a checklist of what to test for.

## Module Conclusion

- Web applications represent a **huge attack surface**, often the majority of targets in an external pentest.
- Core skills: **discover** applications, **organize** scan data efficiently, **footprint** versions, find **known vulnerabilities**, and **abuse built-in functionality**.
- Orgs often patch well but overlook simpler issues — weak Tomcat Manager creds, default printer web-admin credentials leaking LDAP creds, etc.
- These fundamentals generalize far beyond the specific applications covered in this module.