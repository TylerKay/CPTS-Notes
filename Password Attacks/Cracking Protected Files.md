The use of file encryption is often neglected in both `private` and `professional` contexts.  In many cases, `symmetric encryption` algorithms such as `AES-256` are used to securely store individual files or folders. In this method, the same key is used for both encryption and decryption. For transmitting files, `asymmetric encryption` is typically employed, which uses two distinct keys: the sender encrypts the file with the recipient's `public key`, and the recipient decrypts it using the corresponding `private key.


## Hunting for Encrypted Files

Many different extensions correspond to encrypted files—a useful reference list can be found on [FileInfo](https://fileinfo.com/filetypes/encoded). As an example, consider this command we might use to locate commonly encrypted files on a Linux system:

`tylapcheong@htb[/htb]$ for ext in $(echo ".xls .xls* .xltx .od* .doc .doc* .pdf .pot .pot* .pp*");do echo -e "\nFile extension: " $ext; find / -name *$ext 2>/dev/null | grep -v "lib\|fonts\|share\|core" ;done`

## Hunting for SSH keys

Certain files, such as SSH keys, do not have standard file extension. In cases like these, it may be possible to identify files by standard content such as header and footer values. For example, SSH private keys always begin with `-----BEGIN [...SNIP...] PRIVATE KEY-----`. We can use tools like `grep` to recursively search the file system for them during post-exploitation.

`tylapcheong@htb[/htb]$ grep -rnE '^\-{5}BEGIN [A-Z0-9]+ PRIVATE KEY\-{5}$' /* 2>/dev/null`

Some SSH keys are encrypted with a passphrase. With older PEM formats, it was possible to tell if an SSH key is encrypted based on the header, which contains the encryption method in use. Modern SSH keys, however, appear the same whether encrypted or not.

`tylapcheong@htb[/htb]$ cat /home/jsmith/.ssh/SSH.private 

-----BEGIN RSA PRIVATE KEY-----`


One way to tell whether an SSH key is encrypted or not, is to try reading the key with `ssh-keygen`.

`tylapcheong@htb[/htb]$ ssh-keygen -yf ~/.ssh/id_ed25519  ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIpNefJd834VkD5iq+22Zh59Gzmmtzo6rAffCx2UtaS6`

As shown below, attempting to read a password-protected SSH key will prompt the user for a passphrase:

`tylapcheong@htb[/htb]$ ssh-keygen -yf ~/.ssh/id_rsa Enter passphrase for "/home/jsmith/.ssh/id_rsa":`


## Cracking encrypted SSH keys

As mentioned in a previous section, JtR has many different scripts for extracting hashes from files—which we can then proceed to crack. We can find these scripts on our system using the following command:

`tylapcheong@htb[/htb]$ locate *2john*`


For example, we could use the Python script `ssh2john.py` to acquire the corresponding hash for an encrypted SSH key, and then use JtR to try and crack it.

`tylapcheong@htb[/htb]$ ssh2john.py SSH.private > ssh.hash tylapcheong@htb[/htb]$ john --wordlist=rockyou.txt ssh.hash`

We can then view the resulting hash:

`tylapcheong@htb[/htb]$ john ssh.hash --show SSH.private:1234 1 password hash cracked, 0 left`


## Cracking password-protected documents

Today, most reports, documentation, and information sheets are commonly distributed as Microsoft Office documents or PDFs. John the Ripper (JtR) includes a Python script called `office2john.py`, which can be used to extract password hashes from all common Office document formats. These hashes can then be supplied to JtR or Hashcat for offline cracking. The cracking procedure remains consistent with other hash types.
#### Cracking Office
`tylapcheong@htb[/htb]$ office2john.py Protected.docx > protected-docx.hash tylapcheong@htb[/htb]$ john --wordlist=rockyou.txt protected-docx.hash tylapcheong@htb[/htb]$ john protected-docx.hash --show`
#### Cracking PDFs
The process for cracking PDF files is quite similar, as we simply swap out `office2john.py` for `pdf2john.py`.

`tylapcheong@htb[/htb]$ pdf2john.py PDF.pdf > pdf.hash 
`tylapcheong@htb[/htb]$ john --wordlist=rockyou.txt pdf.hash 
`tylapcheong@htb[/htb]$ john pdf.hash --show`