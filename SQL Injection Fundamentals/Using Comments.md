In this section we will learn how to use comments to subvert the logic of more advanced SQL queries and end up with a working SQL query to bypass the login authentication process.

We can use two types of line comments with MySQL `--` and `#`, in addition to an in-line comment `/**/` (although this is not typically used in basic sql injections). The `--` can be used as follows:

```
mysql> SELECT username FROM logins; -- Selects usernames from the logins table
```

The `#` symbol can be used as well.

```
        shellsession
mysql> SELECT * FROM logins WHERE username = 'admin'; # You can place anything here AND password = 'something'
```

The server will ignore the part of the query with `AND password = 'something'` during evaluation.

---

## Auth Bypass with comments

Let us go back to our previous example and inject `admin'--` as our username. The final query will be:

```
SELECT * FROM logins WHERE username='admin'-- ' AND password = 'something';
```

