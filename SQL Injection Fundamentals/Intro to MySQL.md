The `mysql` utility is used to authenticate to and interact with a MySQL/MariaDB database. The `-u` flag is used to supply the username and the `-p` flag for the password.

```
tylapcheong@htb[/htb]$ mysql -u root -p
```

Again, it is also possible to use the password directly in the command, though this should be avoided, as it could lead to the password being kept in logs and terminal history:
```
tylapcheong@htb[/htb]$ mysql -u root -p<password>
```

Tip: There shouldn't be any spaces between '-p' and the password.


When we do not specify a host, it will default to the `localhost` server. We can specify a remote host and port using the `-h` and `-P` flags.

`tylapcheong@htb[/htb]$ mysql -u root -h docker.hackthebox.eu -P 3306 -p`

## Creating a database

Once we log in to the database using the `mysql` utility, we can start using SQL queries to interact with the DBMS. For example, a new database can be created within the MySQL DBMS using the [CREATE DATABASE](https://dev.mysql.com/doc/refman/5.7/en/create-database.html) statement.

```
mysql> CREATE DATABASE users;
```

MySQL expects command-line queries to be terminated with a semi-colon. The example above created a new database named `users`. We can view the list of databases with [SHOW DATABASES](https://dev.mysql.com/doc/refman/8.0/en/show-databases.html), and we can switch to the `users` database with the `USE` statement:

```
mysql> SHOW DATABASES;

mysql> USE users;
```

## Tables

DBMS stores data in the form of tables. A table is made up of horizontal rows and vertical columns.
```
CREATE TABLE logins (
    id INT,
    username VARCHAR(100),
    password VARCHAR(100),
    date_of_joining DATETIME
    );
```

```
mysql> SHOW TABLES;
```

```
mysql> DESCRIBE logins;

+-----------------+--------------+
| Field           | Type         |
+-----------------+--------------+
| id              | int          |
| username        | varchar(100) |
| password        | varchar(100) |
| date_of_joining | date         |
+-----------------+--------------+
4 rows in set (0.00 sec)
```

