[osTicket](https://osticket.com/) is an open-source support ticketing system.  osTicket is written in PHP and uses a MySQL backend. It can be installed on Windows or Linux.

## Footprinting/Discovery/Enumeration

Looking back at our EyeWitness scan from earlier, we notice a screenshot of an osTicket instance which also shows that a cookie named `OSTSESSID` was set when visiting the page.

Also, most osTicket installs will showcase the osTicket logo with the phrase `powered by` in front of it in the page's footer. The footer may also contain the words `Support Ticket System`.

An Nmap scan will just show information about the webserver, such as Apache or IIS, and will not help us footprint the application.

`osTicket` is a web application that is highly maintained and serviced. If we look at the [CVEs](https://www.cvedetails.com/vendor/2292/Osticket.html) found over decades, we will not find many vulnerabilities and exploits that osTicket could have.

Even if the application is not vulnerable, it can still be used for our purposes. Here we can break down the main functions into the layers:
```
1. User input	2. Processing	3. Solution
```
#### User Input

The core function of osTicket is to inform the company's employees about a problem so that a problem can be solved with the service or other components. A significant advantage we have here is that the application is open-source.
#### Processing

As staff or administrators, they try to reproduce significant errors to find the core of the problem. Processing is finally done internally in an isolated environment that will have very similar settings to the systems in production.

#### Solution

Depending on the depth of the problem, it is very likely that other staff members from the technical departments will be involved in the email correspondence.

## Attacking osTicket

A search for osTicket on exploit-db shows various issues, including remote file inclusion, SQL injection, arbitrary file upload, XSS, etc. osTicket version 1.14.1 suffers from [CVE-2020-24881](https://nvd.nist.gov/vuln/detail/CVE-2020-24881) which was an SSRF vulnerability. If exploited, this type of flaw may be leveraged to gain access to internal resources or perform internal port scanning.

Aside from web application-related vulnerabilities, support portals can sometimes be used to obtain an email address for a company domain, which can be used to sign up for other exposed applications requiring an email verification to be sent.

Let's walk through a quick example, which is related to this [excellent blog post](https://medium.com/intigriti/how-i-hacked-hundreds-of-companies-through-their-helpdesk-b7680ddc2d4c) which [@ippsec](https://twitter.com/ippsec) also mentioned was an inspiration for his box Delivery which I highly recommend checking out after reading this section.

Suppose we find an exposed service such as a company's Slack server or GitLab, which requires a valid company email address to join. Many companies have a support email such as `support@inlanefreight.local`, and emails sent to this are available in online support portals that may range from Zendesk to an internal custom tool.

If we come across a customer support portal during our assessment and can submit a new ticket, we may be able to obtain a valid company email address.

## osTicket - Sensitive Data Exposure

Let's say we are on an external penetration test. During our OSINT and information gathering, we discover several user credentials using the tool [Dehashed](http://dehashed.com/) (for our purposes, the sample data below is fictional).

        shellsession
`tylapcheong@htb[/htb]$ sudo python3 dehashed.py -q inlanefreight.local -p`

This dump shows cleartext passwords for two different users: `jclayton` and `kgrimes`. At this point, we have also performed subdomain enumeration and come across several interesting ones.

        shellsession
`tylapcheong@htb[/htb]$ cat ilfreight_subdomains`

We browse to each subdomain and find that many are defunct, but the `support.inlanefreight.local` and `vpn.inlanefreight.local` are active and very promising. `Support.inlanefreight.local` is hosting an osTicket instance, and `vpn.inlanefreight.local` is a Barracuda SSL VPN web portal that does not appear to be using multi-factor authentication.

We then try the credentials for `kgrimes` and have no success but noticing that the login page also accepts an email address, we try `kevin@inlanefreight.local` and get a successful login!

## Closing Thoughts

Though this section showcased some fictional scenarios, they are based on things we are likely to see in the real world. When we come across support portals (especially external), we should test out the functionality and see if we can do things like creating a ticket and having a legitimate company email address assigned to us. From there, we may be able to use the email address to sign in to other company services and gain access to sensitive data.