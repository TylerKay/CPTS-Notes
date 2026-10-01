markdown_content = """---
tags:
  - web-reconnaissance
  - security
  - htb
  - osint
  - search-engines
  - google-dorking
---

# Search Engine Discovery & OSINT

> **Context:** HTB Module Notes - Search Engine Discovery & Google Dorking
> **Purpose:** Using search engines as powerful web reconnaissance tools to uncover hidden information, sensitive files, and potential vulnerabilities.

---

## 📋 Overview
Beyond everyday queries, search engines index a vast portion of the web, holding a treasure trove of public data. **Search engine discovery (OSINT gathering)** uses advanced search algorithms, operators, and techniques to extract hard-to-find data without intrusive scanning.

### Why It Matters
* **Open Source:** Publicly accessible, making it fully legal and ethical.
* **Breadth & Ease:** Requires no specialized technical skills while covering massive data sources.
* **Cost-Effective:** Free and readily available resource for initial reconnaissance.

### Core Application Areas
* **Security Assessment:** Identifying vulnerabilities, exposed data, and attack vectors.
* **Competitive Intelligence:** Gathering insight into competitor products and strategies.
* **Investigative Journalism:** Uncovering hidden connections and records.
* **Threat Intelligence:** Tracking malicious actors and predicting potential attacks.

> ⚠️ **Limitation Note:** Search engines do not index everything; some data may be deliberately hidden, protected, or restricted.

---

## 🔎 Advanced Search Operators

Search operators act as "secret codes" to pinpoint specific details across indexed websites.

| Operator                      | Description                                        | Example                                             | Example Description                                            |
| :---------------------------- | :------------------------------------------------- | :-------------------------------------------------- | :------------------------------------------------------------- |
| **`site:`**                   | Limits results to a specific domain.               | `site:example.com`                                  | Find all publicly accessible pages on example.com.             |
| **`inurl:`**                  | Finds pages with a specific term in the URL.       | `inurl:login`                                       | Search for login pages on any website.                         |
| **`filetype:`**               | Searches for files of a particular type.           | `filetype:pdf`                                      | Find downloadable PDF documents.                               |
| **`intitle:`**                | Finds pages with a specific term in the title.     | `intitle:"confidential report"`                     | Look for documents titled "confidential report" or similar.    |
| **`intext:`** / **`inbody:`** | Searches for a term within the body text.          | `intext:"password reset"`                           | Identify webpages containing the phrase.                       |
| **`cache:`**                  | Displays the cached version of a webpage.          | `cache:example.com`                                 | View previous content of example.com.                          |
| **`link:`**                   | Finds pages linking to a specific webpage.         | `link:example.com`                                  | Identify websites linking to example.com.                      |
| **`related:`**                | Finds websites similar to a specific webpage.      | `related:example.com`                               | Discover similar websites.                                     |
| **`info:`**                   | Provides a summary of a webpage.                   | `info:example.com`                                  | Get basic details and description.                             |
| **`define:`**                 | Provides definitions of a word or phrase.          | `define:phishing`                                   | Get definitions from various sources.                          |
| **`numrange:`**               | Searches for numbers within a specific range.      | `site:example.com numrange:1000-2000`               | Find numbers between 1000-2000 on a domain.                    |
| **`allintext:`**              | Finds pages with all specified words in the body.  | `allintext:admin password reset`                    | Search for pages containing all terms in body text.            |
| **`allinurl:`**               | Finds pages with all specified words in the URL.   | `allinurl:admin panel`                              | Look for pages with multiple terms in the URL.                 |
| **`allintitle:`**             | Finds pages with all specified words in the title. | `allintitle:confidential report 2023`               | Search for exact terms in the page title.                      |
| **`AND`**                     | Narrows results requiring all terms to be present. | `site:example.com AND (inurl:admin OR inurl:login)` | Find admin or login pages on a specific domain.                |
| **`OR`**                      | Broadens results including any of the terms.       | `"linux" OR "ubuntu" OR "debian"`                   | Search for pages mentioning alternative terms.                 |
| **`NOT`**                     | Excludes results containing the specified term.    | `site:bank.com NOT inurl:login`                     | Find domain pages excluding specific patterns.                 |
| **`*` (wildcard)**            | Represents any character or word.                  | `site:socialnetwork.com filetype:pdf user* manual`  | Find wildcard variations like "user guide" or "user handbook". |
| **`...` (range)**             | Finds results within a numerical range.            | `site:ecommerce.com "price" 100..500`               | Look for items within a specific price bracket.                |
| **`" "`**                     | Searches for exact phrases.                        | `"information security policy"`                     | Force exact match text matching.                               |
| **`-` (minus)**               | Excludes terms from the search results.            | `site:news.com -inurl:sports`                       | Filter out unwanted sub-topics or pages.                       |

---

## 🕵️‍♂️ Google Dorking (Google Hacking)

**Google Dorking** leverages search operators to unearth sensitive information, security vulnerabilities, or hidden content indexed by Google. For extended patterns, reference the **Google Hacking Database (GHDB)**.

### Common Dorking Patterns

* **Finding Login Pages:**
  ```text
  site:example.com inurl:login
  site:example.com (inurl:login OR inurl:admin)