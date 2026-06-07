# FTP

---

The `File Transfer Protocol` (`FTP`) is one of the oldest protocols on the Internet. The FTP runs within the application layer of the TCP/IP protocol stack.

#### Install vsFTPd

`tylapcheong@htb[/htb]$ sudo apt install vsftpd`

#### FTPUSERS


`tylapcheong@htb[/htb]$ cat /etc/ftpusers guest john kevin`

## Dangerous Settings
|**Setting**|**Description**|
|---|---|
|`anonymous_enable=YES`|Allowing anonymous login?|
|`anon_upload_enable=YES`|Allowing anonymous to upload files?|
|`anon_mkdir_write_enable=YES`|Allowing anonymous to create new directories?|
|`no_anon_password=YES`|Do not ask anonymous for password?|
|`anon_root=/home/username/ftp`|Directory for anonymous.|
|`write_enable=YES`|Allow the usage of FTP commands: STOR, DELE, RNFR, RNTO, MKD, RMD, APPE, and SITE?|
#### Anonymous Login

`tylapcheong@htb[/htb]$ ftp 10.129.14.136`

|**Setting**|**Description**|
|---|---|
|`dirmessage_enable=YES`|Show a message when they first enter a new directory?|
|`chown_uploads=YES`|Change ownership of anonymously uploaded files?|
|`chown_username=username`|User who is given ownership of anonymously uploaded files.|
|`local_enable=YES`|Enable local users to login?|
|`chroot_local_user=YES`|Place local users into their home directory?|
|`chroot_list_enable=YES`|Use a list of local users that will be placed in their home directory?|

|**Setting**|**Description**|
|---|---|
|`hide_ids=YES`|All user and group information in directory listings will be displayed as "ftp".|
|`ls_recurse_enable=YES`|Allows the use of recurse listings.|

Another helpful setting we can use for our purposes is the `ls_recurse_enable=YES`. This is often set on the vsFTPd server to have a better overview of the FTP directory structure, as it allows us to see all the visible content at once.
#### Recursive Listing

`ftp> ls -R`

#### Download a File
ftp> get Important\ Notes.txt

#### Download All Available Files

`tylapcheong@htb[/htb]$ wget -m --no-passive ftp://anonymous:anonymous@10.129.14.136`

With the `PUT` command, we can upload files in the current folder to the FTP server.
`ftp> put testupload.txt`


#### Nmap FTP Scripts
`tylapcheong@htb[/htb]$ sudo nmap --script-updatedb`

All the NSE scripts are located on the Pwnbox in `/usr/share/nmap/scripts/`, but on our systems, we can find them using a simple command.

`tylapcheong@htb[/htb]$ find / -type f -name ftp* 2>/dev/null | grep scripts`


#### Nmap

`tylapcheong@htb[/htb]$ sudo nmap -sV -p21 -sC -A 10.129.14.136`\

#### Nmap Script Trace

Nmap also provides the ability to trace the progress of NSE scripts at the network level if we use the `--script-trace` option in our scans. This lets us see what commands Nmap sends, what ports are used, and what responses we receive from the scanned server.

`tylapcheong@htb[/htb]$ sudo nmap -sV -p21 -sC -A 10.129.14.136 --script-trace`

 
 
 If necessary, we can, of course, use other applications such as `netcat` or `telnet` to interact with the FTP server.
#### Service Interaction
`tylapcheong@htb[/htb]$ nc -nv 10.129.14.136 21`
`tylapcheong@htb[/htb]$ telnet 10.129.14.136 21`

It looks slightly different if the FTP server runs with TLS/SSL encryption. Because then we need a client that can handle TLS/SSL.

The good thing about using `openssl` is that we can see the SSL certificate, which can also be helpful.
`tylapcheong@htb[/htb]$ openssl s_client -connect 10.129.14.136:21 -starttls ftp`

