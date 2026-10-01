
> **Source / Context:** Web Crawling & Reconnaissance notes (compatible with Obsidian)
> **Target Example:** `inlanefreight.com`

---

## 📋 Overview
Web crawling is vast and intricate, but automation tools can streamline the process, making it faster and more efficient. This allows you to focus on analyzing the extracted data rather than manual collection.

---

## 🛠️ Popular Web Crawlers

| Tool | Type | Key Features & Best Use Cases |
| :--- | :--- | :--- |
| **Burp Suite Spider** | Active Crawler / Testing Platform | Excellent for mapping out web applications, identifying hidden content, and uncovering vulnerabilities. |
| **OWASP ZAP** (Zed Attack Proxy) | Free, Open-Source Security Scanner | Supports automated and manual modes; includes a spider component to crawl applications and find vulnerabilities. |
| **Scrapy** | Python Framework | Versatile and scalable framework for custom web crawlers. Ideal for tailored reconnaissance, structured data extraction, and handling complex crawling logic. |
| **Apache Nutch** | Scalable Java Crawler | Highly extensible and designed for massive, multi-domain web crawls. Requires higher technical setup but powerful for large-scale projects. |

> ⚠️ **Ethical & Responsible Crawling:** Always obtain permission before crawling a website (especially for extensive/intrusive scans). Be mindful of server resources and avoid overloading targets with excessive requests.

---

## 🕷️ Practical Reconnaissance with Scrapy & ReconSpider

We will leverage **Scrapy** and a custom spider (`ReconSpider`) tailored for reconnaissance on `inlanefreight.com`.

### 1. Installation
Ensure Scrapy is installed on your system via `pip`:
```
tylapcheong@htb[/htb]$ pip3 install scrapy
```
### ReconSpider

First, run this command in your terminal to download the custom scrapy spider, `ReconSpider`, and extract it to the current working directory.

```
tylapcheong@htb[/htb]$ wget -O ReconSpider.zip https://academy.hackthebox.com/storage/modules/144/ReconSpider.v1.2.zip

tylapcheong@htb[/htb]$ unzip ReconSpider.zip 
```

With the files extracted, you can run `ReconSpider.py` using the following command:

        shellsession
```
tylapcheong@htb[/htb]$ python3 ReconSpider.py http://inlanefreight.com
```

Replace `inlanefreight.com` with the domain you want to spider. The spider will crawl the target and collect valuable information.

### results.json

After running `ReconSpider.py`, the data will be saved in a JSON file, `results.json`.