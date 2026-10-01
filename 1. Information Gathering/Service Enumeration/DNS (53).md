`Domain Name System` (`DNS`) is an integral part of the Internet. DNS is a system for resolving computer names into IP addresses, and it does not have a central database. Simplified, we can imagine it like a library with many different phone books.

|**Server Type**|**Description**|
|---|---|
|`DNS Root Server`|The root servers of the DNS are responsible for the top-level domains (`TLD`). As the last instance, they are only requested if the name server does not respond. Thus, a root server is a central interface between users and content on the Internet, as it links domain and IP address. The [Internet Corporation for Assigned Names and Numbers](https://www.icann.org/) (`ICANN`) coordinates the work of the root name servers. There are `13` such root servers around the globe.|
|`Authoritative Nameserver`|Authoritative name servers hold authority for a particular zone. They only answer queries from their area of responsibility, and their information is binding. If an authoritative name server cannot answer a client's query, the root name server takes over at that point. Based on the country, company, etc., authoritative nameservers provide answers to recursive DNS nameservers, assisting in finding the specific web server(s).|
|`Non-authoritative Nameserver`|Non-authoritative name servers are not responsible for a particular DNS zone. Instead, they collect information on specific DNS zones themselves, which is done using recursive or iterative DNS querying.|
|`Caching DNS Server`|Caching DNS servers cache information from other name servers for a specified period. The authoritative name server determines the duration of this storage.|
|`Forwarding Server`|Forwarding servers perform only one function: they forward DNS queries to another DNS server.|
|`Resolver`|Resolvers are not authoritative DNS servers but perform name resolution locally in the computer or router.|
DNS is mainly unencrypted. Devices on the local WLAN and Internet providers can therefore hack in and spy on DNS queries. By default, IT security professionals apply `DNS over TLS` (`DoT`) or `DNS over HTTPS` (`DoH`) here. In addition, the network protocol `DNSCrypt` also encrypts the traffic between the computer and the name server.

![[Pasted image 20260607000623.png]]

Different `DNS records` are used for the DNS queries, which all have various tasks. Moreover, separate entries exist for different functions since we can set up mail servers and other servers for a domain.

|**DNS Record**|**Description**|
|---|---|
|`A`|Returns an IPv4 address of the requested domain as a result.|
|`AAAA`|Returns an IPv6 address of the requested domain.|
|`MX`|Returns the responsible mail servers as a result.|
|`NS`|Returns the DNS servers (nameservers) of the domain.|
|`TXT`|This record can contain various information. The all-rounder can be used, e.g., to validate the Google Search Console or validate SSL certificates. In addition, SPF and DMARC entries are set to validate mail traffic and protect it from spam.|
|`CNAME`|This record serves as an alias for another domain name. If you want the domain [www.hackthebox.eu](http://www.hackthebox.eu/) to point to the same IP as hackthebox.eu, you would create an A record for hackthebox.eu and a CNAME record for [www.hackthebox.eu](http://www.hackthebox.eu/).|
|`PTR`|The PTR record works the other way around (reverse lookup). It converts IP addresses into valid domain names.|
|`SOA`|Provides information about the corresponding DNS zone and email address of the administrative contact.|

The `SOA` record is located in a domain's zone file and specifies who is responsible for the operation of the domain and how DNS information for the domain is managed.

`tylapcheong@htb[/htb]$ dig soa www.inlanefreight.com`
;; AUTHORITY SECTION: inlanefreight.com. 900 IN SOA ns-161.awsdns-20.com. awsdns-hostmaster.amazon.com. 1 7200 900 1209600 86400

The dot (.) is replaced by an at sign (@) in the email address. In this example, the email address of the administrator is `awsdns-hostmaster@amazon.com`.

 All DNS servers work with three different types of configuration files:

1. local DNS configuration files
2. zone files
3. reverse name resolution files
4. 
The DNS server [Bind9](https://www.isc.org/bind/) is very often used on Linux-based distributions. Its local configuration file (`named.conf`) is roughly divided into two sections, firstly the options section for general settings and secondly the zone entries for the individual domains. The local configuration files are usually:

- `named.conf.local`
- `named.conf.options`
- `named.conf.log`
- 
A `zone file` is a text file that describes a DNS zone with the BIND file format. In other words it is a point of delegation in the DNS tree.  There must be precisely one `SOA` record and at least one `NS` record. The SOA resource record is usually located at the beginning of a zone file.

In short, here, all `forward records` are entered according to the BIND format

#### Zone Files

`root@bind9:~# cat /etc/bind/db.domain.com`

For the `Fully Qualified Domain Name` (`FQDN`) to be resolved from the IP address, the DNS server must have a reverse lookup file. In this file, the computer name (`FQDN`) is assigned to the last octet of an IP address, which corresponds to the respective host, using a PTR record. The PTR records are responsible for the reverse translation of IP addresses into names, as we have already seen in the above table.

#### Reverse Name Resolution Zone Files
`root@bind9:~# cat /etc/bind/db.10.129.14`


## Dangerous Settings

There are many ways in which a DNS server can be attacked. For example, a list of vulnerabilities targeting the BIND9 server can be found at [CVEdetails](https://www.cvedetails.com/product/144/ISC-Bind.html?vendor_id=64). In addition, SecurityTrails provides a short [list](https://web.archive.org/web/20250329174745/https://securitytrails.com/blog/most-popular-types-dns-attacks) of the most popular attacks on DNS servers.

|**Option**|**Description**|
|---|---|
|`allow-query`|Defines which hosts are allowed to send requests to the DNS server.|
|`allow-recursion`|Defines which hosts are allowed to send recursive requests to the DNS server.|
|`allow-transfer`|Defines which hosts are allowed to receive zone transfers from the DNS server.|
|`zone-statistics`|Collects statistical data of zones.|
## Footprinting the Service

The footprinting at DNS servers is done as a result of the requests we send. So, first of all, the DNS server can be queried as to which other name servers are known.

#### DIG - NS Query
`tylapcheong@htb[/htb]$ dig ns inlanefreight.htb @10.129.14.128`

Sometimes it is also possible to query a DNS server's version using a class CHAOS query and type TXT. However, this entry must exist on the DNS server. For this, we could use the following command:
#### DIG - Version Query
`tylapcheong@htb[/htb]$ dig CH TXT version.bind 10.129.120.85`

We can use the option `ANY` to view all available records. This will cause the server to show us all available entries that it is willing to disclose. It is important to note that not all entries from the zones will be shown.
#### DIG - ANY Query

`tylapcheong@htb[/htb]$ dig any inlanefreight.htb @10.129.14.128`

`Zone transfer` refers to the transfer of zones to another server in DNS, which generally happens over TCP port 53. This procedure is abbreviated `Asynchronous Full Transfer Zone` (`AXFR`). Since a DNS failure usually has severe consequences for a company, the zone file is almost invariably kept identical on several name servers.

For some `Top-Level Domains` (`TLDs`), making zone files for the `Second Level Domains` accessible on at least two servers is mandatory.

DNS entries are generally only created, modified, or deleted on the primary. This can be done by manually editing the relevant zone file or automatically by a dynamic update from a database

The slave fetches the `SOA` record of the relevant zone from the master at certain intervals, the so-called refresh time, usually one hour, and compares the serial numbers.

#### DIG - AXFR Zone Transfer
`tylapcheong@htb[/htb]$ dig axfr inlanefreight.htb @10.129.14.128`

If the administrator used a subnet for the `allow-transfer` option for testing purposes or as a workaround solution or set it to `any`, everyone would query the entire zone file at the DNS server. In addition, other zones can be queried, which may even show internal IP addresses and hostnames.

#### DIG - AXFR Zone Transfer - Internal
`tylapcheong@htb[/htb]$ dig axfr internal.inlanefreight.htb @10.129.14.128`

The individual `A` records with the hostnames can also be found out with the help of a brute-force attack. To do this, we need a list of possible hostnames, which we use to send the requests in order. Such lists are provided, for example, by [SecLists](https://github.com/danielmiessler/SecLists/blob/master/Discovery/DNS/subdomains-top1million-5000.txt).

#### Subdomain Brute Forcing
`tylapcheong@htb[/htb]$ for sub in $(cat /opt/useful/seclists/Discovery/DNS/subdomains-top1million-110000.txt);do dig $sub.inlanefreight.htb @10.129.14.128 | grep -v ';\|SOA' | sed -r '/^\s*$/d' | grep $sub | tee -a subdomains.txt;done`


Many different tools can be used for this, and most of them work in the same way. One of these tools is, for example [DNSenum](https://github.com/fwaeytens/dnsenum).

`tylapcheong@htb[/htb]$ dnsenum --dnsserver 10.129.14.128 --enum -p 0 -s 0 -o subdomains.txt -f /opt/useful/seclists/Discovery/DNS/subdomains-top1million-110000.txt inlanefreight.htb`