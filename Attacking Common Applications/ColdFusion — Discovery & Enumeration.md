> ⚠️ Target VMs running ColdFusion may respond slowly (up to ~90s) — be patient before assuming a service is down.

---
## 1. What Is ColdFusion?

- Java-based programming language + web application development platform.
- Originally by **Allaire Corporation (1995)** → acquired by **Macromedia (2001)** → now owned/developed by **Adobe**.
- Builds dynamic, data-driven web apps; integrates with MySQL, Oracle, MS SQL Server, etc.
- Can be deployed on Windows, Mac, or Linux, and on cloud platforms (AWS, Azure).

### ColdFusion Markup Language (CFML)

- Proprietary tag-based language, HTML-like syntax — easy to learn.
- Tags simplify DB integration, web services, email, and other common tasks.

**Query example:**

```html
<cfquery name="myQuery" datasource="myDataSource">
  SELECT * FROM myTable
</cfquery>
```

**Iterate results:**

```html
<cfloop query="myQuery">
  <p>#myQuery.firstName# #myQuery.lastName#</p>
</cfloop>
```

- Supports embedding JavaScript/Java within CFML apps.
- Also supports email, PDF manipulation, graphing, AJAX serialization/deserialization.

### Key Benefits (for context/recon value)

|Benefit|Description|
|---|---|
|Rapid dev|Session management, form handling, debugging built in|
|DB integration|Native connectivity to Oracle/SQL Server/MySQL|
|Content management|Dynamic HTML gen, URL rewriting, file uploads|
|Performance|Optimized for low latency / high throughput|
|Collaboration|Code sharing, debugging, version control features|

### Version History

- Latest stable (at time of writing): **ColdFusion 2021**; **ColdFusion 2023** entering Alpha.
- Earlier versions: 2018, 2016, 11 — each with security/performance improvements.

---

## 2. Known Vulnerabilities (Historical)

|CVE|Description|
|---|---|
|**CVE-2013-0632**|Remote code execution|
|**CVE-2013-0629**|Directory traversal + sensitive file disclosure|
|**CVE-2010-2861**|Directory traversal + arbitrary file reading|
|**CVE-2018-15961**|Arbitrary file upload → RCE|
|**CVE-2023-26360**|Pre-authentication RCE|

> General weak points across ColdFusion's history: SQL injection, XSS, directory traversal, auth bypass, arbitrary file upload.

---

## 3. Default Ports

| Port     | Protocol       | Description                                                  |
| -------- | -------------- | ------------------------------------------------------------ |
| 80       | HTTP           | Standard non-secure web traffic                              |
| 443      | HTTPS          | Encrypted web traffic                                        |
| 1935     | RPC            | Remote Procedure Call, client-server comms                   |
| 25       | SMTP           | Outbound email                                               |
| **8500** | SSL            | **ColdFusion's own SSL service port — a strong fingerprint** |
| 5500     | Server Monitor | Remote admin of the ColdFusion server                        |
|          |                |                                                              |

> Ports can be changed during install/config — don't rely on defaults alone.

---

## 4. Enumeration Techniques

|Method|What to Look For|
|---|---|
|**Port scanning**|Ports 80/443 (generic) or **8500** (strong ColdFusion indicator)|
|**File extensions**|`.cfm` / `.cfc` pages|
|**HTTP headers**|`Server: ColdFusion` or `X-Powered-By: ColdFusion`|
|**Error messages**|References to ColdFusion-specific tags/functions|
|**Default files/paths**|`admin.cfm`, `CFIDE/administrator/index.cfm`|

---

## 5. Walkthrough Example
### Step 1 — Full Port Scan
```bash
nmap -p- -sC -Pn 10.129.247.30 --open
```

```
PORT      STATE SERVICE
135/tcp   open  msrpc
8500/tcp  open  fmtp
49154/tcp open  unknown
```

Port **8500** open → strong ColdFusion signal.
### Step 2 — Browse the Web Root
Navigating to `https://<IP>:8500/` reveals two directories:
```
CFIDE
cfdocs
```

Both are ColdFusion-standard directory names — confirms the platform.

### Step 3 — Explore `/CFIDE/`
Directory listing reveals files like:
```
Application.cfm
adminapi/
install.cfm
```

Triggering `Application.cfm` directly produces a ColdFusion-specific error page (**"Invalid request of Application.cfm"**) with debugging info referencing ColdFusion resources — another confirmation point.

### Step 4 — Check the Administrator Login
```
https://<IP>:8500/CFIDE/administrator
```

Loads the **ColdFusion 8 Administrator** login page — now the exact major version is confirmed (ColdFusion 8), which narrows down which CVEs/exploits are relevant.

---

## Summary

|Signal|Confirms|
|---|---|
|Port 8500 open|ColdFusion likely present (default SSL port)|
|`/CFIDE/`, `/cfdocs/` directories|ColdFusion install structure|
|`.cfm` / `.cfc` files, ColdFusion-specific error pages|Platform confirmed|
|`/CFIDE/administrator/` login page|Confirms exact major version (e.g., ColdFusion 8)|

## Key Takeaways

- **Port 8500** is the single strongest quick-win indicator during a scan.
- The `/CFIDE/administrator` path is gold — it often directly reveals the ColdFusion **major version** via its login page styling/banner, which tells you exactly which CVEs to pursue next.
- Error pages are chatty by default in older ColdFusion versions — don't overlook them during recon.
- Always check known CVEs against the confirmed version before attempting exploitation.