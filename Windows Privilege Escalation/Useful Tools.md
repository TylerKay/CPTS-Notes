# Useful Windows PrivEsc Tools

## Tool Reference
|Tool|Description|
|---|---|
|[Seatbelt](https://github.com/GhostPack/Seatbelt)|C# project for performing a wide variety of local privilege escalation checks|
|[winPEAS](https://github.com/carlospolop/privilege-escalation-awesome-scripts-suite/tree/master/winPEAS)|WinPEAS is a script that searches for possible paths to escalate privileges on Windows hosts. All of the checks are explained [here](https://book.hacktricks.wiki/en/windows-hardening/checklist-windows-privilege-escalation.html)|
|[PowerUp](https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Privesc/PowerUp.ps1)|PowerShell script for finding common Windows privilege escalation vectors that rely on misconfigurations. It can also be used to exploit some of the issues found|
|[SharpUp](https://github.com/GhostPack/SharpUp)|C# version of PowerUp|
|[JAWS](https://github.com/411Hall/JAWS)|PowerShell script for enumerating privilege escalation vectors written in PowerShell 2.0|
|[SessionGopher](https://github.com/Arvanaghi/SessionGopher)|SessionGopher is a PowerShell tool that finds and decrypts saved session information for remote access tools. It extracts PuTTY, WinSCP, SuperPuTTY, FileZilla, and RDP saved session information|
|[Watson](https://github.com/rasta-mouse/Watson)|Watson is a .NET tool designed to enumerate missing KBs and suggest exploits for Privilege Escalation vulnerabilities.|
|[LaZagne](https://github.com/AlessandroZ/LaZagne)|Tool used for retrieving passwords stored on a local machine from web browsers, chat tools, databases, Git, email, memory dumps, PHP, sysadmin tools, wireless network configurations, internal Windows password storage mechanisms, and more|
|[Windows Exploit Suggester - Next Generation](https://github.com/bitsadmin/wesng)|WES-NG is a tool based on the output of Windows' `systeminfo` utility which provides the list of vulnerabilities the OS is vulnerable to, including any exploits for these vulnerabilities. Every Windows OS between Windows XP and Windows 10, including their Windows Server counterparts, is supported|
|[Sysinternals Suite](https://docs.microsoft.com/en-us/sysinternals/downloads/sysinternals-suite)|We will use several tools from Sysinternals in our enumeration including [AccessChk](https://docs.microsoft.com/en-us/sysinternals/downloads/accesschk), [PipeList](https://docs.microsoft.com/en-us/sysinternals/downloads/pipelist), and [PsService](https://docs.microsoft.com/en-us/sysinternals/downloads/psservice)|
We can also find pre-compiled binaries of `Seatbelt` and `SharpUp` [here](https://github.com/r3motecontrol/Ghostpack-CompiledBinaries), and standalone binaries of `LaZagne` [here](https://github.com/AlessandroZ/LaZagne/releases/). It is recommended that we always compile our tools from the source if using them in a client environment.

### Upload Location Tip
If few directories are writable by your current user, **`C:\Windows\Temp`** is usually writable by `BUILTIN\Users` — a safe default upload target.

---

## Tools vs. Manual Enumeration — Tradeoffs

**Pros of tools:**
- Speed up enumeration significantly
- Provide detailed, structured output
- Useful for both pentesters and sysadmins (identifying low-hanging fruit, periodic security checks, gold-image reviews, change-impact analysis)

**Cons of tools:**
- **Information overload** — tools like winPEAS return huge amounts of mostly irrelevant output
- **False positives/negatives** — requires deep manual knowledge to validate findings
- **Detection risk** — well-known tools are readily flagged by AV/EDR (e.g. Cylance, Carbon Black)
  - Example: LaZagne v2.4.3 precompiled binary was detected by **47/70** vendors on VirusTotal.
- Excessive automated enumeration can (rarely) cause system instability on fragile systems

**Evasion note:** Techniques exist to bypass AV (removing comments, renaming functions, encrypting executables, etc.) — covered in a separate module. Course labs generally assume Defender is temporarily permissive to focus on finding issues rather than evading defenses.

---

## Key Takeaway
Tools are valuable for speed and coverage, but should **supplement, not replace**, manual enumeration skill. Understanding techniques manually ensures you:
- Catch flaws tools miss (false negatives)
- Correctly interpret/validate tool output (avoid false positives)
- Can operate in restricted environments (air-gapped, no internet, no USB, no tool upload capability)
- Can clearly explain methodology and findings to a client at any stage