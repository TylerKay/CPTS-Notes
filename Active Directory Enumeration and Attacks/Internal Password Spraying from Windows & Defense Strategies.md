This section covers executing password spraying from a domain-joined Windows host, mitigating password spraying risks, detecting attacks through logging, and expanding access via external targets.
### Phase 1: Windows-Based Password Spraying
From a domain-joined Windows host, native PowerShell tools streamline the process by automatically querying Active Directory for user lists, evaluating the domain password policy, and filtering out users near the lockout threshold.

#### Using `DomainPasswordSpray.ps1`
Import the module and run the spray against the domain automatically without specifying a user list file: [DomainPasswordSpray](https://github.com/dafthack/DomainPasswordSpray)

```PowerShell
PS C:\htb> Import-Module .\DomainPasswordSpray.ps1
PS C:\htb> Invoke-DomainPasswordSpray -Password Welcome1 -OutFile spray_success -ErrorAction SilentlyContinue
```

### Phase 2: Mitigations & Defense-in-Depth
Preventing password spraying requires layered security controls across identity, network architecture, and user education:
- **Multi-Factor Authentication (MFA):** Significantly reduces the risk of password spraying by requiring secondary verification (push notifications, OTPs) for authentications, particularly across all external portals.
- **Restricting Access:** Apply the principle of least privilege. Prevent standard domain users from accessing applications, shares, or network segments unless required for their role.
- **Reducing Impact:** Enforce separate accounts for administrative activities (admin accounts vs. daily user accounts), implement application-level permissions, and utilize strong network segmentation to halt lateral movement.
- **Password Hygiene & Filters:** Educate users on using long, complex passphrases and implement custom **password filters** on Domain Controllers to block common dictionary words, seasons, and company-specific terms.

### Phase 3: Detection & Monitoring
Defenders can spot password spraying through centralized logging and SIEM correlation rules:
- **Windows Event ID 4625:** An account failed to log on. Spikes of this event over a short time window indicate SMB/standard password spraying.
- **Windows Event ID 4771:** Kerberos pre-authentication failed (useful for tracking LDAP or Kerberos-based spraying attempts; requires Kerberos logging enabled).
- **Account Lockout Storms:** Sudden spikes in account lockouts across multiple users simultaneously.
### Phase 4: External Password Spraying & Moving Deeper
Beyond internal networks, password spraying is frequently used against perimeter-facing services tied to Active Directory (such as Microsoft 365, Outlook Web Access, VPN portals, and Citrix/VDI environments).

Once initial valid credentials are established from spraying or enumeration, the next step is **credentialed enumeration** to map domain structures, locate high-value targets, and execute lateral or vertical movement toward the assessment goal.