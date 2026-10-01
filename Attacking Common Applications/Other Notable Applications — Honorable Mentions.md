> ⚠️ This is not an exhaustive list — the real skill is methodology (fingerprint → check defaults → abuse built-in functionality → check known CVEs), applicable to any unfamiliar application you encounter.

---

## 1. Core Methodology Recap

The underlying approach that generalizes to _any_ application encountered in the wild:

1. **Enumerate the network** — build a visual map of applications for full coverage (e.g., EyeWitness reports can run 500+ pages on large engagements).
2. **Fingerprint and discover** — identify the app, version, and tech stack.
3. **Check default/weak credentials** first — often the fastest win.
4. **Abuse built-in functionality** — many apps have legitimate features (file upload, deployment consoles, APIs) that are trivially abusable for RCE.
5. **Check known public exploits/CVEs** for the identified version.
6. **Don't get discouraged by "boring" scan results** — dig through the noise; a weak-credentialed Tomcat instance or an exposed Git repo with an SSH key can be more valuable than a flashy CVE.

> 💡 Support ticketing systems (osTicket) and Git platforms (GitLab) are called out specifically because they often yield **credentials or secrets useful elsewhere** in the engagement, beyond just their own compromise.

---

## 2. Honorable Mentions Reference Table

|Application|Abuse Notes|
|---|---|
|**Axis2**|Often sits on top of Tomcat. If Tomcat RCE fails, check Axis2 for weak/default admin creds → upload a webshell as an **AAR file** (Axis2 service file). Metasploit module available.|
|**WebSphere**|History of many vulnerabilities. Default creds like `system:manager` on the admin console → deploy a **WAR file** (Tomcat-style) → webshell/reverse shell.|
|**Elasticsearch**|Older but still found on forgotten/legacy installs during large enterprise assessments. HTB box **Haystack** demonstrates this (though not fully realistic).|
|**Zabbix**|Open-source monitoring; history of SQLi, auth bypass, stored XSS, LDAP password disclosure, RCE. Built-in functionality abusable for RCE via the **Zabbix API** — see HTB box **Zipper**.|
|**Nagios**|Monitoring product with RCE, root privesc, SQLi, code injection, stored XSS history. Check default creds **`nagiosadmin:PASSW0RD`** and fingerprint the version.|
|**WebLogic**|Java EE app server — **190 CVEs** at time of writing. Many unauthenticated RCEs (2007–2021), largely **Java Deserialization** vulnerabilities.|
|**Wikis/Intranets** (MediaWiki, SharePoint, custom)|Check for known CVEs, but also check for a **document repository** or **search functionality** — often leaks valid credentials found in indexed documents.|
|**DotNetNuke (DNN)**|Open-source C#/.NET CMS. History of auth bypass, directory traversal, stored XSS, file upload bypass, arbitrary file download.|
|**vCenter**|Manages multiple ESXi instances in large orgs. Check for weak creds + CVEs like an **Apache Struts 2 RCE** (missed by scanners like Nessus) and **CVE-2021-22005** (unauthenticated OVA file upload, disclosed early 2021). Available as Windows or Linux appliance. On Windows appliance, privesc is often trivial via **JuicyPotato**-style tools. Sometimes already running as **SYSTEM** or even a **domain admin** account — can be a single point of full compromise.|

---

## Key Takeaways

- **Default credentials + built-in deployment/upload functionality** is a recurring pattern across almost every app in this list (Axis2 AAR, WebSphere WAR, Zabbix API, Nagios default creds) — always check this combination first.
- Monitoring/management platforms (Zabbix, Nagios, vCenter, WebSphere/WebLogic) tend to run with **high privileges** on the host and/or have broad network reach — compromising one can be disproportionately valuable.
- Document repositories and internal search functionality (wikis, intranets, SharePoint) are an underrated source of **leaked credentials** — don't skip searching them just because they seem like "just documentation."
- vCenter in particular is a **high-value target**: it's sometimes found running as SYSTEM or even a domain admin account, making it a potential single point of full domain compromise.
- When encountering an application not covered anywhere (module or this list), fall back to the **core methodology**: fingerprint → default creds → built-in functionality abuse → known CVEs. This generalizes indefinitely.