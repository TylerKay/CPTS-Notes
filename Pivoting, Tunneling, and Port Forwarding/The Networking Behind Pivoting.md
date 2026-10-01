- **IP Addresses & Network Interfaces (NICs):** Multi-homed systems equipped with multiple NICs or virtual adapters are primary candidates for pivoting. Identifying whether an IP address is publicly routable (found on DMZ or edge devices) or private helps map accessible internal segments. Commands like `ifconfig` (Linux/macOS) and `ipconfig` (Windows) are essential for discovering these interfaces and active VPN tunnels (`tun0`).
    
- **Subnets & Default Gateways:** The subnet mask establishes the boundaries of a local network. When traffic is destined for an IP address outside that local segment, the system forwards it to the **default gateway** (typically a router or routing appliance) to be directed across networks.
    
- **Routing Tables:** Operating systems (Linux, Windows, and Pwnbox) maintain routing tables (`netstat -r` or `ip route`) that dictate how packets are forwarded based on destination IPs. Analyzing routing tables helps identify reachable networks or determine what custom routes must be added during a pivot.
```
tylapcheong@htb[/htb]$ netstat -r

Kernel IP routing table
Destination     Gateway         Genmask         Flags   MSS Window  irtt Iface
default         178.62.64.1     0.0.0.0         UG        0 0          0 eth0
10.10.10.0      10.10.14.1      255.255.254.0   UG        0 0          0 tun0
10.10.14.0      0.0.0.0         255.255.254.0   U         0 0          0 tun0
10.106.0.0      0.0.0.0         255.255.240.0   U         0 0          0 eth1
10.129.0.0      10.10.14.1      255.255.0.0     UG        0 0          0 tun0
178.62.64.0     0.0.0.0         255.255.192.0   U         0 0          0 eth0
```

    
- **Protocols, Services, and Ports:** Logical ports tie services to applications. Legitimate inbound ports (such as HTTP on port 80) are frequently allowed through perimeter firewalls, making them valuable vectors for initial footholds, tunneling, and maintaining command-and-control communications.