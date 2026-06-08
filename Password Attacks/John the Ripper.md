[John the Ripper](https://github.com/openwall/john) (aka. `JtR` aka. `john`) is a well-known penetration testing tool used for cracking passwords through various attacks including brute-force and dictionary.

#### Single crack mode

`Single crack mode` is a rule-based cracking technique that is most useful when targeting Linux credentials. 
These strings are run against a large set of rules that apply common string modifications seen in passwords (e.g. a user whose real name is `Bob Smith` might use `Smith1` as their password).

tylapcheong@htb[/htb]$ john --single passwd

#### Wordlist mode

`Wordlist mode` is used to crack passwords with a dictionary attack, meaning it attempts all passwords in a supplied wordlist against the password hash. The basic syntax for the command is as follows:

`tylapcheong@htb[/htb]$ john --wordlist=<wordlist_file> <hash_file>`

#### Incremental mode

`Incremental mode` is a powerful, brute-force-style password cracking mode that generates candidate passwords based on a statistical model ([Markov chains](https://en.wikipedia.org/wiki/Markov_chain)).

The basic syntax is:
`tylapcheong@htb[/htb]$ john --incremental <hash_file>`

You can customize these or define your own to target passwords that use special characters or specific patterns.
`tylapcheong@htb[/htb]$ grep '# Incremental modes' -A 100 /etc/john/john.conf`

## Identifying hash formats

Sometimes, password hashes may appear in an unknown format, and even John the Ripper (JtR) may not be able to identify them with complete certainty. For example, consider the following hash:

One way to get an idea is to consult [JtR's sample hash documentation](https://openwall.info/wiki/john/sample-hashes), or [this list by PentestMonkey](https://pentestmonkey.net/cheat-sheet/john-the-ripper-hash-formats). Both sources list multiple example hashes as well as the corresponding JtR format. Another option is to use a tool like [hashID](https://github.com/psypanda/hashID), which checks supplied hashes against a built-in list to suggest potential formats. By adding the `-j` flag, hashID will, in addition to the hash format, list the corresponding JtR format:
`tylapcheong@htb[/htb]$ hashid -j 193069ceb0461e1d40d216e32c79c704`


JtR supports hundreds of hash formats, some of which are listed in the table below. The `--format` argument can be supplied to instruct JtR which format target hashes have.

| **Hash format** | **Example command**                     | **Description**                          |
| --------------- | --------------------------------------- | ---------------------------------------- |
| afs             | `john --format=afs [...] <hash_file>`   | AFS (Andrew File System) password hashes |
| bfegg           | `john --format=bfegg [...] <hash_file>` | bfegg hashes used in Eggdrop IRC bots    |
| bf              | `john --format=bf [...] <hash_file>`    | Blowfish-based crypt(3) hashes           |

There's more but just keeping it short and simple...Use --format

## Cracking files

It is also possible to crack password-protected or encrypted files with JtR. Multiple `"2john"` tools come with JtR that can be used to process files and produce hashes compatible with JtR. The generalized syntax for these tools is:

`tylapcheong@htb[/htb]$ <tool> <file_to_crack> > file.hash`

Some of the tools included with JtR are:

|**Tool**|**Description**|
|---|---|
|`pdf2john`|Converts PDF documents for John|
|`ssh2john`|Converts SSH private keys for John|
|`mscash2john`|Converts MS Cash hashes for John|
|`keychain2john`|Converts OS X keychain files for John|
|`rar2john`|Converts RAR archives for John|
|`pfx2john`|Converts PKCS#12 files for John|
|`truecrypt_volume2john`|Converts TrueCrypt volumes for John|
|`keepass2john`|Converts KeePass databases for John|
|`vncpcap2john`|Converts VNC PCAP files for John|
|`putty2john`|Converts PuTTY private keys for John|
|`zip2john`|Converts ZIP archives for John|
|`hccap2john`|Converts WPA/WPA2 handshake captures for John|
|`office2john`|Converts MS Office documents for John|
|`wpa2john`|Converts WPA/WPA2 handshakes for John|
An even larger collection can be found on the `Pwnbox`:
`tylapcheong@htb[/htb]$ locate *2john*`