The first point of presence on the Internet may be the `SSL certificate` from the company's main website that we can examine. Often, such a certificate includes more than just a subdomain, and this means that the certificate is used for several domains, and these are most likely still active.

Another source to find more subdomains is [crt.sh](https://crt.sh/). This source is [Certificate Transparency](https://en.wikipedia.org/wiki/Certificate_Transparency) logs. Certificate Transparency is a process that is intended to enable the verification of issued digital certificates for encrypted Internet connections.

tylapcheong@htb[/htb]$ curl -s https://crt.sh/\?q\=inlanefreight.com\&output\=json | jq . | grep name | cut -d":" -f2 | grep -v "CN=" | cut -d'"' -f2 | awk '{gsub(/\\n/,"\n");}1;' | sort -u

#### Company Hosted Servers

`tylapcheong@htb[/htb]$ for i in $(cat subdomainlist);do host $i | grep "has address" | grep inlanefreight.com | cut -d" " -f1,4;done`

#### Shodan - IP List


`tylapcheong@htb[/htb]$ for i in $(cat subdomainlist);do host $i | grep "has address" | grep inlanefreight.com | cut -d" " -f4 >> ip-addresses.txt;done tylapcheong@htb[/htb]$ for i in $(cat ip-addresses.txt);do shodan host $i;done`


#### DNS Records

`tylapcheong@htb[/htb]$ dig any inlanefreight.com`
- `A` records: We recognize the IP addresses that point to a specific (sub)domain through the A record. Here we only see one that we already know.
- `MX` records: The mail server records show us which mail server is responsible for managing the emails for the company. Since this is handled by google in our case, we should note this and skip it for now.
- `NS` records: These kinds of records show which name servers are used to resolve the FQDN to IP addresses. Most hosting providers use their own name servers, making it easier to identify the hosting provider.
- `TXT` records: this type of record often contains verification keys for different third-party providers and other security aspects of DNS, such as [SPF](https://datatracker.ietf.org/doc/html/rfc7208), [DMARC](https://datatracker.ietf.org/doc/html/rfc7489), and [DKIM](https://datatracker.ietf.org/doc/html/rfc6376), which are responsible for verifying and confirming the origin of the emails sent. Here we can already see some valuable information if we look closer at the results.
# Cloud Resources

---

The use of cloud, such as [AWS](https://aws.amazon.com/), [GCP](https://cloud.google.com/), [Azure](https://azure.microsoft.com/en-us/), and others, is now one of the essential components for many companies nowadays

Things to check:
	Target Website - Source code
	Private and Public SSH Keys leaked.

Staff
- Linkedin
- Job post => Can include tech stack info