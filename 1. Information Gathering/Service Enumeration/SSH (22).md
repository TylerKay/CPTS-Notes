# SSH (22)

---

## Overview

`Secure Shell` (`SSH`) enables two computers to establish an **encrypted, direct connection** within a possibly insecure network on standard **TCP port 22** — preventing third parties from intercepting sensitive data.

- Server can be configured to allow connections only from specific clients.
- Runs on all common operating systems; native on Linux/macOS (Unix origins); Windows needs a client program.
- **OpenSSH** (OpenBSD SSH) = open-source fork of the original commercial SSH server (SSH Communication Security).
- Usable beyond shells: send commands, **transfer files**, **port forwarding**, GUI management.

#### Protocol Versions

|**Version**|**Notes**|
|---|---|
|SSH-1|Vulnerable to **MITM attacks**|
|SSH-2|More advanced in encryption, speed, stability, security; not vulnerable to SSH-1's MITM flaw|

Banner decoding: `SSH-1.99-OpenSSH_3.9p1` → accepts **both** SSH-1 and SSH-2, OpenSSH 3.9p1 · `SSH-2.0-OpenSSH_8.2p1` → **SSH-2 only**, OpenSSH 8.2p1.

## Authentication Methods

OpenSSH supports six methods:

- Password authentication
- Public-key authentication
- Host-based authentication
- Keyboard authentication
- Challenge-response authentication
- GSSAPI authentication

#### Public Key Authentication (most common)

1. **Server authentication first**: server sends its public host key → client verifies identity. Only the *initial* connection carries MITM risk; the host key can't be forged because signing requires the private key (assuming the client verifies against a trusted source).
2. **Client authentication**: server already holds the encrypted hash of the user's password — meaning password entry is required on every new server during a session. Alternative: **public/private keypair**.
	- **Private key**: created individually per user machine, protected by a **passphrase** (should be longer than a typical password), stored *exclusively* locally, never leaves the machine.
	- Flow: server builds a cryptographic problem using the client's **public key** (stored on server) → client decrypts it with its **private key** → returns solution → connection allowed.
	- Passphrase entered **once per session** regardless of how many servers are contacted; log out afterwards so physical access to the local machine doesn't grant server access.

## Default Configuration

```
tylapcheong@htb[/htb]$ cat /etc/ssh/sshd_config | grep -v "#" | sed -r '/^\s*$/d'

Include /etc/ssh/sshd_config.d/*.conf
ChallengeResponseAuthentication no
UsePAM yes
X11Forwarding yes
PrintMotd no
AcceptEnv LANG LC_*
Subsystem       sftp    /usr/lib/openssh/sftp-server
```

Most settings are commented out and require manual configuration. Note `X11Forwarding yes` is default — X11 forwarding contained a command injection vulnerability in OpenSSH 7.2p1 (2016).

## Dangerous Settings

|**Setting**|**Description**|
|---|---|
|`PasswordAuthentication yes`|Allows password-based authentication.|
|`PermitEmptyPasswords yes`|Allows the use of empty passwords.|
|`PermitRootLogin yes`|Allows to log in as the root user.|
|`Protocol 1`|Uses an outdated version of encryption.|
|`X11Forwarding yes`|Allows X11 forwarding for GUI applications.|
|`AllowTcpForwarding yes`|Allows forwarding of TCP ports.|
|`PermitTunnel`|Allows tunneling.|
|`DebianBanner yes`|Displays a specific banner when logging in.|

`PasswordAuthentication yes` enables brute-forcing known usernames. Humans are lazy: common mutations append numbers/characters to the *end* of well-known passwords — attack tooling uses exactly these patterns. Hardening guides exist for locking SSH down.

## Footprinting the Service

#### ssh-audit

Fingerprints client- AND server-side configuration: general info + every encryption algorithm offered (attack surface for later crypto-level attacks):

```
tylapcheong@htb[/htb]$ git clone https://github.com/jtesta/ssh-audit.git && cd ssh-audit
tylapcheong@htb[/htb]$ ./ssh-audit.py 10.129.14.132
```

Key output sections:

- **banner** → exact software/version: `SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.3`
- **kex algorithms** → `[fail] using weak elliptic curves` (nistp variants), DH group sizes
- **host-key algorithms** → `[fail] ssh-rsa ... weak hashing algorithm` + deprecation notices; `[warn] weak random number generator could reveal the key` (ecdsa-nistp)

Older versions carry known CVEs — e.g. **CVE-2020-14145** (MITM on initial connection attempt).

#### Enumerate Allowed Auth Methods

Verbose SSH reveals which methods the server permits:

```
tylapcheong@htb[/htb]$ ssh -v cry0l1t3@10.129.14.132

debug1: Authentications that can continue: publickey,password,keyboard-interactive
```

For brute-forcing, force the method explicitly:

```
tylapcheong@htb[/htb]$ ssh -v cry0l1t3@10.129.14.132 -o PreferredAuthentications=password
```

## Workflow Cheat Sheet

1. Banner grab → decode protocol support + exact OpenSSH version (`SSH-x.x-OpenSSH_y.y`)
2. `ssh-audit.py <IP>` → weak kex/host-key algorithms, CVE-relevant version info
3. `ssh -v` → enumerate accepted authentication methods
4. If `password` is accepted → brute-force with mutated wordlists (common-password suffix patterns)
5. Check dangerous settings if we ever read `sshd_config`: root login, empty passwords, tunneling
