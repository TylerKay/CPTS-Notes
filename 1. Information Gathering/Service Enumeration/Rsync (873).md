# Rsync (873)

---

## Overview

`Rsync` is a fast and efficient tool for **locally and remotely copying files**. Famous for its **delta-transfer algorithm**: when a version of the file already exists on the destination, it transmits **only the differences** between source files and the older destination copies — drastically reducing network traffic.

- Common uses: **backups and mirroring**.
- Detects files needing transfer by comparing **size or last modified time**.
- Default port **873**; can be configured to piggyback on an established SSH connection for secure transfers.

## Why Attackers Care

- Shared folders can often be **listed and read without authentication** (otherwise credentials are needed).
- Found credentials + Rsync = always test **password re-use** → may pull sensitive files that lead to remote access.

## Footprinting

#### Nmap

```
tylapcheong@htb[/htb]$ sudo nmap -sV -p 873 127.0.0.1

873/tcp open  rsync   (protocol version 31)
```

#### Probe for Accessible Shares (netcat)

```
tylapcheong@htb[/htb]$ nc -nv 127.0.0.1 873

(UNKNOWN) [127.0.0.1] 873 (rsync) open
@RSYNCD: 31.0
#list
dev             Dev Tools
@RSYNCD: EXIT
```

Sending `#list` after the handshake reveals exposed share names.

#### Enumerate an Open Share

```
tylapcheong@htb[/htb]$ rsync -av --list-only rsync://127.0.0.1/dev

drwxr-xr-x             48 2022/09/19 09:43:10 .
-rw-r--r--              0 2022/09/19 09:34:50 build.sh
-rw-r--r--              0 2022/09/19 09:36:02 secrets.yaml
drwx------             54 2022/09/19 09:43:10 .ssh
```

Watch for high-value targets like `secrets.yaml` or a readable `.ssh` directory (**SSH keys!**).

#### Download Everything

```
tylapcheong@htb[/htb]$ rsync -av rsync://127.0.0.1/dev
```

If Rsync is configured over SSH, add the `-e` flag:

```
rsync -av rsync://127.0.0.1/dev -e ssh
rsync -av rsync://127.0.0.1/dev -e "ssh -p2222"    # non-standard SSH port
```

## Workflow Cheat Sheet

1. Nmap `-p 873 -sV` → confirm rsync + protocol version
2. `nc -nv <IP> 873` → send `#list` to enumerate shares
3. `rsync -av --list-only rsync://<IP>/<share>` → inspect contents for secrets/keys
4. Sync the whole share locally with `rsync -av rsync://<IP>/<share>`
5. Try found credentials here too — re-use is common on internal hosts
