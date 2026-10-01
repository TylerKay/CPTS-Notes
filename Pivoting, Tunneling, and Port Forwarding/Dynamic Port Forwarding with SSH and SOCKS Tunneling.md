### Methodology Overview

When an attack host lacks direct routing to an internal subnet (e.g., `172.16.5.0/23`), but has access to a dual-homed compromised host (pivot host), dynamic port forwarding (SOCKS proxy) allows all TCP traffic from local tools to be encapsulated over an SSH connection. Tools like `proxychains` are then leveraged to route scanner and client traffic through the local SOCKS listener to discover and interact with internal assets.

### Step-by-Step Process

#### Step 1: Identify Pivot Opportunities via Network Interfaces

Examine the network interfaces on the compromised host to discover internal subnets attached to secondary NICs.
```Bash
ifconfig
```

_Look for secondary interfaces (e.g., `ens224`) showing private IP addresses belonging to unreached internal networks._

#### Step 2: Establish Dynamic Port Forwarding with SSH

From the attack host, execute the SSH client with the `-D` flag to open a local SOCKS listener (typically on port `9050`) routed through the compromised pivot host.
```bash
ssh -D 9050 ubuntu@10.129.202.64
```
- **`-D 9050`**: Instructs SSH to set up a dynamic application-layer port forwarding proxy on local port `9050`.
    

#### Step 3: Configure Proxychains

Update the proxychains configuration file to point to the local SOCKS listener so non-proxy-aware tools can route through the tunnel.
1. Open `/etc/proxychains.conf`.
2. Ensure the following line is present at the end of the file:
    ```Plaintext
    socks4 127.0.0.1 9050
    ```

#### Step 4: Enumerate Internal Targets via Proxychains

Because proxychains operates on full TCP connections, use a full connect scan (`-sT`) along with host discovery disabled (`-Pn`) when scanning internal Windows hosts where ICMP is blocked.
```bash
proxychains nmap -v -Pn -sT 172.16.5.19
```

#### Step 5: Interact with Internal Services

Route exploit frameworks, scanners, or client applications through proxychains to target discovered internal ports (such as RDP on port `3389`).
- **Using Metasploit:**
    ```bash
    proxychains msfconsole
    ```
    _(Example: Configure and run `auxiliary/scanner/rdp/rdp_scanner` against the internal target)_
    
- **Using `xfreerdp` for Remote Access:**
    ```bash
    proxychains xfreerdp /v:172.16.5.19 /u:victor /p:pass@123
    ```