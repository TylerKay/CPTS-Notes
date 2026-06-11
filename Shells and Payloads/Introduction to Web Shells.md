It is almost guaranteed that we will come across web servers in our time learning and actively engaging in the practice of pentesting.

Furthermore, during external penetration tests, we often find that clients' perimeter networks are well-hardened. They do not expose vulnerable services such as SMB or other elements that we used to frequently encounter.

Web applications are often the majority of what we see exposed during an external network assessment and often present an enormous attack surface. We may find publicly available file upload forms that let us directly upload a PHP, JSP, or ASP.NET web shell.

## What is a Web Shell?

A `web shell` is a browser-based shell session we can use to interact with the underlying operating system of a web server. Again, to gain remote code execution via web shell, we must first find a website or web application vulnerability that can give us file upload capabilities. Most web shells are gained by uploading a payload written in a web language on the target server. The payload(s) we upload should give us remote code execution capability within the browser.

# Laudanum, One Webshell to Rule Them All

---

Laudanum is a repository of ready-made files that can be used to inject onto a victim and receive back access via a reverse shell, run commands on the victim host right from the browser, and more.
. The repo includes injectable files for many different web application languages to include `asp, aspx, jsp, php,` and more.

## Working with Laudanum

The Laudanum files can be found in the `/usr/share/laudanum` directory. For most of the files within Laudanum, you can copy them as-is and place them where you need them on the victim to run. For specific files such as the shells, you must edit the file first to insert your `attacking` host IP address to ensure you can access the web shell or receive a callback in the instance that you use a reverse shell. Before using the different files, be sure to read the contents and comments to ensure you take the proper actions.

. If you wish to follow along with this demonstration, you will need to add an entry into your `/etc/hosts` file on your attack VM or within Pwnbox for the host we are attacking. That entry should read: `<target ip> status.inlanefreight.local`.

#### Move a Copy for Modification
`tylapcheong@htb[/htb]$ cp /usr/share/laudanum/aspx/shell.aspx /home/tester/demo.aspx`

Add your IP address to the `allowedIps` variable on line `59`.

We are taking advantage of the upload function at the bottom of the status page(`Green Arrow`) for this to work.

Once the upload is successful, you will need to navigate to your web shell to utilize its functions.

We can now utilize the Laudanum shell we uploaded to issue commands to the host. We can see in the example that the `systeminfo` command was run.

![[laundanum_shell_success.png]]


# Antak Webshell

---

## ASPX and a Quick Learning Tip

Before diving into aspx shell concepts and exercises, we should take the time to cover a learning resource that can help reinforce most of the concepts covered here in HTB Academy.  One great resource to use in learning is `IPPSEC's` blog site [ippsec.rocks](https://ippsec.rocks/?#). The site is a powerful learning tool.

## ASPX Explained

`Active Server Page Extended` (`ASPX`) is a file type/extension written for [Microsoft's ASP.NET Framework](https://docs.microsoft.com/en-us/aspnet/overview). On a web server running the ASP.NET framework, web form pages can be generated for users to input data. On the server side, the information will be converted into HTML. We can take advantage of this by using an ASPX-based web shell to control the underlying Windows operating system. Let's witness this first-hand by utilizing the Antak Webshell.

## Antak Webshell

Antak is a web shell built in ASP.Net included within the [Nishang project](https://github.com/samratashok/nishang). Nishang is an Offensive PowerShell toolset that can provide options for any portion of your pentest. Since we are focused on web applications for the moment, let's keep our eyes on `Antak`. Antak utilizes PowerShell to interact with the host, making it great for acquiring a web shell on a Windows server.

## Working with Antak

The Antak files can be found in the `/usr/share/nishang/Antak-WebShell` directory.

`tylapcheong@htb[/htb]$ ls /usr/share/nishang/Antak-WebShell 
`antak.aspx  Readme.md`

 If you wish to follow along with this demonstration, you will need to add an entry into your `/etc/hosts` file on your attack VM or within Pwnbox for the host we are attacking. That entry should read: `<target ip> status.inlanefreight.local`

#### Move a Copy for Modification
`tylapcheong@htb[/htb]$ cp /usr/share/nishang/Antak-WebShell/antak.aspx /home/administrator/Upload.aspx`
#### Modify the Shell for Use
Make sure you set credentials for access to the web shell. Modify `line 14`, adding a user (green arrow) and password (orange arrow).

Now that we have access, we can utilize PowerShell commands to navigate and take actions against the host. We can issue basic commands from the Antak shell window, upload and download files, encode and execute scripts, and much more (green arrow below).

