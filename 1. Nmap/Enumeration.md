TCP-SYN scan (`-sS`) makes it possible to scan several thousand ports per second.
```
sudo nmap -sS localhost
```
#### Scan Network Range

        shellsession
`tylapcheong@htb[/htb]$ sudo nmap 10.129.2.0/24 -sn -oA tnet | grep for | cut -d" " -f5`

| `10.129.2.0/24` | Target network range.                                            |
| --------------- | ---------------------------------------------------------------- |
| `-sn`           | Disables port scanning.                                          |
| `-oA tnet`      | Stores the results in all formats starting with the name 'tnet'. |

Scan IP List
```
sudo nmap -sn -oA tnet -iL hosts.lst | grep for | cut -d" " -f5
```

|**Scanning Options**|**Description**|
|---|---|
|`-sn`|Disables port scanning.|
|`-oA tnet`|Stores the results in all formats starting with the name 'tnet'.|
|`-iL`|Performs defined scans against targets in provided 'hosts.lst' list.|
## Scan Multiple IPs

It can also happen that we only need to scan a small part of a network. An alternative to the method we used last time is to specify multiple IP addresses.

`tylapcheong@htb[/htb]$ sudo nmap -sn -oA tnet 10.129.2.18 10.129.2.19 10.129.2.20| grep for | cut -d" " -f5  10.129.2.18 10.129.2.19 10.129.2.20`