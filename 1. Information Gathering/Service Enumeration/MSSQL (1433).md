# MSSQL (1433)

---

## Overview

`Microsoft SQL` (`MSSQL`) is Microsoft's **closed-source** SQL-based relational database management system. Initially written for Windows only; versions exist for Linux/macOS, but we'll mostly encounter it on **Windows** targets.

- Popular with DBAs and developers building apps on Microsoft's **.NET framework** (strong native support).
- Interaction happens through **T-SQL** (`Transact-SQL`).

#### Clients

|**Client**|**Notes**|
|---|---|
|SQL Server Management Studio (**SSMS**)|Installs with MSSQL or standalone; used by admins for config/long-term management. Client-side app → can exist on *any* admin/developer workstation. A vulnerable system with SSMS may hold **saved credentials** we can reuse!|
|mssql-cli, SQL Server PowerShell, HeidiSQL, SQLPro|Alternative GUI/CLI clients|
|**Impacket `mssqlclient.py`**|Most useful for pentesting; ships with most pentesting distros|

```
tylapcheong@htb[/htb]$ locate mssqlclient
/usr/bin/impacket-mssqlclient
/usr/share/doc/python3-impacket/examples/mssqlclient.py
```

## Default System Databases

Understanding these helps map the structure of every database hosted on a target server:

|**Database**|**Description**|
|---|---|
|`master`|Tracks all system information for an SQL server instance|
|`model`|Template database — structure for every new DB created; changes here propagate to all databases created afterwards|
|`msdb`|Used by the SQL Server Agent to schedule jobs & alerts|
|`tempdb`|Stores temporary objects|
|`resource`|Read-only database containing system objects included with SQL server|

## Default Configuration

- When configured to be network-accessible, the service typically runs as **`NT SERVICE\MSSQLSERVER`**.
- Client connections default to **Windows Authentication**: the underlying Windows OS processes the login via the **local SAM database** or the **domain controller (Active Directory)**.
	- ✅ Ideal for auditing activity & access control in Windows environments
	- ❌ One compromised account → privilege escalation & lateral movement across the whole domain
- **Encryption is NOT enforced by default** on client connections.

## Dangerous Settings

Think like a busy IT admin — speed pressure makes mistakes easy, and one tiny misconfiguration can compromise a critical server:

- MSSQL clients **not using encryption** to connect
- Use of **self-signed certificates** when encryption is enabled → they can be **spoofed**
- Use of **named pipes**
- **Weak & default `sa` credentials** — admins may forget to disable the built-in `sa` account entirely

*(Not exhaustive — countless org-specific configurations exist.)*

## Footprinting the Service

Default port: **TCP 1433**.

#### Nmap Script Scan

```
tylapcheong@htb[/htb]$ sudo nmap --script ms-sql-info,ms-sql-empty-password,ms-sql-xp-cmdshell,ms-sql-config,ms-sql-ntlm-info,ms-sql-tables,ms-sql-hasdbaccess,ms-sql-dac,ms-sql-dump-hashes --script-args mssql.instance-port=1433,mssql.username=sa,mssql.password=,mssql.instance-name=MSSQLSERVER -sV -p 1433 10.129.201.248
```

What the output reveals (add to notes!):

|**Finding**|**Value from example**|
|---|---|
|Software version|Microsoft SQL Server **2019 RTM** (`15.00.2000.00`, no post-SP patches)|
|Instance name|`MSSQLSERVER`|
|Windows server name / hostname|`SQL-01`|
|TCP port|`1433`|
|Named pipe (enabled!)|`\\10.129.201.248\pipe\sql\query`|
|NTLM info|NetBIOS/DNS names, OS product version `10.0.17763`|
|DAC port|`1434` (via `ms-sql-dac`)|

#### Metasploit — mssql_ping

Cleaner alternative for quick footprinting:

```
msf6 auxiliary(scanner/mssql/mssql_ping) > set rhosts 10.129.201.248
msf6 auxiliary(scanner/mssql/mssql_ping) > run
```

Returns: `ServerName`, `InstanceName`, `IsClustered`, `Version`, `tcp` port, `np` (named pipe path) in one shot.

## Connecting with mssqlclient.py

With guessed/found credentials we connect remotely and interact with databases via T-SQL:

```
tylapcheong@htb[/htb]$ python3 mssqlclient.py Administrator@10.129.201.248 -windows-auth
```

Connection notes:
- `-windows-auth` → authenticates against Windows/AD instead of SQL logins
- Client auto-switches to **TLS** if the server requires encryption (`[*] Encryption required, switching to TLS`)
- First useful query once connected — lay of the land:

```
SQL> select name from sys.databases
```

Lists default DBs (`master`, `tempdb`, `model`, `msdb`) plus any user databases (e.g. `Transactions`).

## Workflow Cheat Sheet

1. Nmap `-p1433` with the `ms-sql-*` script battery (or Metasploit `mssql_ping`) → hostname, instance, version, named pipe, DAC port
2. Try weak/default `sa` credentials and empty passwords before moving on
3. Connect with `mssqlclient.py <user>@<IP> -windows-auth` (or SQL auth)
4. Enumerate `select name from sys.databases` → hunt non-default databases for sensitive tables
5. Remember the attack surface: spoofed self-signed certs, unencrypted client traffic, named pipes, and `xp_cmdshell` if we land elevated privileges
