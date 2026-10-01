## Overview

Occur when administrators, tech support, or developers incorrectly configure a security framework (application, website, desktop, server), creating open pathways for unauthorized users.

## Common Service Misconfigurations

### 1. Authentication

- **Default Credentials:** Historically common and still found in older applications. Many administrators fail to change factory defaults.
    
- **Weak/No Passwords:** Temporary weak credentials set during setup are often forgotten or left active.
    
- **Common Weak Combinations to Test:**
    Plaintext
    ```
    admin:admin
    admin:password
    admin:<blank>
    root:12345678
    administrator:Password
    ```
- **Mitigation:** Enforce strict password complexity policies, require credential setup during installation, and test for default/weak combinations after grabbing service banners.
### 2. Anonymous Authentication
- Services configured to allow unauthenticated access, letting anyone with network connectivity bypass login prompts entirely.
- **Example Check (FTP):**
    Bash
    ```
    ftp <target_ip>
    # Username: anonymous
    # Password: (any email or blank)
    ```
### 3. Misconfigured Access Rights

- **Over-permissioning:** User accounts are granted incorrect permissions (e.g., standard users having read access to sensitive FTP directories containing PII, plaintext credentials, or other service configs).
- **Mitigation:** Implement structured access control strategies like Role-Based Access Control (RBAC) or Access Control Lists (ACL).
### 4. Unnecessary Defaults
- Initial settings, features, files, and credentials prioritized for _usability_ over security.
- **OWASP Top 10 Indicators:**
    - Unnecessary features/ports/services/accounts enabled.
    - Default accounts/passwords active.
    - Verbose error handling (revealing stack traces).
    - Security features disabled post-upgrade.
## Prevention & Hardening Strategies

- **Lock Down Infrastructure:** Disable all communication, admin interfaces, and debugging not strictly required by the application.
- **Repeatable Hardening:** Automate a fast, identical deployment process across Development, QA, and Production environments (using distinct credentials per environment).
- **Minimal Platform:** Strip out unused features, components, documentation, samples, and frameworks to reduce the attack surface.
- **Patch Management:** Regularly review/update configurations against security notes, patches, and cloud storage permissions (e.g., AWS S3 bucket permissions).
- **Architecture & Directives:** Use segmented application architecture (containers, cloud security groups, ACLs) and send security headers to clients.
- **Auditing:** Run regular scans and automated checks to verify configuration effectiveness across all environments.
- **Example Automated Scan (Nmap Vulnerability Check):**
    Bash
    ```
    nmap --script vuln <target_ip>
    ```