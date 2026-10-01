
---

When attacking a service, we usually play a detective role, and we need to collect as much information as possible and carefully observe the details. Therefore, every single piece of information is essential.

A misconfigured service let us access a piece of information that initially may look insignificant, `johnsmith`, but that information opened the doors for us to discover more information and finally get remote code execution on the database server. This is the importance of paying attention to every piece of information, every detail, as we enumerate and attack common services.

Sensitive information may include, but is not limited to:

- Usernames.
- Email Addresses.
- Passwords.
- DNS records.
- IP Addresses.
- Source code.
- Configuration files.
- PII.

This module will cover some common services where we can find interesting information and discover different methods and tools we can use to automate our discovery process. These services include:

- File Shares.
- Email.
- Databases.

---

#### Understanding of What We Have to Look for

Every target is unique, and we need to familiarize ourselves with our target, its processes, procedures, business model, and purpose. Once we understand our target, we can think about what information is essential for them and what kind of information is helpful for our attack.

There are two key elements to finding sensitive information:

1. We need to understand the service and how it works.
2. We need to know what we are looking for.