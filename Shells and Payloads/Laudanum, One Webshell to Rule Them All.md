Laudanum is a repository of ready-made files that can be used to inject onto a victim and receive back access via a reverse shell, run commands on the victim host right from the browser, and more.

The repo includes injectable files for many different web application languages to include `asp, aspx, jsp, php,` and more.

## Working with Laudanum

The Laudanum files can be found in the `/usr/share/laudanum` directory. For most of the files within Laudanum, you can copy them as-is and place them where you need them on the victim to run. For specific files such as the shells, you must edit the file first to insert your `attacking` host IP address to ensure you can access the web shell or receive a callback in the instance that you use a reverse shell. Before using the different files, be sure to read the contents and comments to ensure you take the proper actions.

#### Move a Copy for Modification
```
        shellsession
`tylapcheong@htb[/htb]$ cp /usr/share/laudanum/aspx/shell.aspx /home/tester/demo.aspx`
```
Once the upload is successful, you will need to navigate to your web shell to utilize its functions. The image below shows us how to do it. As seen from the last image, our shell was uploaded to the `\\files\` directory, and the name was kept the same.
