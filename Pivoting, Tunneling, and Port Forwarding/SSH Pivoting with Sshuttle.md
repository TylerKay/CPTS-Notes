
---

[Sshuttle](https://github.com/sshuttle/sshuttle) is another tool written in Python which removes the need to configure proxychains. However, this tool only works for pivoting over SSH and does not provide other options for pivoting over TOR or HTTPS proxy servers. `Sshuttle` can be extremely useful for automating the execution of iptables and adding pivot rules for the remote host. We can configure the Ubuntu server as a pivot point and route all of Nmap's network traffic with sshuttle using the example later in this section.

One interesting usage of sshuttle is that we don't need to use proxychains to connect to the remote hosts. Let's install sshuttle via our Ubuntu pivot host and configure it to connect to the Windows host via RDP.

#### Installing sshuttle
```
tylapcheong@htb[/htb]$ sudo apt-get install sshuttle
```

To use sshuttle, we specify the option `-r` to connect to the remote machine with a username and password. Then we need to include the network or IP we want to route through the pivot host, in our case, is the network 172.16.5.0/23.

#### Running sshuttle

```
tylapcheong@htb[/htb]$ sudo sshuttle -r ubuntu@10.129.202.64 172.16.5.0/23 -v 
```

With this command, sshuttle creates an entry in our `iptables` to redirect all traffic to the 172.16.5.0/23 network through the pivot host.

#### Traffic Routing through iptables Routes
```
tylapcheong@htb[/htb]$ sudo nmap -v -A -sT -p3389 172.16.5.19 -Pn
```
We can now use any tool directly without using proxychains.

---

Note: When spawning your target, we ask you to wait for 3 - 5 minutes until the whole lab with all the configurations is set up so that the connection to your target works flawlessly. SSH to the target with user "`ubuntu`" and password "`HTB_@cademy_stdnt!`"