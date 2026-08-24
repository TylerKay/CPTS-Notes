# Environment Enumeration (Linux PrivEsc)

Enumeration is the foundation of privilege escalation. Helper scripts (LinPEAS, LinEnum) exist, but understanding **manual** enumeration is critical — tools can fail or be unavailable on target systems.

## Quick Orientation Commands
Run these first to get situational awareness (and screenshot for reporting/RCE evidence):

| Command | Purpose |
|---|---|
| `whoami` | Current user |
| `id` | Group memberships |
| `hostname` | Server name (naming convention may hint at role) |
| `ifconfig` / `ip a` | Subnet(s), additional NICs |
| `sudo -l` | Sudo rights — easy win if NOPASSWD present (`sudo su` → root) |

---

## OS & Kernel Fingerprinting

**OS Version** — identifies distro, tooling, and known public exploits.
```bash
cat /etc/os-release
```
- Check end-of-life/support status to gauge patch level likelihood.

**Kernel Version** — check against known CVEs/PoCs.
```bash
uname -a
# alt: cat /proc/version
```
⚠️ Kernel exploits can crash/destabilize systems — understand impact before running.

**Running Services** — especially those running as root (misconfig = easy win).
- Known vulnerable services: Nagios, Exim, Samba, ProFTPd.
- Example: `CVE-2016-9566` (Nagios Core < 4.2.4 local privesc).

---

## Shell & Environment Details

**PATH variable** — note it; misconfigured PATH can be abused for privesc later.
```bash
echo $PATH
```

**Environment variables** — may leak sensitive data (passwords, etc.).
```bash
env
```

**Hardware info** (CPU/virtualization platform):
```bash
lscpu
```

**Available login shells** — note if Tmux/Screen present (potential privesc vectors).
```bash
cat /etc/shells
```

**Security defenses in place** (may limit what's feasible):
- Exec Shield, iptables, AppArmor, SELinux, Fail2ban, Snort, UFW
- Often can't view configs without privilege, but knowing what's present saves wasted effort.

---

## Disks, Mounts & Network

**Block devices / drives:**
```bash
lsblk
```
- Look for unmounted/additional drives — may contain sensitive data if mountable.

**Printers** (`lpstat`) — check active/queued jobs for sensitive info.

**fstab** — check mounted & unmounted filesystems; grep for creds:
```bash
cat /etc/fstab
```

**Routing table** — reveals reachable networks/interfaces:
```bash
route
# alt: netstat -rn
```

**DNS config** (useful in AD environments):
```bash
cat /etc/resolv.conf
```

**ARP table** — shows recent host communication (cross-reference with SSH keys found):
```bash
arp -a
```

---

## User & Group Enumeration

**All users** — `/etc/passwd` format: username:password:UID:GID:info:home:shell
```bash
cat /etc/passwd
```
- Occasionally password hashes appear directly here (uncommon; seen on embedded devices/routers).

**Hash algorithm identification (by prefix):**

| Algorithm | Prefix |
|---|---|
| Salted MD5 | `$1$...` |
| SHA-256 | `$5$...` |
| SHA-512 | `$6$...` |
| BCrypt | `$2a$...` |
| Scrypt | `$7$...` |
| Argon2 | `$argon2i$...` |

**Users with login shells** (check shell versions for exploits, e.g. Shellshock on old Bash):
```bash
grep "sh$" /etc/passwd
```

**Groups:**
```bash
cat /etc/group
getent group sudo   # list members of a specific group
```

**Home directories** — enumerate each for sensitive files:
```bash
ls /home
```
- Check `.bash_history`, config files, and **SSH keys** (persistence, privesc, pivoting).
- Cross-reference ARP cache against usable SSH private keys.

---

## Low-Hanging Fruit

- Search `.conf` / `.config` files for creds.
- **Reuse found passwords** against all discovered users — password reuse is common.
- Check mounted vs. unmounted filesystems:
```bash
df -h                              # mounted
cat /etc/fstab | grep -v "#" | column -t   # unmounted (needs root to mount)
```

**Hidden files/directories** — often contain sensitive info even with read-only access:
```bash
find / -type f -name ".*" -exec ls -l {} \; 2>/dev/null | grep <user>
find / -type d -name ".*" -ls 2>/dev/null
```

**Temporary directories** — world-readable, may hold logs/script output:
```bash
ls -l /tmp /var/tmp /dev/shm
```
- `/tmp`: files auto-deleted after ~10 days, cleared on reboot.
- `/var/tmp`: retained up to ~30 days, survives reboots (used for persistent temp data).

---

## Next Steps
After environment enumeration, move to **permissions enumeration** (readable/writable dirs, scripts, binaries). Real-world assessments should still run **LinPEAS** for thoroughness, but manual enumeration builds deeper understanding and a reusable personal cheat sheet.