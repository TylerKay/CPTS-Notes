## ICMP Tunneling with Ptunnel-ng

This guide covers the methodology and step-by-step process for encapsulating TCP traffic (such as SSH and dynamic SOCKS proxies) within ICMP echo request and response packets using `ptunnel-ng`.

### Methodology Overview

When traditional TCP ports are restricted by strict firewall egress or ingress filtering, but ICMP (ping) traffic is permitted, `ptunnel-ng` can be deployed to tunnel traffic. By running the server on a compromised pivot host and connecting via a local client listener on your attack host, you can wrap protocols like SSH inside ICMP payloads, effectively bypassing standard TCP blocklists.

### Step-by-Step Process

#### Step 1: Set Up and Build Ptunnel-ng on the Attack Host

1. Clone the repository and initialize the build script:
    ```bash
    git clone https://github.com/utoni/ptunnel-ng.git
    cd ptunnel-ng/
    sudo ./autogen.sh
    ```
    
    _(Alternatively, configure the build script for a static binary to avoid GLIBC version mismatches between the attack host and the target)._
    

#### Step 2: Transfer Ptunnel-ng to the Pivot Host

Copy the compiled repository directory to the compromised target host via SCP:
```bash
scp -r ptunnel-ng ubuntu@10.129.202.64:~/
```

#### Step 3: Start the Ptunnel-ng Server on the Target Host

Execute the server component on the compromised pivot host, specifying the interface IP to listen on and the destination port to forward traffic to (e.g., local SSH on port `22`):
```bash
sudo ./ptunnel-ng -r 10.129.202.64 -R 22
```

#### Step 4: Connect to the Ptunnel-ng Server from the Attack Host

On your attack host, run the client component to bind a local port (e.g., `2222`) to the ICMP tunnel routed through the pivot host:
```bash
sudo ./ptunnel-ng -p 10.129.202.64 -l 2222 -r 10.129.202.64 -R 22
```

#### Step 5: Tunnel Services and Dynamic SOCKS Proxies

1. **Establish an SSH session through the ICMP tunnel:**
    ```bash
    ssh -p 2222 -l ubuntu 127.0.0.1
    ```
    
2. **Enable Dynamic Port Forwarding for Proxychains:** Layer a dynamic SOCKS proxy on top of the tunneled SSH connection:
    ```bash
    ssh -D 9050 -p 2222 -l ubuntu 127.0.0.1
    ```
    
3. **Execute Tools via Proxychains:** Use tools like Nmap through proxychains to scan internal network assets:
    ```bash
    proxychains nmap -sV -sT 172.16.5.19 -p 3389
    ```