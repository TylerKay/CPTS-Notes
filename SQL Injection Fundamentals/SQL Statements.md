## INSERT Statement

The [INSERT](https://dev.mysql.com/doc/refman/8.0/en/insert.html) statement is used to add new records to a given table. The statement following the below syntax:

        sql
`INSERT INTO table_name VALUES (column1_value, column2_value, column3_value, ...);`

The example above shows how to add a new login to the logins table, with appropriate values for each column. However, we can skip filling columns with default values, such as `id` and `date_of_joining`. This can be done by specifying the column names to insert values into a table selectively:

        sql
`INSERT INTO table_name(column2, column3, ...) VALUES (column2_value, column3_value, ...);`

## SELECT Statement

```
SELECT column1, column2 FROM table_name;
```

## DROP Statement

We can use [DROP](https://dev.mysql.com/doc/refman/8.0/en/drop-table.html) to remove tables and databases from the server.

```
mysql> DROP TABLE logins;
```

## ALTER Statement

Finally, we can use ALTER to change the name of any table and any of its fields or to delete or add a new column to an existing table. The below example adds a new column newColumn to the logins table using ADD:

```
        shellsession
mysql> ALTER TABLE logins ADD newColumn INT;
```

To rename a column, we can use RENAME COLUMN:

```
        shellsession
mysql> ALTER TABLE logins RENAME COLUMN newColumn TO newerColumn;
```

We can also change a column's datatype with MODIFY:

```
        shellsession
mysql> ALTER TABLE logins MODIFY newerColumn DATE;

Query OK, 0 rows affected (0.01 sec)
```

## UPDATE Statement
While ALTER is used to change a table's properties, the UPDATE statement can be used to update specific records within a table, based on certain conditions. Its general syntax is:
```
        sql
UPDATE table_name SET column1=newvalue1, column2=newvalue2, ... WHERE <condition>;
```

We specify the table name, each column and its new value, and the condition for updating records. Let us look at an example:

        shellsession
`mysql> UPDATE logins SET password = 'change_password' WHERE id > 1;`