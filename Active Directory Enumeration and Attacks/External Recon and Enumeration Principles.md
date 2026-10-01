External reconnaissance and enumeration form the foundation of a comprehensive penetration test. This phase involves gathering publicly accessible data to map the target's digital footprint, validate scoping documents, identify information leaks, and uncover potential entry points without directly attacking infrastructure.

## Purpose of External Recon

* **Validate Scope:** Verify information provided in the client's scoping document.
* **Ensure Compliance:** Confirm actions are taken against appropriate remote targets within the defined scope.
* **Identify Leaks:** Locate publicly accessible information (e.g., leaked credentials, internal document links, schema formats) that impacts the test outcome.

---

## What Are We Looking For?

| Data Point | Description |
| :--- | :--- |
| **IP Space** | Valid ASN for the target, netblocks in use for public-facing infrastructure, cloud presence, hosting providers, and DNS record entries. |
| **Domain Information** | Administrative contacts, subdomains, publicly accessible domain services (mail servers, DNS, websites, VPN portals), and visible defense mechanisms (SIEM, AV, IPS/IDS). |
| **Schema Format** | Email accounts, Active Directory usernames, and password policies to build valid username lists for external-facing service attacks (password spraying, brute forcing, etc.). |
| **Data Disclosures** | Publicly accessible files (`.pdf`, `.ppt`, `.docx`, `.xlsx`) containing intranet site listings, user metadata, or pushed credentials (e.g., public GitHub repositories). |
| **Breach Data** | Publicly released usernames, passwords, or critical data to help establish an initial foothold. |

---

## Where Are We Looking? (Resources & Tools)

| Resource | Examples & Tools |
| :--- | :--- |
| **ASN / IP Registrars** | IANA, ARIN, RIPE, BGP Toolkit (`bgp.he.net`) |
| **Domain Registrars & DNS** | Domaintools, PTRArchive, ICANN, manual DNS queries via `nslookup` or `8.8.8.8`, ViewDNS (`viewdns.info`) |
| **Social Media** | LinkedIn, Twitter, Facebook, major regional platforms, and news articles |
| **Company Websites** | Corporate "About Us" and "Contact Us" pages, embedded documents, news articles |
| **Cloud & Dev Storage** | GitHub, AWS S3 buckets, Azure Blob storage, Google Dorks (e.g., `filetype:pdf inurl:target.com`), Trufflehog, Greyhat Warfare |
| **Breach Data Sources** | HaveIBeenPwned, Dehashed |

---

## Methodology & Step-by-Step Process

### Step 1: Define Scope & Review Parameters
* **Action:** Examine the scoping document provided by the client to understand approved targets, exclusions, and rules of engagement.
* **Verification:** Confirm all domains, IP blocks, and third-party hosted services are explicitly listed and authorized for testing. Clarify any ambiguous self-hosted vs. third-party managed infrastructure with management or legal teams before proceeding.

### Step 2: Perform Passive IP & ASN Research
* **Action:** Use tools like Hurricane Electric's BGP-Toolkit to identify Autonomous System Numbers (ASNs), netblocks, and cloud or self-hosted infrastructure.
* **Verification:** Cross-reference discovered IP addresses with domain validation tools such as `viewdns.info` to ensure current accuracy and avoid scanning unapproved infrastructure sharing the same hosting provider.

### Step 3: Gather Domain & DNS Information
* **Action:** Query DNS records using tools like `nslookup`, `domaintools`, or ViewDNS to map subdomains, mail servers, and authoritative nameservers.
	```
	nslookup -type=txt {domainName}
	```

* **Verification:** Ensure any newly discovered subdomains or external services reside on in-scope IP addresses before further interaction.

### Step 4: Conduct OSINT & Public Data Harvesting
* **Action:** Search social media platforms (LinkedIn, Twitter), corporate websites, and job postings to determine organizational structures, software versions (e.g., SharePoint 2013/2016), and email naming conventions (e.g., `first.last`).
* **Verification:** Document discovered employee names, email formats, and technology stacks for future targeting.

### Step 5: Search for Data Disclosures & Leaked Credentials
* **Action:** Use search engine dorks (e.g., `intext:"@target.com" inurl:target.com`) to find exposed documents or contact pages, and check breach databases (such as Dehashed) for leaked corporate credentials using tools or API scripts.
* **Verification:** Securely download any discovered files locally, archive screenshots or tool outputs immediately, and compile harvested usernames and passwords into structured lists for potential authorized password-spraying scenarios.


