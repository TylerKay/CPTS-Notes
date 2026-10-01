## Overview & Terminology

- **Pivoting:** Utilizing a compromised host (also known as a **Pivot Host**, **Proxy**, **Foothold**, **Beach Head system**, or **Jump Host**) to cross network boundaries and access previously unreachable network segments or isolated environments.
    
- **Tunneling:** Encapsulating network traffic inside another protocol (e.g., HTTPS, SSH) to route it securely or stealthily through a network, often used for obfuscation, data exfiltration, or Command & Control (C2) communications.
    
- **Lateral Movement:** Spreading wide across a network environment to access additional hosts, applications, and services, often aiding in privilege escalation and locating domain resources.
    

## Core Concepts Compared

| **Concept**          | **Primary Focus / Objective**                                                                                                           | **Practical Scenario**                                                                                                                          |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| **Lateral Movement** | Expanding access horizontally or vertically across hosts and systems within an accessible network segment.                              | Reusing local administrator credentials found on an initial workstation to compromise other Windows machines sharing the same account.          |
| **Pivoting**         | Bypassing physical or logical network segmentation to reach deeper, isolated internal networks via dual-homed or multi-interface hosts. | Using an engineering workstation connected to both an enterprise network and an isolated operational technology (OT) network to bridge the gap. |
| **Tunneling**        | Obfuscating network traffic by wrapping it within trusted or encrypted protocols to evade detection or filtering.                       | Masking C2 instructions inside standard HTTP/HTTPS GET and POST web requests to blend in with normal web traffic.                               |
