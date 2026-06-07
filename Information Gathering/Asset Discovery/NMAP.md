# Host Discovery
#### Scan Network Range

It is always recommended to store every single scan. This can later be used for comparison, documentation, and reporting.

`tylapcheong@htb[/htb]$ sudo nmap 10.129.2.0/24 -sn -oA tnet | grep for | cut -d" " -f5`

|**Scanning Options**|**Description**|
|---|---|
|`10.129.2.0/24`|Target network range.|
|`-sn`|Disables port scanning.|
|`-oA tnet`|Stores the results in all formats starting with the name 'tnet'.|
## Scan IP List
During an internal penetration test, it is not uncommon for us to be provided with an IP list with the hosts we need to test. `Nmap` also gives us the option of working with lists and reading the hosts from this list instead of manually defining or typing them in.
cat hosts.lst 

10.129.2.4 
10.129.2.10 
10.129.2.11 
10.129.2.18 
10.129.2.19 
10.129.2.20 
10.129.2.28


tylapcheong@htb[/htb]$ sudo nmap -sn -oA tnet -iL hosts.lst | grep for | cut -d" " -f5 
10.129.2.18 
10.129.2.19 
10.129.2.20

|**Scanning Options**|**Description**|
|---|---|
|`-sn`|Disables port scanning.|
|`-oA tnet`|Stores the results in all formats starting with the name 'tnet'.|
|`-iL`|Performs defined scans against targets in provided 'hosts.lst' list.|
## Scan Multiple IPs

It can also happen that we only need to scan a small part of a network. An alternative to the method we used last time is to specify multiple IP addresses.

`tylapcheong@htb[/htb]$ sudo nmap -sn -oA tnet 10.129.2.18 10.129.2.19 10.129.2.20| grep for | cut -d" " -f5 

10.129.2.18 
10.129.2.19 
10.129.2.20`

If these IP addresses are next to each other, we can also define the range in the respective octet.
`tylapcheong@htb[/htb]$ sudo nmap -sn -oA tnet 10.129.2.18-20| grep for | cut -d" " -f5`


## Scan Single IP

Before we scan a single host for open ports and its services, we first have to determine if it is alive or not. For this, we can use the same method as before.

`tylapcheong@htb[/htb]$ sudo nmap 10.129.2.18 -sn -oA host`

| `10.129.2.18` | Performs defined scans against the target.                       |
| ------------- | ---------------------------------------------------------------- |
| `-sn`         | Disables port scanning.                                          |
| `-oA host`    | Stores the results in all formats starting with the name 'host'. |
If we disable port scan (`-sn`), Nmap automatically ping scan with `ICMP Echo Requests` (`-PE`). Once such a request is sent, we usually expect an `ICMP reply`



# Host and Port Scanning

---
There are a total of 6 different states for a scanned port we can obtain:

| **State**          | **Description**                                                                                                                                                                                         |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `open`             | This indicates that the connection to the scanned port has been established. These connections can be **TCP connections**, **UDP datagrams** as well as **SCTP associations**.                          |
| `closed`           | When the port is shown as closed, the TCP protocol indicates that the packet we received back contains an `RST` flag. This scanning method can also be used to determine if our target is alive or not. |
| `filtered`         | Nmap cannot correctly identify whether the scanned port is open or closed because either no response is returned from the target for the port or we get an error code from the target.                  |
| `unfiltered`       | This state of a port only occurs during the **TCP-ACK** scan and means that the port is accessible, but it cannot be determined whether it is open or closed.                                           |
| `open\|filtered`   | If we do not get a response for a specific port, `Nmap` will set it to that state. This indicates that a firewall or packet filter may protect the port.                                                |
| `closed\|filtered` | This state only occurs in the **IP ID idle** scans and indicates that it was impossible to determine if the scanned port is closed or filtered by a firewall.                                           |
## Discovering Open TCP Ports

By default, `Nmap` scans the top 1000 TCP ports with the SYN scan (`-sS`)
Otherwise, the TCP scan (`-sT`) is performed by default.
#### Nmap - Trace the Packets
`tylapcheong@htb[/htb]$ sudo nmap 10.129.2.28 -p 21 --packet-trace -Pn -n --disable-arp-ping`

#### Connect Scan on TCP Port 443

`tylapcheong@htb[/htb]$ sudo nmap 10.129.2.28 -p 443 --packet-trace --disable-arp-ping -Pn -n --reason -sT`

## Filtered Ports

When a port is shown as filtered, it can have several reasons. In most cases, firewalls have certain rules set to handle specific connections.
 To be able to track how our sent packets are handled, we deactivate the ICMP echo requests (`-Pn`), DNS resolution (`-n`), and ARP ping scan (`--disable-arp-ping`) again.

`tylapcheong@htb[/htb]$ sudo nmap 10.129.2.28 -p 139 --packet-trace -n --disable-arp-ping -Pn`

## Discovering Open UDP Ports

Some system administrators sometimes forget to filter the UDP ports in addition to the TCP ones. Since `UDP` is a `stateless protocol` and does not require a three-way handshake like TCP

#### UDP Port Scan
`tylapcheong@htb[/htb]$ sudo nmap 10.129.2.28 -F -sU`

|**Scanning Options**|**Description**|
|---|---|
|`10.129.2.28`|Scans the specified target.|
|`-F`|Scans top 100 ports.|
|`-sU`|Performs a UDP scan.|
Another disadvantage of this is that we often do not get a response back because `Nmap` sends empty datagrams to the scanned UDP ports, and we do not receive any response. So we cannot determine if the UDP packet has arrived at all or not. If the UDP port is `open`, we only get a response if the application is configured to do so.

sudo nmap 10.129.2.28 -sU -Pn -n --disable-arp-ping --packet-trace -p 100 --reason
#### Version Scan

`tylapcheong@htb[/htb]$ sudo nmap 10.129.2.28 -Pn -n --disable-arp-ping --packet-trace -p 445 --reason  -sV`

# Service Enumeration

---

A full port scan takes quite a long time. To view the scan status, we can press the `[Space Bar]` during the scan, which will cause `Nmap` to show us the scan status.

`tylapcheong@htb[/htb]$ sudo nmap 10.129.2.28 -p- -sV`

We can also increase the `verbosity level` (`-v` / `-vv`), which will show us the open ports directly when `Nmap` detects them.

        shellsession
`tylapcheong@htb[/htb]$ sudo nmap 10.129.2.28 -p- -sV -v`

sudo tcpdump -i eth0 host 10.10.14.2 and 10.129.2.28

# Nmap Scripting Engine

---

Nmap Scripting Engine (`NSE`) is another handy feature of `Nmap`.
There are a total of 14 categories into which these scripts can be divided:

|**Category**|**Description**|
|---|---|
|`auth`|Determination of authentication credentials.|
|`broadcast`|Scripts, which are used for host discovery by broadcasting and the discovered hosts, can be automatically added to the remaining scans.|
|`brute`|Executes scripts that try to log in to the respective service by brute-forcing with credentials.|
|`default`|Default scripts executed by using the `-sC` option.|
|`discovery`|Evaluation of accessible services.|
|`dos`|These scripts are used to check services for denial of service vulnerabilities and are used less as it harms the services.|
|`exploit`|This category of scripts tries to exploit known vulnerabilities for the scanned port.|
|`external`|Scripts that use external services for further processing.|
|`fuzzer`|This uses scripts to identify vulnerabilities and unexpected packet handling by sending different fields, which can take much time.|
|`intrusive`|Intrusive scripts that could negatively affect the target system.|
|`malware`|Checks if some malware infects the target system.|
|`safe`|Defensive scripts that do not perform intrusive and destructive access.|
|`version`|Extension for service detection.|
|`vuln`|Identification of specific vulnerabilities.|
#### Default Scripts

`tylapcheong@htb[/htb]$ sudo nmap <target> -sC`

#### Specific Scripts Category

`tylapcheong@htb[/htb]$ sudo nmap <target> --script <category>`

#### Defined Scripts

`tylapcheong@htb[/htb]$ sudo nmap <target> --script <script-name>,<script-name>,...`



This scans the target with multiple options as service detection (`-sV`), OS detection (`-O`), traceroute (`--traceroute`), and with the default NSE scripts (`-sC`).

#### Nmap - Aggressive Scan

        shellsession
`tylapcheong@htb[/htb]$ sudo nmap 10.129.2.28 -p 80 -A`

## Vulnerability Assessment

Now let us move on to HTTP port 80 and see what information and vulnerabilities we can find using the `vuln` category from `NSE`.
#### Nmap - Vuln Category

`tylapcheong@htb[/htb]$ sudo nmap 10.129.2.28 -p 80 -sV --script vuln`
```
| vulners:
|   cpe:/a:apache:http_server:2.4.29:
|       CVE-2019-0211   7.2 https://vulners.com/cve/CVE-2019-0211
|       CVE-2018-1312   6.8 https://vulners.com/cve/CVE-2018-1312
|       CVE-2017-15715  6.8 https://vulners.com/cve/CVE-2017-15715
<SNIP>
```

# Performance

---

Scanning performance plays a significant role when we need to scan an extensive network or are dealing with low network bandwidth. We can use various options to tell `Nmap` how fast (`-T <0-5>`), with which frequency (`--min-parallelism <number>`), which timeouts (`--max-rtt-timeout <time>`) the test packets should have, how many packets should be sent simultaneously (`--min-rate <number>`), and with the number of retries (`--max-retries <number>`) for the scanned ports the targets should be scanned.

#### Default Scan

`tylapcheong@htb[/htb]$ sudo nmap 10.129.2.0/24 -F <SNIP> Nmap done: 256 IP addresses (10 hosts up) scanned in 39.44 seconds`

#### Optimized RTT

`tylapcheong@htb[/htb]$ sudo nmap 10.129.2.0/24 -F --initial-rtt-timeout 50ms --max-rtt-timeout 100ms <SNIP> Nmap done: 256 IP addresses (8 hosts up) scanned in 12.29 seconds`

| **Scanning Options**         | **Description**                                       |
| ---------------------------- | ----------------------------------------------------- |
| `10.129.2.0/24`              | Scans the specified target network.                   |
| `-F`                         | Scans top 100 ports.                                  |
| `--initial-rtt-timeout 50ms` | Sets the specified time value as initial RTT timeout. |
| `--max-rtt-timeout 100ms`    | Sets the specified time value as maximum RTT timeout. |
|                              |                                                       |
## Max Retries

Another way to increase scan speed is by specifying the retry rate of sent packets (`--max-retries`). The default value is `10`, but we can reduce it to `0`. This means if Nmap does not receive a response for a port, it won't send any more packets to that port and will skip it.

#### Default Scan

`tylapcheong@htb[/htb]$ sudo nmap 10.129.2.0/24 -F | grep "/tcp" | wc -l 23`

#### Reduced Retries

`tylapcheong@htb[/htb]$ sudo nmap 10.129.2.0/24 -F --max-retries 0 | grep "/tcp" | wc -l 21`

Again, we recognize that accelerating can also have a negative effect on our results, which means we can overlook important information.

## Rates

During a white-box penetration test, we may get whitelisted for the security systems to check the systems in the network for vulnerabilities and not only test the protection measures
#### Default Scan

`tylapcheong@htb[/htb]$ sudo nmap 10.129.2.0/24 -F -oN tnet.default`

#### Optimized Scan

`tylapcheong@htb[/htb]$ sudo nmap 10.129.2.0/24 -F -oN tnet.minrate300 --min-rate 300`


## Timing

Because such settings cannot always be optimized manually, as in a black-box penetration test, `Nmap` offers six different timing templates (`-T <0-5>`) for us to use. These values (`0-5`) determine the aggressiveness of our scans. This can also have negative effects if the scan is too aggressive, and security systems may block us due to the produced network traffic. The default timing template used when we have defined nothing else is the normal (`-T 3`).
https://nmap.org/book/performance-timing-templates.html

- `-T 0` / `-T paranoid`
- `-T 1` / `-T sneaky`
- `-T 2` / `-T polite`
- `-T 3` / `-T normal`
- `-T 4` / `-T aggressive`
- `-T 5` / `-T insane`
#### Insane Scan
##### Insane Scan

`tylapcheong@htb[/htb]$ sudo nmap 10.129.2.0/24 -F -oN tnet.T5 -T 5 <SNIP> Nmap done: 256 IP addresses (10 hosts up) scanned in 18.07 seconds`

##### Default Scan (Regular...slower)

`tylapcheong@htb[/htb]$ sudo nmap 10.129.2.0/24 -F -oN tnet.default  <SNIP> Nmap done: 256 IP addresses (10 hosts up) scanned in 32.44 seconds`

