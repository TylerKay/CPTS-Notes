# Introduction to Linux Privilege Escalation

Full admin access on Linux = root account. After landing a low-privileged shell, the goal is to escalate to root — enabling traffic capture, sensitive file access, and (if domain-joined) NTLM hash extraction for AD attacks.

## Enumeration — The Key to PrivEsc

Manual enumeration matters even with helper scripts (e.g. LinEnum) available. Key areas to check:

### 1. OS Version
- Identify distro (Ubuntu, Debian, FreeBSD, Fedora, SUSE, RHEL, CentOS, etc.)
- Determines available tooling and potential public exploits for that specific version.

### 2. Kernel Version
- Public kernel exploits may exist for specific versions.
- ⚠️ Kernel exploits can cause instability/crashes — use caution on production systems.

### 3. Running Services
- Check for services running **as root** — misconfigured/vulnerable ones are easy wins.
- Known vulnerable services: Nagios, Exim, Samba, ProFTPd, etc.
- Example: `CVE-2016-9566` — local privesc in Nagios Core < 4.2.4.

```bash
ps aux | grep root
```

### 4. Installed Packages & Versions
- Check for outdated/vulnerable packages.
- Example: **Screen v4.05.00** has a known easily-exploitable privesc vulnerability.

### 5. Logged-in Users
- Reveals possible lateral movement paths.
```bash
ps au
```

### 6. User Home Directories
- Check accessibility of other users' home dirs.
- Look for SSH keys, config files, and credentials.
```bash
ls /home
ls -la /home/<user>/
```
- If an SSH key is found, it may allow SSH access to this host or others on the network. Cross-reference with ARP cache for other reachable hosts.
```bash
ls -l ~/.ssh
```

### 7. Bash History
- Look for passwords passed as CLI args, git activity, cron setup, etc.
```bash
history
```

### 8. Sudo Privileges
- Check what the current user can run as root.
- `NOPASSWD` entries = no password prompt needed.
- Full sudo access → `sudo su` grants an instant root session.
```bash
sudo -l
```

### 9. Configuration Files
- Search `.conf` / `.config` files for usernames, passwords, secrets.

### 10. Readable Shadow File / Passwd Hashes
- Readable `/etc/shadow` → grab hashes for offline cracking.
- Sometimes hashes appear directly in `/etc/passwd` (not common, but seen on embedded devices/routers).
```bash
cat /etc/passwd
```

### 11. Cron Jobs
- Look for jobs vulnerable to relative-path issues or weak permissions.
```bash
ls -la /etc/cron.daily/
```

### 12. Unmounted File Systems / Additional Drives
- May contain sensitive files, passwords, or backups.
```bash
lsblk
```

### 13. SETUID / SETGID Binaries
- Binaries with these bits let users run commands as root without full root access.
- Many have exploitable functionality for root shell access.

### 14. Writable Directories
- Useful for staging tools.
- Writable dirs tied to cron jobs can hint at execution frequency and privesc potential.
```bash
find / -path /proc -prune -o -type d -perm -o+w 2>/dev/null
```

### 15. Writable Files
- World-writable scripts/configs — especially those run as root via cron — can be modified to append malicious commands.
```bash
find / -path /proc -prune -o -type f -perm -o+w 2>/dev/null
```

---

**Summary:** Thorough enumeration across OS/kernel version, services, packages, users, sudo rights, cron jobs, file permissions, and writable paths builds the foundation for identifying a viable Linux privilege escalation vector.