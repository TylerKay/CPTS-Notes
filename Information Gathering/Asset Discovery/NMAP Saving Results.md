# Saving the Results

---

## Different Formats
- Normal output (`-oN`) with the `.nmap` file extension
- Grepable output (`-oG`) with the `.gnmap` file extension
- XML output (`-oX`) with the `.xml` file extension

We can also specify the option (`-oA`) to save the results in all formats. The command could look like this:

`tylapcheong@htb[/htb]$ sudo nmap 10.129.2.28 -p- -oA target`

## Style sheets

With the XML output, we can easily create HTML reports that are easy to read, even for non-technical people. This is later very useful for documentation, as it presents our results in a detailed and clear way. To convert the stored results from XML format to HTML, we can use the tool `xsltproc`.

        shellsession
`tylapcheong@htb[/htb]$ xsltproc target.xml -o target.html`