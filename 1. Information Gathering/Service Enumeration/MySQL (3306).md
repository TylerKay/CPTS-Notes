# MySQL (3306)

---

## Overview

`MySQL` is an **open-source SQL relational database management system** developed and supported by Oracle. Works on the **client-server principle**: a MySQL server (the actual DBMS — handles data storage and distribution) plus one or more clients that send structured queries to the database engine.

- Data is stored in **tables** with columns, rows, and data types; controlled via the SQL language.
- Databases are often exported/backed up as a single `.sql` file (e.g. `wordpress.sql`).
- Classic stack partner of dynamic websites: **LAMP** (Linux, Apache, MySQL, PHP) or **LEMP** (with Nginx) — the DB is the central store for content used by PHP scripts.
- Access may be internal-network only or public Internet. WordPress is a prime example: all posts, usernames, and passwords live in its DB (usually localhost-only).
- Passwords *can* sit in plain text, but PHP scripts normally one-way-encrypt them beforehand.
- **MariaDB** = fork of MySQL created by its chief developer after Oracle acquired MySQL AB.

Typical contents found in a web-hosting DB:

| | | | |
|---|---|---|---|
|Headers|Texts|Meta tags|Forms|
|Customers|Usernames|Administrators|Moderators|
|Email addresses|User information|Permissions|Passwords|
|External/Internal links|Links to Files|Specific contents|Values|

#### Why It Matters for Attacks

- The web app translates our input into executable code — **SQL injections** provoke error messages that leak information and confirm unintended DB interaction.
- Verbose errors shown on web apps can be manipulated toward making the MySQL server execute system commands (see SQL Injection Fundamentals / SQLMap Essentials modules).

## Default Configuration

```
tylapcheong@htb[/htb]$ sudo apt install mysql-server -y
tylapcheong@htb[/htb]$ cat /etc/mysql/mysql.conf.d/mysqld.cnf | grep -v "#" | sed -r '/^\s*$/d'
```

Key lines:

|**Setting**|**Value**|**Meaning**|
|---|---|---|
|`port`|`3306`|Default TCP port|
|`user`|`mysql`|Service runs as this user|
|`datadir`|`/var/lib/mysql`|Where databases are stored|
|`socket`|`/var/run/mysqld/mysqld.sock`|Local socket|

## Dangerous Settings

|**Setting**|**Description**|
|---|---|
|`user`|Which user the MySQL service runs as.|
|`password`|Password for the MySQL user.|
|`admin_address`|IP address to listen on for the administrative network interface.|
|`debug`|Current debugging settings.|
|`sql_warnings`|Whether single-row INSERT statements produce an info string when warnings occur.|
|`secure_file_priv`|Limits the effect of data import/export operations.|

> [!warning] Plaintext credentials in config
> `user`, `password`, and `admin_address` entries are made **in plain text**, and the config file's permissions are often set incorrectly. With any arbitrary file read (or shell), we get the MySQL username/password → full database access (customers, emails, passwords, personal data) unless other measures prevent it.

`debug` / `sql_warnings` produce verbose error output — useful to admins but a gift to attackers probing web apps via trial and error.

## Footprinting the Service

Usually runs on **TCP port 3306**. External exposure is rarely best practice — often leftover "temporary" settings or workarounds admins forgot about.

#### Nmap Scan

```
tylapcheong@htb[/htb]$ sudo nmap 10.129.14.128 -sV -sC -p3306 --script mysql*
```

What each script contributes:

|**Script**|**Reveals**|
|---|---|
|`mysql-info`|Protocol version (`10`), server version (`8.0.26...`), capability flags (e.g. `SupportsLoadDataLocal`, `SwitchToSSLAfterHandshake`, `SupportsCompression`), salt, auth plugin (`caching_sha2_password`)|
|`mysql-enum`|Valid usernames (root, netadmin, guest, user, web, sysadmin, administrator, webadmin, admin, test...)|
|`mysql-empty-password`|Accounts with no password|
|`mysql-brute`|Credential brute-force results/statistics|

> [!warning] Verify brute-force results manually!
> Nmap results can be false positives. In the example above, `mysql-empty-password` claims root has an empty password — but a direct connection attempt proves otherwise:
>
> ```
> tylapcheong@htb[/htb]$ mysql -u root -h 10.129.14.132
> ERROR 1045 (28000): Access denied for user 'root'@'10.129.14.1' (using password: NO)
> ```

#### Logging In & Enumerating

```
tylapcheong@htb[/htb]$ mysql -u root -pP4SSw0rd -h 10.129.14.128
```

Once in:

```
MySQL [(none)]> show databases;
MySQL [(none)]> select version();
MySQL [(none)]> use mysql;
MySQL [mysql]> show tables;
```

Two system databases matter most:

- **`sys`** (system schema) — tables/info/metadata necessary for management. E.g. `select host, unique_users from host_summary;` shows which hosts connect and how many users.
- **`information_schema`** — metadata database (ANSI/ISO standard requirement), largely derived from the system schema.

## Command Cheat Sheet

|**Command**|**Description**|
|---|---|
|`mysql -u <user> -p<password> -h <IP address>`|Connect to the MySQL server (**no space between `-p` and the password!**).|
|`show databases;`|Show all databases.|
|`use <database>;`|Select one of the existing databases.|
|`show tables;`|Show all available tables in the selected database.|
|`show columns from <table>;`|Show all columns in the selected table.|
|`select * from <table>;`|Show everything in the desired table.|
|`select * from <table> where <column> = "<string>";`|Search for needed string in the desired table.|

## Workflow Cheat Sheet

1. Nmap `-p3306 --script mysql*` → server version, capabilities, auth plugin, valid usernames
2. Manually verify any empty-password/brute-force hits (false positives are common)
3. Log in: `mysql -u <user> -p<pass> -h <IP>` → `show databases;` → hunt for non-default DBs (e.g. `wordpress`)
4. Dump sensitive tables: users, emails, password hashes (crack offline)
5. If we have file-read/shell elsewhere: check `/etc/mysql/mysql.conf.d/mysqld.cnf` for plaintext credentials
6. Note `secure_file_priv` value — it constrains `LOAD DATA`/`INTO OUTFILE` abuse paths
