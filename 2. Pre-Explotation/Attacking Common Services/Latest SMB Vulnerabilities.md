# Latest SMB Vulnerabilities (SMBGhost)

## Overview: CVE-2020-0796
- **Target Protocol:** SMB v3.1.1 compression mechanism.
- **Affected Systems:** Windows 10 versions 1903 and 1909.
- **Impact:** Unauthenticated remote code execution (RCE) and full system access.

## Attack Concept & Mechanism
### 1. Root Cause
- **Integer Overflow:** Caused by a lack of bounds checks on data size during SMB session negotiation.
- **Mechanism:** When the CPU attempts to generate a number exceeding the allocated memory space limit (or handles negative numbers returned as positive integers), an arithmetic error occurs.
- **Execution Flow:** Malformed compressed packets sent post-Negotiate Protocol overflow the buffer, overwriting subsequent CPU instructions with attacker-supplied payloads, forcing the system to execute arbitrary instructions.
    
### 2. Attack Lifecycle Steps

1. **Source:** Client sends a manipulated request to the SMB server.
2. **Process:** Compressed packets are processed according to negotiated protocol responses.
3. **Privileges:** Executed with system privileges (or administrator equivalent).
4. **Destination:** Local process processes the compressed packets.
5. **Secondary Cycle (RCE):** The overwritten buffer forces the CPU to execute malicious instructions, granting remote attacker access to the target system.