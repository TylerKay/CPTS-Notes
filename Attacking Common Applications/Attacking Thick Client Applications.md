
---

Thick client applications are the applications that are installed locally on our computers. Unlike thin client applications that run on a remote server and can be accessed through the web browser, these applications do not require internet access to run, and they perform better in processing power, memory, and storage capacity.

A critical security measure that, for example, `Java` has is a technology called `sandbox`. The sandbox is a virtual environment that allows untrusted code, such as code downloaded from the internet, to run safely on a user's system without posing a security risk.

A critical security measure that, for example, `Java` has is a technology called `sandbox`. The sandbox is a virtual environment that allows untrusted code, such as code downloaded from the internet, to run safely on a user's system without posing a security risk. Besides that, there are also `Java API restrictions` and `Code Signing` that helps to create a more secure environment.

Web-specific vulnerabilities like XSS, CSRF, and Clickjacking, do not apply to thick client applications. However, thick client applications are considered less secure than web applications with many attacks being applicable, including:

- Improper Error Handling.
- Hardcoded sensitive data.
- DLL Hijacking.
- Buffer Overflow.
- SQL Injection.
- Insecure Storage.
- Session Management.
## Penetration Testing Steps

Thick client applications are considered more complex than others, and the attacking surface can be large. Thick client application penetration testing can be done both using automated tools and manually. The following steps are usually followed when testing thick client applications.

#### Information Gathering
In this step, penetration testers have to identify the application architecture, the programming languages and frameworks that have been used, and understand how the application and the infrastructure work. They should also need to identify technologies that are used on the client and server sides and find entry points and user inputs. Testers should also look for identifying common vulnerabilities like the ones we mentioned earlier at the end of the About section. The following tools will help us gather information.

```
CFF Explorer	Detect It Easy	Process Monitor	Strings
```

This interaction with servers and other external systems can expose thick clients to vulnerabilities similar to those found in web applications, including command injection, weak access control, and SQL injection.

Dynamic analysis should also be performed in this step, as thick client applications store sensitive information in the memory as well.

|||||
|---|---|---|---|
|[Ghidra](https://www.ghidra-sre.org/)|[IDA](https://hex-rays.com/ida-pro/)|[OllyDbg](http://www.ollydbg.de/)|[Radare2](https://www.radare.org/r/index.html)|
|[dnSpy](https://github.com/dnSpy/dnSpy)|[x64dbg](https://x64dbg.com/)|[JADX](https://github.com/skylot/jadx)|[Frida](https://frida.re/)|

Penetration testers that are performing traffic analysis on thick client applications should be familiar with tools like:

|||||
|---|---|---|---|
|[Wireshark](https://www.wireshark.org/)|[tcpdump](https://www.tcpdump.org/)|[TCPView](https://learn.microsoft.com/en-us/sysinternals/downloads/tcpview)|[Burp Suite](https://portswigger.net/burp)|

#### Server Side Attacks

Server-side attacks in thick client applications are similar to web application attacks, and penetration testers should pay attention to the most common ones including most of the OWASP Top Ten.

## Retrieving hardcoded Credentials from Thick-Client Applications

The following scenario walks us through enumerating and exploiting a thick client application, in order to move laterally inside a corporative network during penetration testing. The scenario starts after we have gained access to an exposed SMB service.

Exploring the `NETLOGON` share of the SMB service reveals `RestartOracle-Service.exe` among other files. Downloading the executable locally and running it through the command line, it seems like it does not run or it runs something hidden.

```
C:\Apps>.\Restart-OracleService.exe
C:\Apps>
```

Downloading the tool `ProcMon64` from [SysInternals](https://learn.microsoft.com/en-gb/sysinternals/downloads/procmon) and monitoring the process reveals that the executable indeed creates a temp file in `C:\Users\Matt\AppData\Local\Temp`.

In order to capture the files, it is required to change the permissions of the `Temp` folder to disallow file deletions. To do this, we right-click the folder `C:\Users\Matt\AppData\Local\Temp` and under `Properties` -> `Security` -> `Advanced` -> `cybervaca` -> `Disable inheritance` -> `Convert inherited permissions into explicit permissions on this object` -> `Edit` -> `Show advanced permissions`, we deselect the `Delete subfolders and files`, and `Delete` checkboxes.