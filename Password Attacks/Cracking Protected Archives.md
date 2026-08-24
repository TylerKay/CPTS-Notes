Besides standalone files, we will often run across `archives` and `compressed files`—such as ZIP files—which are protected with a password.

## Cracking ZIP files

The `ZIP` format is often heavily used in Windows environments to compress many files into one file. The process of cracking an encrypted ZIP file is similar to what we have seen already, except for using a different script to extract the hashes.

`
```
tylapcheong@htb[/htb]$ zip2john ZIP.zip > zip.hash
tylapcheong@htb[/htb]$ cat zip.hash 

ZIP.zip/customers.csv:$pkzip2$1*2*2*0*2a*1e*490e7510*0*42*0*2a*490e*409b*ef1e7feb7c1cf701a6ada7132e6a5c6c84c032401536faf7493df0294b0d5afc3464f14ec081cc0e18cb*$/pkzip2$:customers.csv:ZIP.zip::ZIP.zip
```

Once we have extracted the hash, we can use JtR to crack it with the desired password list.

```
tylapcheong@htb[/htb]$ john --wordlist=rockyou.txt zip.hash

Using default input encoding: UTF-8
Loaded 1 password hash (PKZIP [32/64])
Will run 2 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
1234             (ZIP.zip/customers.csv)
1g 0:00:00:00 DONE (2022-02-09 09:18) 100.0g/s 250600p/s 250600c/s 250600C/s 123456..1478963
Use the "--show" option to display all of the cracked passwords reliably
Session completed
tylapcheong@htb[/htb]$ john zip.hash --show

ZIP.zip/customers.csv:1234:customers.csv:ZIP.zip::ZIP.zip
```

## Cracking OpenSSL encrypted GZIP files

It is not always immediately apparent whether a file is password-protected, particularly when the file extension corresponds to a format that does not natively support password protection. As previously discussed, `openssl` can be used to encrypt files in the `GZIP` format. To determine the actual format of a file, we can use the `file` command, which provides detailed information about its contents. For example:

`tylapcheong@htb[/htb]$ file GZIP.gzip  GZIP.gzip: openssl enc'd data with salted password`

The following one-liner may produce several GZIP-related error messages, which can be safely ignored. If the correct password list is used, as in this example, we will see another file successfully extracted from the archive.

`tylapcheong@htb[/htb]$ for i in $(cat rockyou.txt);do openssl enc -aes-256-cbc -d -in GZIP.gzip -k $i 2>/dev/null| tar xz;done`

Once the `for` loop has finished, we can check the current directory for a newly extracted file.
`tylapcheong@htb[/htb]$ ls customers.csv  GZIP.gzip  rockyou.txt`

## Cracking BitLocker-encrypted drives

```
tylapcheong@htb[/htb]$ bitlocker2john -i Backup.vhd > backup.hashes tylapcheong@htb[/htb]$ grep "bitlocker\$0" backup.hashes > backup.hash tylapcheong@htb[/htb]$ cat backup.hash $bitlocker$0$16$02b329c0453b9273f2fc1b927443b5fe$1048576$12$00b0a67f961dd80103000000$60$d59f37e70696f7eab6b8f95ae93bd53f3f7067d5e33c0394b3d8e2d1fdb885cb86c1b978f6cc12ed26de0889cd2196b0510bbcd2a8c89187ba8ec54f
```

Once a hash is generated, either `JtR` or `hashcat` can be used to crack it. For this example, we will look at the procedure with `hashcat`. The hashcat mode associated with the `$bitlocker$0$...` hash is `-m 22100`. We supply the hash, specify the wordlist, and define the hash mode. Since this encryption uses strong AES encryption, cracking may take considerable time depending on hardware performance.

```
tylapcheong@htb[/htb]$ hashcat -a 0 -m 22100 

$bitlocker$0$16$02b329c0453b9273f2fc1b927443b5fe$1048576$12$00b0a67f961dd80103000000$60$d59f37e70696f7eab6b8f95ae93bd53f3f7067d5e33c0394b3d8e2d1fdb885cb86c1b978f6cc12ed26de0889cd2196b0510bbcd2a8c89187ba8ec54f' /usr/share/wordlists/rockyou.txt`
```

#### Mounting BitLocker-encrypted drives in Windows

The easiest method for mounting a BitLocker-encrypted virtual drive on Windows is to double-click the `.vhd` file. Since it is encrypted, Windows will initially show an error. After mounting, simply double-click the BitLocker volume to be prompted for the password.

#### Mounting BitLocker-encrypted drives in Linux (or macOS)

It is also possible to mount BitLocker-encrypted drives in Linux (or macOS). To do this, we can use a tool called [dislocker](https://github.com/Aorimn/dislocker). First, we need to install the package using `apt`:
`tylapcheong@htb[/htb]$ sudo apt-get install dislocker`

Next, we create two folders which we will use to mount the VHD.
`tylapcheong@htb[/htb]$ sudo mkdir -p /media/bitlocker tylapcheong@htb[/htb]$ sudo mkdir -p /media/bitlockermount`


We then use `losetup` to configure the VHD as [loop device](https://en.wikipedia.org/wiki/Loop_device), decrypt the drive using `dislocker`, and finally mount the decrypted volume:
```
tylapcheong@htb[/htb]$ sudo losetup -f -P Backup.vhd
tylapcheong@htb[/htb]$ sudo dislocker /dev/loop0p2 -u1234qwer -- /media/bitlocker
tylapcheong@htb[/htb]$ sudo mount -o loop /media/bitlocker/dislocker-file /media/bitlockermount
```

If everything was done correctly, we can now browse the files:
```
tylapcheong@htb[/htb]$ cd /media/bitlockermount/
tylapcheong@htb[/htb]$ ls -la
```

Once we have analyzed the files on the mounted drive, we can unmount it using the following commands:

```
tylapcheong@htb[/htb]$ sudo umount /media/bitlockermount
tylapcheong@htb[/htb]$ sudo umount /media/bitlocker
```