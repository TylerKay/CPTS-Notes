# Linux Authentication Process

> ⚠️ Requires root/admin access to read `/etc/shadow` and `/etc/security/opasswd` — treat cracked credentials with the same care as any other post-exploitation loot.

---

## 1. PAM (Pluggable Authentication Modules)

- Linux distros commonly authenticate via **PAM**.
- Key module: `pam_unix.so` (or `pam_unix2.so`) — typically at `/usr/lib/x86_64-linux-gnu/security/` on Debian-based systems.
- Manages user info, authentication, sessions, and password changes (e.g., invoked automatically by `passwd`).
- Uses standardized system library calls to read/write `/etc/passwd` and `/etc/shadow`.
- PAM also has modules for LDAP, mount operations, Kerberos auth, etc.

---
## 2. `/etc/passwd`
- World-readable; contains one entry per user, 7 colon-separated fields.
```bash
htb-student:x:1000:1000:,,,:/home/htb-student:/bin/bash
```

|Field|Value|
|---|---|
|Username|`htb-student`|
|Password|`x`|
|User ID|`1000`|
|Group ID|`1000`|
|GECOS|`,,,`|
|Home directory|`/home/htb-student`|
|Default shell|`/bin/bash`|

- **Password field = `x`** → hash actually lives in `/etc/shadow` (normal, modern setup).
- On very old systems, the hash itself may be stored directly in this field (world-readable → crackable).

### Misconfiguration: Empty Password Field

If `/etc/passwd` is writable and the password field for root is blanked:

```bash
head -n 1 /etc/passwd
```

```
root::0:0:root:/root:/bin/bash
```

Result: **no password prompt** when elevating:

```bash
su
```

```
root@htb[/htb]#
```

> Rare, but can happen if an admin unfamiliar with Linux grants overly broad write permissions to `/etc` for an application and never corrects it.

---

## 3. `/etc/shadow`
- Introduced to stop world-readable password hash exposure.
- Only readable by privileged users.
- 9 colon-separated fields:
```
htb-student:$y$j9T$3QSBB6CbHEu...SNIP...f8Ms:18955:0:99999:7:::
```

|Field|Value|
|---|---|
|Username|`htb-student`|
|Password (hash)|`$y$j9T$3QSBB6CbHEu...f8Ms`|
|Last change|`18955`|
|Min age|`0`|
|Max age|`99999`|
|Warning period|`7`|
|Inactivity period|—|
|Expiration date|—|
|Reserved|—|

- **No `/etc/shadow` entry** for a user listed in `/etc/passwd` → user is considered invalid.
- **`!` or `*` in password field** → Unix password login disabled, but other methods (Kerberos, key-based auth) may still work.
- **Empty password field** → no password required to log in (may still be blocked by some programs/policies).

### Hash Format

```
$<id>$<salt>$<hashed>
```

|ID|Algorithm|
|---|---|
|`1`|MD5|
|`2a`|Blowfish|
|`5`|SHA-256|
|`6`|SHA-512|
|`sha1`|SHA1crypt|
|`y`|Yescrypt|
|`gy`|Gost-yescrypt|
|`7`|Scrypt|

> Many modern distros (Debian included) default to **yescrypt**. Older systems may still use weaker algorithms (MD5, SHA-256/512) — worth checking, since MD5 is far easier to crack.

---

## 4. `/etc/security/opasswd`

- Stores **previous password hashes** so `pam_unix.so` can enforce password-reuse restrictions.
- Requires root to read (unless permissions were manually loosened).

```bash
sudo cat /etc/security/opasswd
```

```
cry0l1t3:1000:2:$1$HjFAfYTG$qNDkF0zJ3v8ylCOrKB0kt0,$1$kcUjWZJX$E9uMSmiQeRh4pAAgzuvkq1
```

- Multiple historical hashes per user, comma-separated.
- **Check the hash type carefully** — old MD5 (`$1$`) hashes are much easier to crack than SHA-512, and cracked _old_ passwords often reveal reuse patterns useful for guessing _current_ passwords.

---

## 5. Cracking Linux Credentials

### Step 1 — Back Up passwd/shadow

```bash
sudo cp /etc/passwd /tmp/passwd.bak
sudo cp /etc/shadow /tmp/shadow.bak
```

### Step 2 — Combine with `unshadow` (John the Ripper toolset)

```bash
unshadow /tmp/passwd.bak /tmp/shadow.bak > /tmp/unshadowed.hashes
```

### Step 3 — Crack with Hashcat

```bash
hashcat -m 1800 -a 0 /tmp/unshadowed.hashes rockyou.txt -o /tmp/unshadowed.cracked
```

> `-m 1800` = sha512crypt mode; adjust hash mode to match the algorithm ID found in `/etc/shadow`.

> 💡 This exact scenario (combined passwd+shadow file) is what John the Ripper's **single crack mode** was purpose-built for.

---

## Summary

|File|Readable By|Contains|
|---|---|---|
|`/etc/passwd`|Everyone|Username, UID/GID, shell, home dir; password field usually just `x`|
|`/etc/shadow`|Root/privileged only|Actual password hashes + aging policy|
|`/etc/security/opasswd`|Root/privileged only|Historical password hashes (reuse prevention)|

## Key Takeaways

- A writable `/etc/passwd` can let you blank the root password field entirely for instant root.
- Hash algorithm ID (`$1$`, `$5$`, `$6$`, `$y$`, etc.) tells you how hard the hash will be to crack — prioritize weaker (MD5) hashes first.
- `/etc/security/opasswd` can reveal old, weaker, or pattern-following passwords useful for guessing current ones.
- Standard workflow: `unshadow` → `hashcat`/`john` → crack offline.

## Further Reading

- The Linux Documentation Project — Linux authentication process