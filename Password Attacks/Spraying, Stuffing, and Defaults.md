## Password spraying

[Password spraying](https://owasp.org/www-community/attacks/Password_Spraying_Attack) is a type of brute-force attack in which an attacker attempts to use a single password across many different user accounts.

Depending on the target system, different tools may be used to carry out password spraying attacks. For web applications, [Burp Suite](https://portswigger.net/burp) is a strong option, while for Active Directory environments, tools such as [NetExec](https://github.com/Pennyw0rth/NetExec) or [Kerbrute](https://github.com/ropnop/kerbrute) are commonly used.

```
tylapcheong@htb[/htb]$ netexec smb 10.100.38.0/24 -u <usernames.list> -p 'ChangeMe123!'

```

## Credential stuffing

[Credential stuffing](https://owasp.org/www-community/attacks/Credential_stuffing) is another type of brute-force attack in which an attacker uses stolen credentials from one service to attempt access on others.

For example, if we have a list of `username:password` credentials obtained from a database leak, we can use `hydra` to perform a credential stuffing attack against an SSH service using the following syntax:

```
tylapcheong@htb[/htb]$ hydra -C user_pass.list ssh://10.100.38.23
```

## Default credentials

Many systems—such as routers, firewalls, and databases—come with `default credentials`.

`tylapcheong@htb[/htb]$ pip3 install defaultcreds-cheat-sheet`

Once installed, we can use the `creds` command to search for known default credentials associated with a specific product or vendor.

```
tylapcheong@htb[/htb]$ creds search linksys
```