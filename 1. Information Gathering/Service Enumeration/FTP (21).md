# FTP (21)

---

The `File Transfer Protocol` (`FTP`) is one of the oldest protocols on the Internet. It runs within the application layer of the TCP/IP protocol stack (same layer as HTTP or POP).

#### How It Works

- Two channels are opened per connection:
	- **Control channel** – TCP port `21`: client sends commands, server returns status codes.
	- **Data channel** – TCP port `20`: used exclusively for data transmission; interrupted transfers can be resumed.
- **Active mode**: client connects via port 21 and tells the server which client-side port to send data to. Fails when a firewall blocks inbound connections to the client.
- **Passive mode**: server announces a port, the *client* initiates the data connection → firewalls don't block it.
- FTP is a **clear-text protocol** → credentials/data can be sniffed under the right network conditions.
- Usually requires credentials, but servers may offer **anonymous FTP** (no password, limited permissions).

> [!tip] Related
> For the UDP-based sibling protocol, see [[TFTP (UDP 69)]] — no authentication, no directory listing, local/protected networks only.

## Default Configuration (vsFTPd)

Most common FTP server on Linux. Config: `/etc/vsftpd.conf`

`tylapcheong@htb[/htb]$ sudo apt install vsftpd`
`tylapcheong@htb[/htb]$ cat /etc/vsftpd.conf | grep -v "#"`

|**Setting**|**Description**|
|---|---|
|`listen=NO`|Run from inetd or as a standalone daemon?|
|`listen_ipv6=YES`|Listen on IPv6?|
|`anonymous_enable=NO`|Enable Anonymous access?|
|`local_enable=YES`|Allow local users to login?|
|`dirmessage_enable=YES`|Display active directory messages when users go into certain directories?|
|`use_localtime=YES`|Use local time?|
|`xferlog_enable=YES`|Activate logging of uploads/downloads?|
|`connect_from_port_20=YES`|Connect from port 20?|
|`secure_chroot_dir=/var/run/vsftpd/empty`|Name of an empty directory|
|`pam_service_name=vsftpd`|The name of the PAM service vsftpd will use.|
|`rsa_cert_file=/etc/ssl/certs/ssl-cert-snakeoil.pem`|Location of the RSA certificate for SSL encrypted connections.|
|`rsa_private_key_file=/etc/ssl/private/ssl-cert-snakeoil.key`|Location of the RSA private key.|
|`ssl_enable=NO`|Enable SSL?|

#### FTPUSERS

`/etc/ftpusers` **denies** listed users access to the FTP service, even if they exist on the system:

`tylapcheong@htb[/htb]$ cat /etc/ftpusers`

```
guest
john
kevin
```

## Dangerous Settings

|**Setting**|**Description**|
|---|---|
|`anonymous_enable=YES`|Allowing anonymous login?|
|`anon_upload_enable=YES`|Allowing anonymous to upload files?|
|`anon_mkdir_write_enable=YES`|Allowing anonymous to create new directories?|
|`no_anon_password=YES`|Do not ask anonymous for password?|
|`anon_root=/home/username/ftp`|Directory for anonymous.|
|`write_enable=YES`|Allow the usage of FTP commands: STOR, DELE, RNFR, RNTO, MKD, RMD, APPE, and SITE?|

|**Setting**|**Description**|
|---|---|
|`dirmessage_enable=YES`|Show a message when they first enter a new directory?|
|`chown_uploads=YES`|Change ownership of anonymously uploaded files?|
|`chown_username=username`|User who is given ownership of anonymously uploaded files.|
|`local_enable=YES`|Enable local users to login?|
|`chroot_local_user=YES`|Place local users into their home directory?|
|`chroot_list_enable=YES`|Use a list of local users that will be placed in their home directory?|
|`hide_ids=YES`|All user and group information in directory listings will be displayed as "ftp".|
|`ls_recurse_enable=YES`|Allows the use of recurse listings.|

- On connect, the server returns code `220` with its **banner** — often includes description/version/system type.
- `hide_ids=YES` replaces real UIDs/GIDs with `ftp` in listings → harder to identify write/upload rights (defends against username harvesting for brute-force; though fail2ban is standard nowadays).
- `ls_recurse_enable=YES` allows `ls -R` to see the entire visible directory tree at once.

#### Anonymous Login

```
tylapcheong@htb[/htb]$ ftp 10.129.14.136

220 "Welcome to the HTB Academy vsFTP service."
Name (10.129.14.136:cry0l1t3): anonymous
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
```

Even without download rights, listing contents alone yields useful information for other approaches.

#### Useful Client Commands

- `status` – shows connection/mode settings overview
- `debug` – debugging on; prints each command sent (`---> PORT ...`, `---> LIST`)
- `trace` – packet tracing on

#### Recursive Listing

```
ftp> ls -R
```

Lists all files/folders across the whole accessible tree in one shot (e.g. reveals `Clients/HackTheBox`, `Clients/Inlanefreight`, `Documents`, etc.).

## Downloading & Uploading Files

Downloading files lets us inspect them locally; uploading matters because web-synced FTP folders can lead to direct webserver access or a reverse shell. Uploaded files can also enable LFI-driven command execution, and FTP logs themselves can be leveraged toward Remote Command Execution (RCE).

#### Download a File

```
ftp> get Important\ Notes.txt
```

#### Download All Available Files

Mirrors the whole tree via wget — creates a folder named after the target IP containing everything. Can trigger alarms (bulk downloads are abnormal behavior).

```
tylapcheong@htb[/htb]$ wget -m --no-passive ftp://anonymous:anonymous@10.129.14.136
tylapcheong@htb[/htb]$ tree .
```

#### Upload a File

With `PUT` we can upload files from the current folder to the FTP server:

```
ftp> put testupload.txt
```

Always check whether anonymous users can write — admins often assume internal components are unreachable and neglect hardening.

## Footprinting the Service

#### Nmap FTP Scripts

```
tylapcheong@htb[/htb]$ sudo nmap --script-updatedb
tylapcheong@htb[/htb]$ find / -type f -name ftp* 2>/dev/null | grep scripts
```

Key scripts found in `/usr/share/nmap/scripts/`:
- `ftp-anon.nse` – checks anonymous login; if allowed, renders the FTP root contents (flags `[NSE: writeable]`)
- `ftp-syst.nse` – executes `STAT` → server status/config + exact version (e.g. `vsFTPD 3.0.3 - secure, fast, stable`)
- `ftp-brute.nse`, `ftp-bounce.nse`, `ftp-vsftpd-backdoor.nse`, `ftp-proftpd-backdoor.nse`, `ftp-vuln-cve2010-4221.nse`, `ftp-libopie.nse`

#### Nmap Scan

```
tylapcheong@htb[/htb]$ sudo nmap -sV -p21 -sC -A 10.129.14.136
```

Default script scan fingerprints the service, then runs matching scripts: `ftp-anon` confirms anonymous access + directory listing; `ftp-syst` reveals session status, plain-text control/data connections, timeout, and version.

#### Nmap Script Trace

`--script-trace` traces NSE progress at the network level — shows exactly what commands Nmap sends, which ports are used, and server responses (e.g. four parallel CONNECTs, then the `220` banner received by one script).

```
tylapcheong@htb[/htb]$ sudo nmap -sV -p21 -sC -A 10.129.14.136 --script-trace
```

## Service Interaction

Plain interaction with netcat or telnet:

```
tylapcheong@htb[/htb]$ nc -nv 10.129.14.136 21
tylapcheong@htb[/htb]$ telnet 10.129.14.136 21
```

If the FTP server uses TLS/SSL, we need a TLS-capable client — `openssl`. Bonus: we get to see the **SSL certificate**, which often reveals:

- Hostname (e.g. `CN = master.inlanefreight.htb`)
- Organization / department (`O = Inlanefreight, OU = Dev`)
- Email address (`admin@inlanefreight.htb`) — potential usernames/targets
- Location-specific certs for companies with multiple sites

```
tylapcheong@htb[/htb]$ openssl s_client -connect 10.129.14.136:21 -starttls ftp
```

## Key Takeaways

- Port 21 = control (commands/status codes), port 20 = data; passive mode exists to survive client-side firewalls.
- Banner grab on connect (`220`) + `ftp-syst` give quick version fingerprinting.
- Always test: anonymous login → recursive listing → download everything (`wget -m`) → test upload (`put`).
- Writable anonymous FTP + webroot sync = likely path to shell/RCE.
- TLS-enabled FTP leaks hostname/org/email via certificate — free OSINT.
