## What is an Injection?

In the above example, we accept user input and pass it directly to the SQL query without sanitization.

Sanitization refers to the removal of any special characters in user-input, in order to break any injection attempts.

Injection occurs when an application misinterprets user input as actual code rather than a string, changing the code flow and executing it. This can occur by escaping user-input bounds by injecting a special character like (`'`), and then writing code to be executed, like JavaScript code or SQL in SQL Injections. Unless the user input is sanitized, it is very likely to execute the injected code and run it.

```
$searchInput = $_POST['findUser'];
$query = "select * from logins where username like '%$searchInput'";
$result = $conn->query($query);

```

In typical cases, the `searchInput` would be inputted to complete the query, returning the expected outcome. Any input we type goes into the following SQL query:

        sql
`select * from logins where username like '%$searchInput'`

However, as there is no sanitization, in this case, **we can add a single quote (`'`), which will end the user-input field, and after it, we can write actual SQL code**. For example, if we search for `1'; DROP TABLE users;`, the search input would be:

        php
`'%1'; DROP TABLE users;'`

Notice how we added a single quote (') after "1", in order to escape the bounds of the user-input in ('%$searchInput').

So, the final SQL query executed would be as follows:

        sql
`select * from logins where username like '%1'; DROP TABLE users;'`

## Syntax Errors

The previous example of SQL injection would return an error:

        php
`Error: near line 1: near "'": syntax error`

This is because of the last trailing character, where we have a single extra quote (`'`) that is not closed, which causes a SQL syntax error when executed:

        sql
```
select * from logins where username like '%1'; DROP TABLE users;'
```

## Types of SQL Injections

SQL Injections are categorized based on how and where we retrieve their output.![[Types_of_SQL_Injection.png]]
In simple cases, the output of both the intended and the new query may be printed directly on the front end, and we can directly read it. This is known as `In-band` SQL injection, and it has two types: `Union Based` and `Error Based`.

With `Union Based` SQL injection, we may have to specify the exact location, 'i.e., column', which we can read, so the query will direct the output to be printed there. As for `Error Based` SQL injection, it is used when we can get the `PHP` or `SQL` errors in the front-end, and so we may intentionally cause an SQL error that returns the output of our query.

In more complicated cases, we may not get the output printed, so we may utilize SQL logic to retrieve the output character by character. This is known as `Blind` SQL injection, and it also has two types: `Boolean Based` and `Time Based`.

With `Boolean Based` SQL injection, we can use SQL conditional statements to control whether the page returns any output at all, 'i.e., original query response,' if our conditional statement returns `true`. As for `Time Based` SQL injections, we use SQL conditional statements that delay the page response if the conditional statement returns `true` using the `Sleep()` function.

Finally, in some cases, we may not have direct access to the output whatsoever, so we may have to direct the output to a remote location, 'i.e., DNS record,' and then attempt to retrieve it from there. This is known as `Out-of-band` SQL injection.

## SQLi Discovery

Before we start subverting the web application's logic and attempting to bypass the authentication, we first have to test whether the login form is vulnerable to SQL injection. To do that, we will try to add one of the below payloads after our username and see if it causes any errors or changes how the page behaves:

|Payload|URL Encoded|
|---|---|
|`'`|`%27`|
|`"`|`%22`|
|`#`|`%23`|
|`;`|`%3B`|
|`)`|`%29`|
We would need the query always to return `true`, regardless of the username and password entered, to bypass the authentication. To do this, we can abuse the `OR` operator in our SQL injection.

An example of a condition that will always return `true` is `'1'='1'`. However, to keep the SQL query working and keep an even number of quotes, instead of using ('1'='1'), we will remove the last quote and use ('1'='1), so the remaining single quote from the original query would be in its place.

So, if we inject the below condition and have an `OR` operator between it and the original condition, it should always return `true`:

        sql
```
admin' or '1'='1
```

The final query should be as follow:

```
SELECT * FROM logins WHERE username='admin' or '1'='1' AND password = 'something';
```

To successfully log in once again, we will need an overall `true` query. This can be achieved by injecting an `OR` condition into the password field, so it will always return `true`. Let us try `something' or '1'='1` as the password.