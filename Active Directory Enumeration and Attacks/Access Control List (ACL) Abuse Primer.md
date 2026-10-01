## 1. Executive Summary

Access Control Lists (ACLs) define resource permissions in Active Directory (AD). Misconfigured ACLs—specifically Access Control Entries (ACEs)—can leak permissions to unintended users, creating severe security risks. Attackers and penetration testers leverage these misconfigurations for lateral movement, privilege escalation, and persistence when "low-hanging fruit" AD flaws are absent.
## 2. Core Concepts
- **ACLs & ACEs:** Every AD object has an ACL composed of Access Control Entries (ACEs). Each ACE maps a security principal (user/group) to specific permissions.
- **Types of ACLs:**
    - **DACL (Discretionary Access Control List):** Determines which security principals are explicitly granted or denied access.
    - **SACL (System Access Control List):** Used by administrators to log access attempts (auditing).
- **ACE Components:** Security Identifier (SID), ACE type (Allow/Deny/Audit), Inheritance flags, and an Access Mask (32-bit rights value). _Note: ACLs are processed from top to bottom until an explicit "deny" is met.

## 3. High-Value ACEs & Attack Vectors
Organizations often leave specific ACEs unchecked for years. Key targets include:
- **ForceChangePassword:** Reset a user's password without knowing the current one (e.g., via `Set-DomainUserPassword`).
- **GenericWrite:** Write to non-protected attributes. Can lead to Kerberoasting (by assigning an SPN to a weak-password user) or unauthorized group additions.
- **AddSelf:** Allows a user to add themselves to specific security groups.
- **GenericAll:** Full control over a target object (allows password resets, group modifications, or LAPS password retrieval for local admin access).

## 4. Methodology and Step-by-Step Process for ACL Assessments
### Phase 1: Enumeration & Visualization
- **Step 1:** Import AD environment data into analysis tools.
- **Step 2:** Use visualization and querying tools (such as **BloodHound** or **PowerView**) to map out object permissions, find non-standard ACE edges, and identify overly permissive ACL settings across users, groups, and computers.
    
### Phase 2: Analysis & Attack Selection
- **Step 3:** Review discovered ACEs to determine the appropriate attack path (e.g., identifying `ForceChangePassword` on a high-privilege account or `GenericWrite` for targeted Kerberoasting).
- **Step 4:** Consult with the client to secure written approval if the intended action is potentially "destructive" (such as modifying passwords or altering group memberships).
    
### Phase 3: Exploitation
- **Step 5:** Execute the chosen technique using appropriate tooling from a Windows or Linux attack host (e.g., PowerView commands like `Set-DomainUserPassword`, `Add-DomainGroupMember`, or utilizing BloodHound paths).
- **Step 6:** Validate the success of the exploitation (e.g., achieving lateral movement, vertical privilege escalation, or persistence).

### Phase 4: Cleanup & Reporting
- **Step 7:** Carefully revert all changes made during the assessment (e.g., resetting passwords back or removing added group members).
- **Step 8:** Document all actions taken from start to finish, highlighting modified objects so the client can verify that changes were successfully cleaned up.