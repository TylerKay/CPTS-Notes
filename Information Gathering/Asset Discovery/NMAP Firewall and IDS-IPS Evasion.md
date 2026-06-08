`Nmap` gives us many different ways to bypass firewalls rules and IDS/IPS. These methods include the fragmentation of packets, the use of decoys, and others that we will discuss in this section.

When a port is closed or open, the host must respond with an `RST` flag. Unlike outgoing connections, all connection attempts (with the `SYN` flag) from external networks are usually blocked by firewalls. However, the packets with the `ACK` flag are often passed by the firewall because the firewall cannot determine whether the connection was first established from the external network or the internal network.

Nmap's TCP ACK scan (`-sA`) method is much harder to filter for firewalls and IDS/IPS systems than regular SYN (`-sS`) or Connect scans (`sT`) because they only send a TCP packet with only the `ACK` flag. When a port is closed or open, the host must respond with an `RST` flag. Unlike outgoing connections, all connection attempts (with the `SYN` flag) from external networks are usually blocked by firewalls. However, the packets with the `ACK` flag are often passed by the firewall because the firewall cannot determine whether the connection was first established from the external network or the internal network.


### Important

Use a **TCP SYN scan** if your goal is to discover **open ports** and map the attack surface. Use a **TCP ACK scan** strictly to map **firewall rule sets** and determine if ports are filtered

#### SYN-Scan

`tylapcheong@htb[/htb]$ sudo nmap 10.129.2.28 -p 21,22,25 -sS -Pn -n --disable-arp-ping --packet-trace`


#### ACK-Scan

`tylapcheong@htb[/htb]$ sudo nmap 10.129.2.28 -p 21,22,25 -sA -Pn -n --disable-arp-ping --packet-trace`


#### Scan by Using Decoys
There are cases in which administrators block specific subnets from different regions in principle. This prevents any access to the target network. Another example is when IPS should block us. For this reason, the Decoy scanning method (`-D`) is the right choice.

`tylapcheong@htb[/htb]$ sudo nmap 10.129.2.28 -p 80 -sS -Pn -n --disable-arp-ping --packet-trace -D RND:5`

#### Testing Firewall Rule

`tylapcheong@htb[/htb]$ sudo nmap 10.129.2.28 -n -Pn -p445 -O`

#### Scan by Using Different Source IP

`tylapcheong@htb[/htb]$ sudo nmap 10.129.2.28 -n -Pn -p 445 -O -S 10.129.2.200 -e tun0`

|   |   |
|---|---|
|`-e tun0`|Sends all requests through the specified interface.|
## DNS Proxying

By default, `Nmap` performs a reverse DNS resolution unless otherwise specified to find more important information about our target

However, `Nmap` still gives us a way to specify DNS servers ourselves (`--dns-server <ns>,<ns>`). This method could be fundamental to us if we are in a demilitarized zone (`DMZ`). The company's DNS servers are usually more trusted than those from the Internet.

#### SYN-Scan of a Filtered Port

`tylapcheong@htb[/htb]$ sudo nmap 10.129.2.28 -p50000 -sS -Pn -n --disable-arp-ping --packet-trace`

#### SYN-Scan From DNS Port

`tylapcheong@htb[/htb]$ sudo nmap 10.129.2.28 -p50000 -sS -Pn -n --disable-arp-ping --packet-trace --source-port 53`

|**Scanning Options**|**Description**|
|---|---|
|`10.129.2.28`|Scans the specified target.|
|`-p 50000`|Scans only the specified ports.|
|`-sS`|Performs SYN scan on specified ports.|
|`-Pn`|Disables ICMP Echo requests.|
|`-n`|Disables DNS resolution.|
|`--disable-arp-ping`|Disables ARP ping.|
|`--packet-trace`|Shows all packets sent and received.|
|`--source-port 53`|Performs the scans from specified source port.


#### Connect To The Filtered Port

`tylapcheong@htb[/htb]$ ncat -nv --source-port 53 10.129.2.28 50000`



--
sudo nc -nv -s 10.10.15.197 -p53 10.129.2.47 50000

This command uses Netcat (`nc`) to establish a direct, raw network connection to a target server while **spoofing your network settings** to bypass firewall rules. 10.10.15.197 is current machine, listen on port 53. Target machine is 10.129.2.47 on port 50000.