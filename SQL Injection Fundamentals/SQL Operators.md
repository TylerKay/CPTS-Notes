
## AND Operator

The `AND` operator takes in two conditions and returns `true` or `false` based on their evaluation:

        sql
`condition1 AND condition2`

The result of the `AND` operation is `true` if and only if both `condition1` and `condition2` evaluate to `true`:

        shellsession
`mysql> SELECT 1 = 1 AND 'test' = 'test';`

## OR Operator

The `OR` operator takes in two expressions as well, and returns `true` when at least one of them evaluates to `true`:

        shellsession
`mysql> SELECT 1 = 1 OR 'test' = 'abc';`


## NOT Operator

The `NOT` operator simply toggles a `boolean` value 'i.e. `true` is converted to `false` and vice versa':

        shellsession
`mysql> SELECT NOT 1 = 1;`

## Symbol Operators

The `AND`, `OR` and `NOT` operators can also be represented as `&&`, `||` and `!`, respectively. The below are the same previous examples, by using the symbol operators:

        shellsession
`mysql> SELECT 1 = 1 && 'test' = 'abc';`

mysql> SELECT 1 = 1 || 'test' = 'abc';

mysql> SELECT 1 != 1;

## Operators in queries

Let us look at how these operators can be used in queries. The following query lists all records where the `username` is NOT `john`:

        shellsession
`mysql> SELECT * FROM logins WHERE username != 'john';`\

The next query selects users who have their `id` greater than `1` AND `username` NOT equal to `john`:

        shellsession
`mysql> SELECT * FROM logins WHERE username != 'john' AND id > 1;`


## Multiple Operator Precedence

SQL supports various other operations such as addition, division as well as bitwise operations. Thus, a query could have multiple expressions with multiple operations at once. The order of these operations is decided through operator precedence.

Here is a list of common operations and their precedence, as seen in the [MariaDB Documentation](https://mariadb.com/kb/en/operator-precedence/):

- Division (`/`), Multiplication (`*`), and Modulus (`%`)
- Addition (`+`) and subtraction (`-`)
- Comparison (`=`, `>`, `<`, `<=`, `>=`, `!=`, `LIKE`)
- NOT (`!`)
- AND (`&&`)
- OR (`||`)
- 
Operations at the top are evaluated before the ones at the bottom of the list. Let us look at an example:

        sql
`SELECT * FROM logins WHERE username != 'tom' AND id > 3 - 2;`

Next, we have two comparison operations, `>` and `!=`. Both of these are of the same precedence and will be evaluated together