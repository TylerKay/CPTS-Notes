```
IP=10.129.42.195
tylapcheong@htb[/htb]$ printf "%s\t%s\n\n" "$IP" "app.inlanefreight.local dev.inlanefreight.local blog.inlanefreight.local" | sudo tee -a /etc/hosts
```

Output in /etc/hosts:
```
10.129.42.195 app.inlanefreight.local dev.inlanefreight.local blog.inlanefreight.local
```

```
printf "%s\t%s\n\n" "10.129.42.195" app.inlanefreight.local dev.inlanefreight.local drupal-dev.inlanefreight.local drupal-qa.inlanefreight.local drupal-acc.inlanefreight.local drupal.inlanefreight.local blog.inlanefreight.local | sudo tee -a /etc/hosts
```


Two phenomenal tools that every tester should have in their arsenal are [EyeWitness](https://github.com/FortyNorthSecurity/EyeWitness) and [Aquatone](https://github.com/michenriksen/aquatone). Both of these tools can be fed raw Nmap XML scan output (Aquatone can also take Masscan XML; EyeWitness can take Nessus XML output) and be used to quickly inspect all hosts running web applications and take screenshots of each. The screenshots are then assembled into a report that we can work through in the web browser to assess the web attack surface.

An example OneNote (also applicable to other tools) structure may look like the following for the discovery phase:

`External Penetration Test - <Client Name>`

- `Scope` (including in-scope IP addresses/ranges, URLs, any fragile hosts, testing timeframes, and any limitations or other relative information we need handy)
- `Client Points of Contact`
- `Credentials`
- `Discovery/Enumeration`
    - `Scans`
    - `Live hosts`
- `Application Discovery`
    - `Scans`
    - `Interesting/Notable Hosts`
- `Exploitation`
    - `<Hostname or IP>`
    - `<Hostname or IP>`
- `Post-Exploitation`
    - `<Hostname or IP>`
    - `<Hostname or IP>`

## Initial Enumeration

Let's assume our client provided us with the following scope:
```
tylapcheong@htb[/htb]$ cat scope_list 

app.inlanefreight.local
dev.inlanefreight.local
drupal-dev.inlanefreight.local
drupal-qa.inlanefreight.local
drupal-acc.inlanefreight.local
...

```

We can start with an Nmap scan of common web ports. I'll typically do an initial scan with ports `80,443,8000,8080,8180,8888,10000` and then run either EyeWitness or Aquatone (or both depending on the results of the first) against this initial scan. While reviewing the screenshot report of the most common ports, I may run a more thorough Nmap scan against the top 10,000 ports or all TCP ports, depending on the size of the scope. Since enumeration is an iterative process, we will run a web screenshotting tool against any subsequent Nmap scans we perform to ensure maximum coverage.

On a non-evasive full scope penetration test, I will usually run a Nessus scan too to give the client the most bang for their buck, but we must be able to perform assessments without relying on scanning tools.

All scans we perform during a non-evasive engagement are to gather data as inputs to our manual validation and manual testing process. We should not rely solely on scanners as the human element in penetration testing is essential. We often find the most unique and severe vulnerabilities and misconfigurations only through thorough manual testing.

 In this lab, we are utilizing Vhosts to simulate the subdomains of a company. Hosts with `dev` as part of the FQDN are worth noting down as they may be running untested features or have things like debug mode enabled. Sometimes the hostnames won't tell us too much, such as `app.inlanefreight.local`. We can infer that it is an application server but would need to perform further enumeration to identify which application(s) are running on it.

```
sudo  nmap -p 80,443,8000,8080,8180,8888,10000 --open -oA web_discovery -iL scope_list 
```

We would also want to add `gitlab-dev.inlanefreight.local` to our "interesting hosts" list to dig into once we complete the discovery phase. We may be able to access public Git repos that could contain sensitive information such as credentials or clues that may lead us to other subdomains/Vhosts.

Enumerating one of the hosts further using an Nmap service scan (-sV) against the default top 1,000 ports can tell us more about what is running on the webserver.
```
tylapcheong@htb[/htb]$ sudo nmap --open -sV 10.129.201.50
```

## Using EyeWitness

First up is EyeWitness. As mentioned before, EyeWitness can take the XML output from both Nmap and Nessus and create a report with screenshots of each web application present on the various ports using Selenium.

```
tylapcheong@htb[/htb]$ sudo apt install eyewitness
```


Let's run the default `--web` option to take screenshots using the Nmap XML output from the discovery scan as input.

`tylapcheong@htb[/htb]$ eyewitness --web -x web_discovery.xml -d inlanefreight_eyewitness`

## Using Aquatone

[Aquatone](https://github.com/michenriksen/aquatone), as mentioned before, is similar to EyeWitness and can take screenshots when provided a `.txt` file of hosts or an Nmap `.xml` file with the `-nmap` flag. We can compile Aquatone on our own or download a precompiled binary. After downloading the binary, we just need to extract it, and we are ready to go.

```
tylapcheong@htb[/htb]$ wget https://github.com/michenriksen/aquatone/releases/download/v1.7.0/aquatone_linux_amd64_1.7.0.zip
```
We can move it to a location in our `$PATH` such as `/usr/local/bin` to be able to call the tool from anywhere or just drop the binary in our working (say, scans) directory.

In this example, we provide the tool the same `web_discovery.xml` Nmap output specifying the `-nmap` flag, and we're off to the races.

`tylapcheong@htb[/htb]$ cat web_discovery.xml | ./aquatone -nmap`

## Interpreting the Results

Even with the 26 hosts above, this report will save us time. Now imagine an environment with 500 or 5,000 hosts! After opening the report, we see that the report is organized into categories, with `High Value Targets` being first and typically the most "juicy" hosts to go after.

During an assessment, I would continue reviewing the report, noting down interesting hosts, including the URL and application name/version for later. It is important at this point to remember that we are still in the information gathering phase, and every little detail could make or break our assessment. We should not get careless and begin attacking hosts right away, as we may end up down a rabbit hole and miss something crucial later in the report.

Your mileage may vary, and sometimes we will come across applications that absolutely should not be exposed, such as a single page with a file upload button I encountered once with a message that stated, "Please only upload .zip and .tar.gz files".