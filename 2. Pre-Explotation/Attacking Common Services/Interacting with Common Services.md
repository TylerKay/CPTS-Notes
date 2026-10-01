## Server Message Block (SMB)
#### Windows

There are different ways we can interact with a shared folder using Windows, and we will explore a couple of them. On Windows GUI, we can press `[WINKEY] + [R]` to open the Run dialog box and type the file share location, e.g.: `\\192.168.220.129\Finance\`



The command [net use](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/gg651155\(v=ws.11\)) connects a computer to or disconnects a computer from a shared resource or displays information about computer connections. We can connect to a file share with the following command and map its content to the drive letter `n`.

#### Windows CMD - Net Use
`C:\htb> net use n: \\192.168.220.129\Finance`

We can also provide a username and password to authenticate to the share.

`C:\htb> net use n: \\192.168.220.129\Finance /user:plaintext Password123`

#### Windows CMD - DIR
```
C:\htb> dir n: /a-d /s /b | find /c ":\"
29302
```
We found 29,302 files. Let's walk through the command:

```
dir n: /a-d /s /b | find /c ":\"
```

| **Syntax** | **Description**                                                |
| ---------- | -------------------------------------------------------------- |
| `dir`      | Application                                                    |
| `n:`       | Directory or drive to search                                   |
| `/a-d`     | `/a` is the attribute and `-d` means not directories           |
| `/s`       | Displays files in a specified directory and all subdirectories |
| `/b`       | Uses bare format (no heading information or summary)           |

The following command `| find /c ":\\"` process the output of `dir n: /a-d /s /b`

```
C:\htb>dir n:\*cred* /s /b

n:\Contracts\private\credentials.txt


C:\htb>dir n:\*secret* /s /b

n:\Contracts\private\secret.txt
```

If we want to search for a specific word within a text file, we can use [findstr](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/findstr).
#### Windows CMD - Findstr
```
c:\htb>findstr /s /i cred n:\*.*

n:\Contracts\private\secret.txt:file with all credentials
n:\Contracts\private\credentials.txt:admin:SecureCredentials!
```

#### Windows PowerShell
```
PS C:\htb> Get-ChildItem \\192.168.220.129\Finance\

    Directory: \\192.168.220.129\Finance

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----         2/23/2022   3:27 PM                Contracts
```

Instead of net use, we can use New-PSDrive in PowerShell.
```
PS C:\htb> New-PSDrive -Name "N" -Root "\\192.168.220.129\Finance" -PSProvider "FileSystem"

Name           Used (GB)     Free (GB) Provider      Root                                               CurrentLocation
----           ---------     --------- --------      ----                                               ---------------
N                                      FileSystem    \\192.168.220.129\Finance
```

To provide a username and password with Powershell, we need to create a [PSCredential object](https://docs.microsoft.com/en-us/dotnet/api/system.management.automation.pscredential). It offers a centralized way to manage usernames, passwords, and credentials.
#### Windows PowerShell - PSCredential Object
```
PS C:\htb> $username = 'plaintext'
PS C:\htb> $password = 'Password123'
PS C:\htb> $secpassword = ConvertTo-SecureString $password -AsPlainText -Force
PS C:\htb> $cred = New-Object System.Management.Automation.PSCredential $username, $secpassword
PS C:\htb> New-PSDrive -Name "N" -Root "\\192.168.220.129\Finance" -PSProvider "FileSystem" -Credential $cred

Name           Used (GB)     Free (GB) Provider      Root                                                              CurrentLocation
----           ---------     --------- --------      ----                                                              ---------------
N                                      FileSystem    \\192.168.220.129\Finance
```

We can use the property `-Include` to find specific items from the directory specified by the Path parameter.
```
PS C:\htb> Get-ChildItem -Recurse -Path N:\ -Include *cred* -File

    Directory: N:\Contracts\private

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----         2/23/2022   4:36 PM             25 credentials.txt
```

The `Select-String` cmdlet uses regular expression matching to search for text patterns in input strings and files. We can use `Select-String` similar to `grep` in UNIX or `findstr.exe` in Windows.
#### Windows PowerShell - Select-String
```
PS C:\htb> Get-ChildItem -Recurse -Path N:\ | Select-String "cred" -List

N:\Contracts\private\secret.txt:1:file with all credentials
N:\Contracts\private\credentials.txt:1:admin:SecureCredentials!
```

#### Linux - Mount
```
tylapcheong@htb[/htb]$ sudo mkdir /mnt/Finance
tylapcheong@htb[/htb]$ sudo mount -t cifs -o username=plaintext,password=Password123,domain=. //192.168.220.129/Finance /mnt/Finance
```

As an alternative, we can use a credential file.
`tylapcheong@htb[/htb]$ mount -t cifs //192.168.220.129/Finance /mnt/Finance -o credentials=/path/credentialfile`

The file `credentialfile` has to be structured like this:
#### CredentialFile
        txt
```
username=plaintext
password=Password123
domain=.
```

Note: We need to install `cifs-utils` to connect to an SMB share folder. To install it we can execute from the command line `sudo apt install cifs-utils`.

#### Linux - Find
`tylapcheong@htb[/htb]$ find /mnt/Finance/ -name *cred* /mnt/Finance/Contracts/private/credentials.txt`

Next, let's find files that contain the string `cred`:
```
tylapcheong@htb[/htb]$ grep -rn /mnt/Finance/ -ie cred

/mnt/Finance/Contracts/private/credentials.txt:1:admin:SecureCredentials!
/mnt/Finance/Contracts/private/secret.txt:1:file with all credentials
```
## Other Services

There are other file-sharing services such as FTP, TFTP, and NFS that we can attach (mount) using different tools and commands.
#### Email

We typically need two protocols to send and receive messages, one for sending and another for receiving.

We can use a mail client such as [Evolution](https://wiki.gnome.org/Apps/Evolution), the official personal information manager, and mail client for the GNOME Desktop Environment. We can interact with an email server to send or receive messages with a mail client. To install Evolution, we can use the following command:

#### Linux - Install Evolution
`tylapcheong@htb[/htb]$ sudo apt-get install evolution ...SNIP...`

Note: If an error appears when starting evolution indicating "bwrap: Can't create file at ...", use this command to start evolution `export WEBKIT_FORCE_SANDBOX=0 && evolution`.

## Command Line Utilities

#### MSSQL

To interact with [MSSQL (Microsoft SQL Server)](https://www.microsoft.com/en-us/sql-server/sql-server-downloads) with Linux we can use [sqsh](https://en.wikipedia.org/wiki/Sqsh) or [sqlcmd](https://docs.microsoft.com/en-us/sql/tools/sqlcmd-utility) if you are using Windows. `Sqsh` is much more than a friendly prompt. It is intended to provide much of the functionality provided by a command shell, such as variables, aliasing, redirection, pipes, back-grounding, job control, history, command substitution, and dynamic configuration. We can start an interactive SQL session as follows:

#### Linux - SQSH
```
tylapcheong@htb[/htb]$ sqsh -S 10.129.20.13 -U username -P Password123
```

The `sqlcmd` utility lets you enter Transact-SQL statements, system procedures, and script files through a variety of available modes:

- At the command prompt.
- In Query Editor in SQLCMD mode.
- In a Windows script file.
- In an operating system (Cmd.exe) job step of a SQL Server Agent job.

#### Windows - SQLCMD
```
C:\htb> sqlcmd -S 10.129.20.13 -U username -P Password123
```

#### MySQL

To interact with [MySQL](https://en.wikipedia.org/wiki/MySQL), we can use MySQL binaries for Linux (`mysql`) or Windows (`mysql.exe`). MySQL comes pre-installed on some Linux distributions, but we can install MySQL binaries for Linux or Windows using this [guide](https://dev.mysql.com/doc/mysql-getting-started/en/#mysql-getting-started-installing). Start an interactive SQL Session using Linux:

#### Linux - MySQL
`tylapcheong@htb[/htb]$ mysql -u username -pPassword123 -h 10.129.20.13`

#### Windows - MySQL
`C:\htb> mysql.exe -u username -pPassword123 -h 10.129.20.13`

 [dbeaver](https://github.com/dbeaver/dbeaver) is a multi-platform database tool for Linux, macOS, and Windows that supports connecting to multiple database engines such as MSSQL, MySQL, PostgreSQL, among others, making it easy for us, as an attacker, to interact with common database servers.
#### Install dbeaver
`tylapcheong@htb[/htb]$ sudo dpkg -i dbeaver-<version>.deb`

#### Run dbeaver
`tylapcheong@htb[/htb]$ dbeaver &`

#### Tools to Interact with Common Services

|**SMB**|**FTP**|**Email**|**Databases**|
|---|---|---|---|
|[smbclient](https://www.samba.org/samba/docs/current/man-html/smbclient.1.html)|[ftp](https://linux.die.net/man/1/ftp)|[Thunderbird](https://www.thunderbird.net/en-US/)|[mssql-cli](https://github.com/dbcli/mssql-cli)|
|[CrackMapExec](https://github.com/byt3bl33d3r/CrackMapExec)|[lftp](https://lftp.yar.ru/)|[Claws](https://www.claws-mail.org/)|[mycli](https://github.com/dbcli/mycli)|
|[SMBMap](https://github.com/ShawnDEvans/smbmap)|[ncftp](https://www.ncftp.com/)|[Geary](https://wiki.gnome.org/Apps/Geary)|[mssqlclient.py](https://github.com/SecureAuthCorp/impacket/blob/master/examples/mssqlclient.py)|
|[Impacket](https://github.com/SecureAuthCorp/impacket)|[filezilla](https://filezilla-project.org/)|[MailSpring](https://getmailspring.com/)|[dbeaver](https://github.com/dbeaver/dbeaver)|
|[psexec.py](https://github.com/SecureAuthCorp/impacket/blob/master/examples/psexec.py)|[crossftp](http://www.crossftp.com/)|[mutt](http://www.mutt.org/)|[MySQL Workbench](https://dev.mysql.com/downloads/workbench/)|
|[smbexec.py](https://github.com/SecureAuthCorp/impacket/blob/master/examples/smbexec.py)||[mailutils](https://mailutils.org/)|[SQL Server Management Studio or SSMS](https://docs.microsoft.com/en-us/sql/ssms/download-sql-server-management-studio-ssms)|
|||[sendEmail](https://github.com/mogaal/sendemail)||
|||[swaks](http://www.jetmore.org/john/code/swaks/)||
|||[sendmail](https://en.wikipedia.org/wiki/Sendmail)||
