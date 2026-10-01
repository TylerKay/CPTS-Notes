## Introduction to Virtual Hosting
Web servers (like Apache, Nginx, or IIS) use **virtual hosting** to host multiple websites or applications on a single server sharing one IP address. 

- **Subdomains vs. VHosts:** Subdomains are extensions of a main domain (e.g., `blog.example.com`) managed via DNS. Virtual hosts are server-level configurations allowing multiple sites/subdomains to be handled on the same server instance.
- **The HTTP Host Header:** Every HTTP browser request includes a `Host` header. The web server uses this header as a switch to dynamically serve the appropriate website files from its document root.

---

## Types of Virtual Hosting
1. **Name-Based Virtual Hosting:** Relies entirely on the HTTP `Host` header. Most common, cost-effective, and scalable (requires no extra IP addresses).
2. **IP-Based Virtual Hosting:** Assigns a unique IP address to each website hosted on the server. Offers better isolation but wastes IP addresses.
3. **Port-Based Virtual Hosting:** Differentiates sites based on different network ports (e.g., port `80` vs. `8080`) on the same IP.

---

## VHost Discovery & Fuzzing
Websites often host internal or hidden subdomains/VHosts that lack public DNS records. **VHost fuzzing** is the technique of testing various hostnames against a known target IP address using the `Host` header to uncover hidden sites.

- If a virtual host has no public DNS record, you can still access it manually by adding an entry to your local **hosts file** (`C:\\Windows\\System32\\drivers\\etc\\hosts` or `/etc/hosts`).

### Common VHost Discovery Tools

| Tool | Description & Features |
| :--- | :--- |
| **`gobuster`** | Multi-purpose tool; highly effective for VHost discovery using speed, custom headers, and wordlists. |
| **`feroxbuster`** | Fast, Rust-based fuzzer supporting recursion, wildcard filtering, and high performance. |
| **`ffuf`** | High-speed web fuzzer ideal for fuzzing the `Host` header with customizable inputs and filters. |

---

## Gobuster VHost Discovery Deep Dive
Gobuster can systematically send HTTP requests with different `Host` headers to an IP address to find valid virtual hosts.

### Basic Syntax (`gobuster vhost`):
```bash
gobuster vhost -u http://<target_IP> -w <wordlist_file> --append-domain