## 0. Target Profiling & Scope

- [ ]  Identify target domain(s)
- [ ]  Identify target IP(s)
- [ ]  Note any provided hostnames
- [ ]  Add findings to notes immediately
- [ ]  Create a running list of:
    - Domains
    - Subdomains
    - Virtual Hosts
    - IP addresses
    - Technologies
    - Interesting endpoints

**Goal:** Build a master asset list early. 12

---

# 1. Passive Reconnaissance

## WHOIS

- [ ]  Query WHOIS records
- [ ]  Identify:
    - Registrar
    - Registrant information
    - Administrative contacts
    - Technical contacts
    - Name servers
    - Registration dates
- [ ]  Record all discovered nameservers

**Potential Findings**

- Additional infrastructure
- Organization information
- DNS servers for further enumeration

1

---

## Search Engine Discovery / OSINT

### Domain Discovery

- [ ]  Search:
    - `site:target.com`
    - `site:*.target.com`
    - `cache:target.com`
    - `link:target.com`
    - `related:target.com`

### Sensitive Data Discovery

- [ ]  Search:
    - `site:target.com filetype:pdf`
    - `site:target.com filetype:xls`
    - `site:target.com filetype:doc`
    - `site:target.com inurl:admin`
    - `site:target.com inurl:login`
    - `site:target.com intitle:index.of`

### Content Discovery

- [ ]  Search:
    - `intext:"password"`
    - `allinurl:admin`
    - `allintitle:admin`

**Goal:** Identify indexed assets and exposed files.

3

---

## Web Archive Investigation

### Wayback Machine

- [ ]  Review oldest snapshots
- [ ]  Review newest snapshots
- [ ]  Compare changes over time

Look for:

- [ ]  Old admin portals
- [ ]  Legacy applications
- [ ]  Deprecated directories
- [ ]  Previous subdomains
- [ ]  Developer comments
- [ ]  Old technologies

**Goal:** Discover assets no longer linked publicly.

4

---

# 2. DNS Enumeration

## Core DNS Records

Enumerate:

- [ ]  A
- [ ]  AAAA
- [ ]  NS
- [ ]  MX
- [ ]  TXT
- [ ]  SRV
- [ ]  PTR
- [ ]  SOA

Record:

- [ ]  Nameservers
- [ ]  Mail servers
- [ ]  External providers
- [ ]  SPF records
- [ ]  Potential internal names
---
## Zone Transfer Assessment

### Check Each Authoritative Nameserver

- [ ]  Attempt AXFR
Look for:
- [ ]  Hidden subdomains
- [ ]  Internal systems
- [ ]  Development environments
- [ ]  Administrative portals
- [ ]  IP mappings
If successful:

- [ ]  Save entire zone output
---
# 3. Subdomain Enumeration

## Passive Techniques

### Certificate Transparency Logs
Search:
- [ ]  crt.sh
- [ ]  Censys
Look for:
- [ ]  Historical subdomains
- [ ]  Expired assets
- [ ]  Staging systems
- [ ]  Development hosts

Document every finding.

---
### OSINT Sources

- [ ]  Search engines
- [ ]  Historical records
- [ ]  Public DNS datasets

---

## Active Techniques
### Brute Force Discovery

Use multiple wordlists:
- [ ]  Common
- [ ]  Technology-specific
- [ ]  Custom
Tools:
- [ ]  dnsenum
- [ ]  dnsrecon
- [ ]  fierce
- [ ]  amass
- [ ]  assetfinder
- [ ]  puredns
Validate:
- [ ]  A records
- [ ]  AAAA records
- [ ]  Live web service
---
# 4. Virtual Host Enumeration

## Hidden VHosts

For every discovered IP:

- [ ]  Test for name-based virtual hosting
- [ ]  Enumerate host headers
- [ ]  Fuzz additional hostnames
Tools:
- [ ]  gobuster
- [ ]  ffuf
- [ ]  feroxbuster
Questions:
- [ ]  Same IP hosting multiple sites?
- [ ]  Default page changing?
- [ ]  Different responses per Host header?
### Hosts File

- [ ]  Add discovered VHosts to hosts file
- [ ]  Browse manually
---
# 5. Web Crawling

## Crawl Entire Application

Collect:

- [ ]  Internal links
- [ ]  External links
- [ ]  Comments
- [ ]  Metadata
- [ ]  Hidden files
- [ ]  Parameters

Pay special attention to:

### Comments

- [ ]  Usernames
- [ ]  Credentials
- [ ]  Internal references
- [ ]  Development notes

### Metadata

- [ ]  Authors
- [ ]  Software
- [ ]  Keywords

### Sensitive Files

- [ ]  Backup files
- [ ]  Config files
- [ ]  Logs
- [ ]  Source code leaks
---
# 6. robots.txt Review

- [ ]  Visit `/robots.txt`

Document:

- [ ]  Disallow entries
- [ ]  Interesting directories
- [ ]  Sensitive locations
- [ ]  Administrative panels

Remember:

- [ ]  Disallowed does NOT mean inaccessible

Often reveals:

- Hidden content
- Admin locations
- Backup paths

11

---

# 7. Well-Known URI Discovery

Check:

```
/.well-known/
```

Investigate:

- [ ]  security.txt
- [ ]  openid-configuration
- [ ]  change-password
- [ ]  assetlinks.json
- [ ]  mta-sts.txt

Look for:

- [ ]  Authentication endpoints
- [ ]  OAuth/OIDC services
- [ ]  Internal architecture
- [ ]  API locations
- [ ]  Security contacts

12

---

# 8. Fingerprinting

## HTTP Header Analysis

Check:

- [ ]  Server
- [ ]  X-Powered-By
- [ ]  Security headers
- [ ]  Redirect behavior

1314

---

## Technology Detection

Identify:

- [ ]  Web server
- [ ]  Operating system
- [ ]  Frameworks
- [ ]  CMS
- [ ]  WAF
- [ ]  Analytics

Tools:

- [ ]  Wappalyzer
- [ ]  BuiltWith
- [ ]  WhatWeb
- [ ]  Netcraft
- [ ]  wafw00f
- [ ]  Nmap

13

---

## Application Fingerprinting

Look for:

- [ ]  Error messages
- [ ]  JavaScript libraries
- [ ]  Framework artifacts
- [ ]  CMS indicators
- [ ]  Versions

Questions:

- [ ]  Is software outdated?
- [ ]  Known exploits available?
- [ ]  Misconfigurations present?

13

---

# 9. Historical Asset Discovery

Cross-reference:

- [ ]  CT Logs
- [ ]  Wayback Machine
- [ ]  Search engines

Search for:

- [ ]  Old directories
- [ ]  Retired subdomains
- [ ]  Deprecated applications
- [ ]  Archived APIs

743

---

# 10. Automation Phase

After manual recon:

Run automated frameworks:

- [ ]  FinalRecon
- [ ]  Recon-ng
- [ ]  SpiderFoot
- [ ]  theHarvester

Collect:

- [ ]  Headers
- [ ]  WHOIS
- [ ]  SSL information
- [ ]  DNS records
- [ ]  Subdomains
- [ ]  Crawling results
- [ ]  Historical URLs

Compare automated findings against manual notes.

**Never trust automation alone. Verify everything manually.**

14

---

# CPTS Final Enumeration Checklist (30-Second Review)

Before moving to exploitation:

- [ ]  WHOIS completed
- [ ]  DNS records mapped
- [ ]  Nameservers identified
- [ ]  AXFR tested
- [ ]  CT logs searched
- [ ]  Passive subdomains collected
- [ ]  Brute-force subdomains completed
- [ ]  VHosts fuzzed
- [ ]  robots.txt reviewed
- [ ]  .well-known reviewed
- [ ]  Site crawled
- [ ]  Historical archives checked
- [ ]  Technologies fingerprinted
- [ ]  WAF identified
- [ ]  Interesting files downloaded
- [ ]  Authentication endpoints documented
- [ ]  Target attack surface mapped

````markdown
---
title: Web Enumeration Methodology
tags:
  - CPTS
  - web-enumeration
  - reconnaissance
  - methodology
  - field-manual
---

# Web Enumeration Methodology

## Purpose

This methodology provides a structured process for enumerating an authorized web target. The workflow moves from low-interaction information gathering to direct enumeration, then consolidates discovered domains, hostnames, virtual hosts, technologies, paths, files, and authentication endpoints into a working attack-surface map.

&gt; [!CAUTION]
&gt; Perform enumeration only against systems for which you have explicit authorization. Respect scope restrictions, rate limits, server resources, and applicable crawling requirements.

---

# 1. Engagement Preparation

## 1.1 Confirm Scope

- [ ] Record each authorized domain.
- [ ] Record each authorized IP address.
- [ ] Record exclusions and prohibited techniques.
- [ ] Confirm whether active DNS enumeration is permitted.
- [ ] Confirm whether crawling and content discovery are permitted.
- [ ] Confirm whether third-party or externally hosted assets are in scope.
- [ ] Keep passive discoveries separate from confirmed in-scope assets.

## 1.2 Create an Evidence Structure

Create a working directory for the target:

```text
web-enum/
├── notes/
├── whois/
├── dns/
├── certificates/
├── subdomains/
├── vhosts/
├── headers/
├── crawling/
├── archives/
├── screenshots/
└── findings/
````

Maintain a master asset register:

|Asset|Type|IP Address|Source|Resolved|HTTP Status|Technology|Notes|
|---|---|---|---|---|---|---|---|
|target.tld|Root domain||Scope|||||
|host.target.tld|Subdomain/VHost|||||||

## 1.3 Establish the Enumeration Loop

Repeat the following loop whenever a new hostname, IP address, application, or path is discovered:

1. Record the discovery and its source.
2. Resolve the hostname or identify its associated IP.
3. determine whether it is in scope.
4. Inspect its web behavior.
5. Fingerprint the exposed technology.
6. Crawl and review discoverable content.
7. Feed new names, paths, and technologies back into enumeration.

---

# 2. Passive Reconnaissance

Passive reconnaissance relies on public or third-party sources rather than direct interaction with the target infrastructure.

## 2.1 WHOIS Enumeration

WHOIS records may contain information about the domain, registrar, registrant, administrative and technical contacts, creation and expiration dates, and name servers.

```bash
whois 
```

Record:

- [ ]  Domain name
- [ ]  Registrar
- [ ]  Registrant organization or contact, if exposed
- [ ]  Administrative contact, if exposed
- [ ]  Technical contact, if exposed
- [ ]  Creation date
- [ ]  Expiration date
- [ ]  Authoritative name servers
- [ ]  Related domains or infrastructure references
- [ ]  Potential naming conventions

### Evidence

```text
Target:
Registrar:
Created:
Expires:
Name servers:
Contacts:
Additional clues:
```

---

## 2.2 Search Engine Discovery

Use search-engine operators to identify indexed pages, login locations, documents, and references associated with the target.

### Baseline Discovery

```text
site:target.tld
inurl:login site:target.tld
filetype:pdf site:target.tld
intitle:"confidential report" site:target.tld
intext:"password reset" site:target.tld
site:target.tld AND (inurl:admin OR inurl:login)
```

Available operators include:

- `site:` to restrict results to a domain
- `inurl:` to search terms in URLs
- `filetype:` to search for specific file types
- `intitle:` to search page titles
- `intext:` or `inbody:` to search page content
- `cache:` to request cached content where supported
- `link:` to locate pages linking to a target
- `related:` to find similar sites
- `allintext:` to require terms in page content
- `allinurl:` to require terms in a URL
- `allintitle:` to require terms in a title
- `AND`, `OR`, and `NOT` to combine or exclude conditions
- Quotation marks to search for exact phrases
- Wildcards to search for variations

Record:

- [ ]  Indexed subdomains
- [ ]  Login or administrative pages
- [ ]  Publicly accessible documents
- [ ]  Interesting URL patterns
- [ ]  Names, email addresses, or technology references
- [ ]  Paths that should be validated later
- [ ]  References to retired or renamed services

> [!NOTE] > Search engines do not index everything. Missing search results do not indicate that an asset or resource does not exist.

---

## 2.3 Certificate Transparency Logs

Certificate Transparency logs are public append-only records of SSL/TLS certificate issuance. Certificate names and Subject Alternative Name entries can reveal present and historical subdomains, including names associated with expired certificates.

Review:

- [ ]  `crt.sh`
- [ ]  Censys certificate data, where available
- [ ]  Certificate names
- [ ]  Subject Alternative Names
- [ ]  Wildcard certificates
- [ ]  Expired certificate entries
- [ ]  Development, staging, administrative, API, VPN, mail, and legacy naming patterns

An example documented query against the `crt.sh` JSON API is:

```bash
curl -s "https://crt.sh/?q=facebook.com&amp;output=json" \
| jq -r '.[] | select(.name_value | contains("dev")) | .name_value' \
| sort -u
```

Replace the example domain and filter with values appropriate to the authorized target.

### Validation Queue

```text
Candidate hostname:
Certificate source:
Certificate status:
Resolved:
Address:
In scope:
Web reachable:
Notes:
```

Do not assume every certificate name remains active. Add discovered names to the validation queue.

---

## 2.4 Historical Web Archives

The Wayback Machine stores historical snapshots that may include HTML, CSS, JavaScript, images, old pages, and earlier versions of site content.

Review:

- [ ]  Earliest available snapshots
- [ ]  Recent available snapshots
- [ ]  Major layout or application changes
- [ ]  Historical directories
- [ ]  Old files
- [ ]  Historical subdomains
- [ ]  Retired login pages
- [ ]  Legacy parameters
- [ ]  Technology references
- [ ]  JavaScript paths
- [ ]  API references
- [ ]  Content removed from the current site

Record historical assets separately until they are validated against the current target.

> [!NOTE] > Web archives do not capture every webpage, and archived content may have been excluded or may no longer represent the live application.

---

# 3. DNS Enumeration

DNS enumeration maps names to addresses and identifies authoritative, mail, service, alias, and administrative records.

## 3.1 Enumerate Core Records

Review the following record types:

- [ ]  `A`: hostname to IPv4 address
- [ ]  `AAAA`: hostname to IPv6 address
- [ ]  `CNAME`: alias to canonical hostname
- [ ]  `MX`: mail server
- [ ]  `NS`: authoritative name server
- [ ]  `TXT`: arbitrary text, including verification or SPF information
- [ ]  `SOA`: administrative zone information
- [ ]  `SRV`: service location and port
- [ ]  `PTR`: reverse DNS mapping

Documented `dig` examples include:

```bash
dig 
dig  A
dig  AAAA
dig  MX
dig 
```