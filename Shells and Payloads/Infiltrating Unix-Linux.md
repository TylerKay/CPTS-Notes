 When considering how we will establish a shell session on a Unix/Linux system, we will benefit from considering the following:

- What distribution of Linux is the system running?
- What shell & programming languages exist on the system?
- What function is the system serving for the network environment it is on?
- What application is the system hosting?
- Are there any known vulnerabilities?


## Gaining a Shell Through Attacking a Vulnerable Application

As in most engagements, we will start with an initial enumeration of the system using `Nmap`.
#### Enumerate the Host
`tylapcheong@htb[/htb]$ nmap -sC -sV 10.129.201.101`

Keeping our goal of `gaining a shell session` in mind, we must establish some next steps after examining our scan output.

Considering we can see the system is listening on ports 80 (`HTTP`), 443 (`HTTPS`), 3306 (`MySQL`), and 21 (`FTP`), it may be safe to assume that this is a web server hosting a web application.

We can also see some version numbers revealed associated with the web stack (`Apache 2.4.6` and `PHP 7.2.34` ) and the distribution of Linux running on the system (`CentOS`). we should also try navigating to the IP address through a web browser to discover the hosted application if possible. Here we discover a network configuration management tool called [rConfig](https://www.rconfig.com/). This application is used by network & system administrators to automate the process of configuring network appliances. One practical use case would be to use rConfig to remotely configure network interfaces with IP addressing information on multiple routers simultaneously.

## Discovering a Vulnerability in rConfig

Take a close look at the bottom of the web login page, and we can see the rConfig version number (`3.9.6`). We should use this information to start looking for any `CVEs`, `publicly available exploits`, and `proof of concepts` (`PoCs`).

Using your search engine of choice will turn up some promising results. We can use the keywords: `rConfig 3.9.6 vulnerability.`


We can also use Metasploit's search functionality to see if any exploit modules can get us a shell session on the target.
#### Search For an Exploit Module
`msf6 > search rconfig`

We could do an even more specific search using a search engine: `rConfig 3.9.6 exploit metasploit github`

This search can point us to the source code for an exploit module called `rconfig_vendors_auth_file_upload_rce.rb`

This exploit can get us a shell session on a target Linux box running rConfig 3.9.6. If this exploit did not show up in the MSF search, we can copy the code from this repo onto our local attack box and save it in the directory that our local install of MSF is referencing. To do this, we can issue this command on our attack box:
#### Locate
`tylapcheong@htb[/htb]$ locate exploits`

We want to look for the directories in the output associated with Metasploit Framework. On Pwnbox, Metasploit exploit modules are kept in:
`/usr/share/metasploit-framework/modules/exploits`

We can copy the code into a file and save it in `/usr/share/metasploit-framework/modules/exploits/linux/http`

We should also keep msf up to date using the commands `apt update; apt install metasploit-framework` or your local package manager.

## Using the rConfig Exploit and Gaining a Shell

In msfconsole, we can manually load the exploit using the command:

#### Select an Exploit
`msf6 > use exploit/linux/http/rconfig_vendors_auth_file_upload_rce`

With this exploit selected, we can list the options, input the proper settings specific to our network environment, and launch the exploit.

msf6 exploit(linux/http/rconfig_vendors_auth_file_upload_rce) > exploit


## Spawning a TTY Shell with Python

When we drop into the system shell, we notice that no prompt is present, yet we can still issue some system commands. This is a shell typically referred to as a `non-tty shell`. These shells have limited functionality and can often prevent our use of essential commands like `su` (`switch user`) and `sudo` (`super user do`), which we will likely need if we seek to escalate privileges

#### Interactive Python
```
python -c 'import pty; pty.spawn("/bin/sh")'
```