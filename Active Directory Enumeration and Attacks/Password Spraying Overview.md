
This document outlines the principles of password spraying, real-world scenario applications, key risks, and strategic considerations for penetration testers.

### Phase 1: Core Concepts & Strategy

Password spraying is an effective technique used to gain an internal network foothold during time-boxed, non-evasive assessments. Unlike traditional brute-forcing (which tests multiple passwords against a single account and risks rapid account lockouts), password spraying tests **one common password against a large list of usernames or email addresses** with built-in delays.

#### Key Advantages & Parallel Execution

- **Efficiency:** Assessments are time-boxed; running password spraying in parallel with other TTPs (such as LLMNR/NBT-NS poisoning or hash capture) maximizes assessment output.
    
- **Low Volume per Account:** Sends fewer authentication requests per specific username, reducing the probability of triggering account lockout policies.
    

### Phase 2: Real-World Scenarios

#### Scenario 1: Standard Enumeration & List Combination

- **Context:** Standard checks (SMB NULL sessions, LDAP anonymous binds) failed to yield a valid user list.
    
- **Methodology:**
    
    1. Combined standard naming conventions (`jsmith.txt` from GitHub) with data scraped from LinkedIn.
        
    2. Used **Kerbrute** to validate active domain usernames from the combined list.
        
    3. Performed a password spray using a common default password (e.g., `Welcome1`).
        
- **Outcome:** Captured low-privileged credentials, enabling further enumeration via BloodHound and eventual domain compromise.
    

#### Scenario 2: Metadata Scraping & Custom Naming Conventions

- **Context:** Standard username lists and LinkedIn scraping yielded no valid accounts.
    
- **Methodology:**
    
    1. Searched for organization-published PDF documents via Google.
        
    2. Inspected document metadata properties and found the internal username format stored in the `Author` field as a randomized GUID pattern (`F9L8` format using capital letters and numbers).
        
    3. Generated all potential account combinations using a short Bash script:
        
        Bash
        
        ```
        #!/bin/bash
        for x in {{A..Z},{0..9}}{{A..Z},{0..9}}{{A..Z},{0..9}}{{A..Z},{0..9}}
            do echo $x;
        done
        ```
        
    4. Used **Kerbrute** with the custom-generated list to identify **100%** of active domain accounts (significantly higher than the typical 40-60% yield).
        
- **Outcome:** Successfully sprayed common passwords across all domain accounts, yielding administrative paths via Resource-Based Constrained Delegation (RBCD) and Shadow Credentials.
    

### Phase 3: Risk Management & Considerations

#### Account Lockouts & Thresholds

- **The Danger:** Careless spraying can inadvertently lock out production accounts, impacting business operations.
    
- **Policy Analysis:** Typical enterprise environments permit ~5 bad attempts before a lockout, with a 30-minute auto-unlock threshold (though some require manual admin intervention).
    
- **Best Practices:**
    
    - Enumerate the domain password policy beforehand if internal access permits.
        
    - If the policy is unknown, introduce **long delays (e.g., several hours)** between spray iterations to allow the lockout threshold to reset.
        
    - Consider a single targeted "hail mary" attempt with a weak password only if all other options have been exhausted, or coordinate directly with the client.