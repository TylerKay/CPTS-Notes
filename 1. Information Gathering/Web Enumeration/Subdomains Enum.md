subdomain_bf_md = """# Subdomain Brute-Forcing & DNSEnum

## Subdomain Brute-Force Enumeration
Subdomain brute-forcing is an active discovery technique that tests pre-defined lists of potential subdomain names against a target domain.

### The 4-Step Process:
1. **Wordlist Selection:** Choose from general-purpose (common names like `dev`, `blog`), targeted (industry/tech-specific), or custom wordlists.
2. **Iteration and Querying:** Scripts append each word to the main domain to generate target names (e.g., `dev.example.com`).
3. **DNS Lookup:** Performs DNS queries (usually `A` or `AAAA` records) to see if the name resolves.
4. **Filtering and Validation:** Valid entries are saved for further inspection or functional testing via browsers.

---

## Common Subdomain Bruteforcing Tools

| Tool | Description |
| :--- | :--- |
| **`dnsenum`** | Comprehensive DNS enumeration toolkit supporting dictionary and brute-force attacks. |
| **`fierce`** | User-friendly tool for recursive subdomain discovery with wildcard detection. |
| **`dnsrecon`** | Versatile utility combining multiple DNS recon techniques with customizable outputs. |
| **`amass`** | Actively maintained tool known for data source integration and deep discovery. |
| **`assetfinder`** | Lightweight, simple, and effective tool ideal for quick scans. |
| **`puredns`** | Powerful and flexible DNS brute-forcing tool with robust resolution and filtering. |

---

## DNSEnum Deep Dive
`dnsenum` is a versatile Perl-based command-line tool for comprehensive DNS reconnaissance.

### Key Features:
- **DNS Record Enumeration:** Retrieves `A`, `AAAA`, `NS`, `MX`, and `TXT` records.
- **Zone Transfer Attempts:** Automatically checks name servers for misconfigured zone transfers.
- **Subdomain Brute-Forcing:** Systematically tests candidate names against targets using wordlists.
- **Google Scraping:** Scrapes search engine results to find subdomains missing from standard records.
- **Reverse Lookups & WHOIS:** Finds co-hosted domains on the same IP and checks registration info.

### Example Command (`dnsenum`):
```bash
dnsenum --enum inlanefreight.com -f /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt -r