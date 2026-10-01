> ⚠️ LDAP injection can bypass authentication entirely — treat any web app backed by LDAP auth as a high-value target for this class of attack.

---

## 1. What Is LDAP?

**LDAP (Lightweight Directory Access Protocol)** — protocol for accessing/managing directory information (hierarchical store of users, groups, computers, printers, devices, etc.).
### Strengths

|Feature|Description|
|---|---|
|Efficient|Fast queries via lean query language, non-normalized storage|
|Global naming model|Supports multiple independent directories with unique entries|
|Extensible|Custom attributes/schemas for local requirements|
|Compatible|Runs over TCP/IP + SSL, platform-independent|
|Authentication|Enables single sign-on across multiple resources|

### Weaknesses

|Issue|Description|
|---|---|
|Compliance|Requires LDAP-compliant directory servers — limits vendor choice|
|Complexity|Easy to misconfigure; many devs/admins don't fully understand it|
|No encryption by default|Traffic is plaintext unless **LDAPS** or **StartTLS** is used|
|Injection|Vulnerable to LDAP injection without proper input validation|

### Common Use Cases

- **Authentication** — single login across multiple apps/systems (most common use case)
- **Authorization** — permissions/access control for network resources (often paired with Kerberos)
- **Directory Services** — search/retrieve/modify large-scale user/device data (based on X.500 standard)
- **Synchronization** — replicating directory changes across systems

### Implementations

- **OpenLDAP** — open-source, widely supported
- **Microsoft Active Directory** — Windows-based, deeply integrated with the MS ecosystem

---

## 2. LDAP vs. Active Directory

|LDAP|Active Directory (AD)|
|---|---|
|A **protocol** for accessing/modifying directory data|A **directory service** that stores/manages user & computer data|
|Open, cross-platform|Proprietary, Windows-only; needs DNS + Kerberos|
|Flexible/extensible schema|Predefined schema (extends X.500); modify with care|
|Multiple auth mechanisms (simple bind, SASL, etc.)|Primarily Kerberos; also NTLM, LDAP over SSL/TLS|

> AD **uses** LDAP as one of its protocols — LDAP itself is not a directory service.

---

## 3. How LDAP Works

Client-server model, ASN.1-encoded messages over TCP/IP. Supported operations: **bind, unbind, search, compare, add, delete, modify**.

### Request Components

- **Session connection** — client connects via LDAP port (389 default, 636 for LDAPS)
- **Request type** — bind, search, etc.
- **Request parameters** — DN, search scope/filter, attributes/values
- **Request ID** — unique identifier to match the response

### Response Components

- **Response type** — operation performed
- **Result code** — success/failure + reason
- **Matched DN** — closest matching existing entry (if applicable)
- **Referral** — pointer to another server with more info
- **Response data** — actual attributes/values returned

---

## 4. `ldapsearch` — Querying LDAP

```bash
ldapsearch -H ldap://ldap.example.com:389 \
  -D "cn=admin,dc=example,dc=com" -w secret123 \
  -b "ou=people,dc=example,dc=com" "(mail=john.doe@example.com)"
```

**Breakdown:**

- `-H` → server + port
- `-D` / `-w` → bind DN + password (authenticate)
- `-b` → base DN to search under
- Filter `(mail=...)` → match entries with that email

**Example response:**

```
dn: uid=jdoe,ou=people,dc=example,dc=com
objectClass: inetOrgPerson
cn: John Doe
uid: jdoe
mail: john.doe@example.com

result: 0 Success
```

---

## 5. LDAP Injection

### What It Is

Similar concept to SQL injection, but targets LDAP queries instead of SQL. Attacker injects special characters/operators to alter query logic, bypass auth, or extract data.

### Key Injection Characters

|Char|Function|
|---|---|
|`*`|Wildcard — matches any number of characters|
|`( )`|Groups expressions|
|`\|`|Logical OR|
|`&`|Logical AND|
|`(cn=*)` / `(objectClass=*)`|Always-true conditions — classic auth bypass payloads|

### Example Vulnerable Query

```
(&(objectClass=user)(sAMAccountName=$username)(userPassword=$password))
```

### Bypass via Wildcard in Username

```php
$username = "*";
$password = "dummy";
```

```
(&(objectClass=user)(sAMAccountName=*)(userPassword=dummy))
```

→ Matches **any** account whose password happens to be `dummy`.

### Bypass via Wildcard in Password

```php
$username = "dummy";
$password = "*";
```

```
(&(objectClass=user)(sAMAccountName=dummy)(userPassword=*))
```

→ Matches the `dummy` account regardless of the actual password.

### Impact

- Unauthorized access / full auth bypass
- Privilege escalation
- Full application/server compromise
- Data integrity/availability impact (attacker can alter/remove directory entries)

### Mitigations

- Validate and sanitize all user input before building LDAP queries.
- Strip/escape LDAP-specific special characters (`*`, `(`, `)`, `\`, `NUL`, etc.).
- Use **parameterized queries** so input is always treated as data, never as query syntax.

---

## 6. Enumeration & Practical Example

### Step 1 — Nmap Service Scan

```bash
nmap -p- -sC -sV --open --min-rate=1000 10.129.204.229
```

```
PORT    STATE SERVICE VERSION
80/tcp  open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-title: Login
389/tcp open  ldap    OpenLDAP 2.2.X - 2.3.X
```

> Port 80 (login page) + Port 389 (OpenLDAP) together strongly suggest the web app authenticates users **against the LDAP backend**.

### Step 2 — Test for Injection

On the login form, submit `*` in **both** the username and password fields.

**Result:** Authentication bypassed — full access granted with no valid credentials, confirming the backend LDAP query has no input sanitization.

---

## Summary

|Concept|Key Point|
|---|---|
|Default LDAP port|389 (unencrypted); 636 for LDAPS|
|No default encryption|Use LDAPS or StartTLS to protect traffic|
|Injection root cause|Unsanitized input concatenated directly into LDAP filter syntax|
|Classic bypass payload|`*` in username and/or password field|
|Real-world signal|Web login page (port 80) + OpenLDAP (port 389) on the same host|

## Key Takeaways

- Any web app authenticating against an LDAP backend should be tested with `*` in both credential fields as a first, trivial check for injection.
- LDAP injection payloads are conceptually identical to SQLi payloads — think "always-true conditions" (`(cn=*)`, `(objectClass=*)`) rather than SQL-specific syntax.
- Confirming OpenLDAP/AD on port 389/636 alongside a login form is a strong signal to test for this class of vulnerability before anything else.
- Mitigation is the same principle as SQLi: sanitize input, use parameterized queries, never trust user-supplied data in the query string itself.