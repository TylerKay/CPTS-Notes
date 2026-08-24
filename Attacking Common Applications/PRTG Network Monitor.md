[PRTG Network Monitor](https://www.paessler.com/prtg) is agentless network monitor software. It can be used to monitor bandwidth usage, uptime and collect statistics from various hosts, including routers, switches, servers, and more. It works with an autodiscovery mode to scan areas of a network and create a device list. Once this list is created, it can gather further information from the detected devices using protocols such as ICMP, SNMP, WMI, NetFlow, and more. Devices can also communicate with the tool via a REST API. The software runs entirely from an AJAX-based website, but there is a desktop application available for Windows, Linux, and macOS. A few interesting data points about PRTG:

## Discovery/Footprinting/Enumeration

We can quickly discover PRTG from an Nmap scan. It can typically be found on common web ports such as 80, 443, or 8080. It is possible to change the web interface port in the Setup section when logged in as an admin.

        shellsession
`tylapcheong@htb[/htb]$ sudo nmap -sV -p- --open -T4 10.129.201.50`

PRTG also shows up in the EyeWitness scan we performed earlier. Here we can see that EyeWitness lists the default credentials `prtgadmin:prtgadmin`. They are typically pre-filled on the login page, and we often find them unchanged. Vulnerability scanners such as Nessus also have [plugins](https://www.tenable.com/plugins/nessus/51874) that detect the presence of PRTG.

Once we have discovered PRTG, we can confirm by browsing to the URL and are presented with the login page.

From the enumeration we performed so far, it seems to be PRTG version `17.3.33.2830` and is likely vulnerable to [CVE-2018-9276](https://nvd.nist.gov/vuln/detail/CVE-2018-9276) which is an authenticated command injection in the PRTG System Administrator web console for PRTG Network Monitor before version 18.2.39. Based on the version reported by Nmap, we can assume that we are dealing with a vulnerable version. Using `cURL` we can see that the version number is indeed `17.3.33.283`.


```
tylapcheong@htb[/htb]$ curl -s http://10.129.201.50:8080/index.htm -A "Mozilla/5.0 (compatible;  MSIE 7.01; Windows NT 5.0)" | grep version
```

Our first attempt to log in with the default credentials fails, but a few tries later, we are in with `prtgadmin:Password123`.

## Leveraging Known Vulnerabilities

Once logged in, we can explore a bit, but we know that this is likely vulnerable to a command injection flaw so let's get right to it. This excellent [blog post](https://www.codewatch.org/blog/?p=453) by the individual who discovered this flaw does a great job of walking through the initial discovery process and how they discovered it. When creating a new notification, the `Parameter` field is passed directly into a PowerShell script without any type of input sanitization.

To begin, mouse over `Setup` in the top right and then the `Account Settings` menu and finally click on `Notifications`.

Next, click on `Add new notification`.

Give the notification a name and scroll down and tick the box next to `EXECUTE PROGRAM`. Under `Program File`, select `Demo exe notification - outfile.ps1` from the drop-down. Finally, in the parameter field, enter a command. For our purposes, we will add a new local admin user by entering `test.txt;net user prtgadm1 Pwn3d_by_PRTG! /add;net localgroup administrators prtgadm1 /add`. During an actual assessment, we may want to do something that does not change the system, such as getting a reverse shell or connection to our favorite C2. Finally, click the `Save` button.

After clicking `Save`, we will be redirected to the `Notifications` page and see our new notification named `pwn` in the list.

Now, we could have scheduled the notification to run (and execute our command) at a later time when setting it up. This could prove handy as a persistence mechanism during a long-term engagement and is worth taking note of. Schedules can be modified in the account settings menu if we want to set it up to run at a specific time every day to get our connection back or something of that nature. At this point, all that is left is to click the `Test` button to run our notification and execute the command to add a local admin user. After clicking `Test` we will get a pop-up that says `EXE notification is queued up`.

Since this is a blind command execution, we won't get any feedback, so we'd have to either check our listener for a connection back or, in our case, check to see if we can authenticate to the host as a local admin. We can use `CrackMapExec` to confirm local admin access. We could also try to RDP to the box, access over WinRM, or use a tool such as [evil-winrm](https://github.com/Hackplayers/evil-winrm) or something from the [impacket](https://github.com/SecureAuthCorp/impacket) toolkit such as `wmiexec.py` or `psexec.py`.

```
tylapcheong@htb[/htb]$ sudo crackmapexec smb 10.129.201.50 -u prtgadm1 -p Pwn3d_by_PRTG! 

SMB         10.129.201.50   445    APP03            [*] Windows 10.0 Build 17763 (name:APP03) (domain:APP03) (signing:False) (SMBv1:False)
SMB         10.129.201.50   445    APP03            [+] APP03\prtgadm1:Pwn3d_by_PRTG! (Pwn3d!)
```


Using evil-winrm to get remote code execution
```
evil-winrm -i 10.129.57.173 -u prtgadm1 -p Pwn3d_by_PRTG!
```