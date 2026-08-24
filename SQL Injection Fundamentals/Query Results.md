## Sorting Results

We can sort the results of any query using [ORDER BY](https://dev.mysql.com/doc/refman/8.0/en/order-by-optimization.html) and specifying the column to sort by:

```
        shellsession
mysql> SELECT * FROM logins ORDER BY password;
```

By default, the sort is done in ascending order, but we can also sort the results by ASC or DESC:

        shellsession
```
mysql> SELECT * FROM logins ORDER BY password DESC;
```

It is also possible to sort by multiple columns, to have a secondary sort for duplicate values in one column:

        shellsession
```
mysql> SELECT * FROM logins ORDER BY password DESC, id ASC;
```

## LIMIT results
In case our query returns a large number of records, we can LIMIT the results to what we want only, using LIMIT and the number of records we want:
```
mysql> SELECT * FROM logins LIMIT 2;
```

If we wanted to LIMIT results with an offset, we could specify the offset before the LIMIT count:

        shellsession
mysql> SELECT * FROM logins LIMIT 1, 2;

## WHERE Clause

To filter or search for specific data, we can use conditions with the `SELECT` statement using the [WHERE](https://dev.mysql.com/doc/refman/8.0/en/where-optimization.html) clause, to fine-tune the results:
```
        sql
SELECT * FROM table_name WHERE <condition>;
```

The query above will return all records which satisfy the given condition. Let us look at an example:

```
        shellsession
mysql> SELECT * FROM logins WHERE id > 1;
```

The example above selects all records where the value of `id` is greater than `1`. As we can see, the first row with its `id` as 1 was skipped from the output. We can do something similar for usernames:

```
        shellsession
mysql> SELECT * FROM logins where username = 'admin';
```
The query above selects the record where the username is `admin`. We can use the `UPDATE` statement to update certain records that meet a specific condition.

## LIKE Clause

Another useful SQL clause is [LIKE](https://dev.mysql.com/doc/refman/8.0/en/pattern-matching.html), enabling selecting records by matching a certain pattern. The query below retrieves all records with usernames starting with `admin`:

        shellsession
`mysql> SELECT * FROM logins WHERE username LIKE 'admin%';`

The `%` symbol acts as a wildcard and matches all characters after `admin`. It is used to match zero or more characters. Similarly, the `_` symbol is used to match exactly one character. The below query matches all usernames with exactly three characters in them, which in this case was `tom`:
```
        shellsession
mysql> SELECT * FROM logins WHERE username like '___';
```

