## What is a DNS Zone Transfer?
A **DNS zone transfer** is a wholesale copy of all DNS records within a zone (a domain and its subdomains) from one name server to another using the **AXFR (Full Zone Transfer)** type. It ensures consistency and redundancy across secondary servers.

### The 5-Step Process:
1. **Zone Transfer Request (AXFR):** The secondary server requests records from the primary server.
2. **SOA Record Transfer:** The primary server responds with its Start of Authority (SOA) record, containing the serial number to check data currency.
3. **DNS Records Transmission:** The primary server transfers all zone records (`A`, `AAAA`, `MX`, `CNAME`, `NS`, etc.) one by one.
4. **Zone Transfer Complete:** The primary server signals the end of transmission.
5. **Acknowledgement (ACK):** The secondary server confirms receipt, completing the process.

---

## The Zone Transfer Vulnerability
If access controls are misconfigured, unauthorized parties can download the entire zone file, revealing critical information:
- **Hidden Subdomains:** Development servers, staging environments, and internal admin panels.
- **IP Addresses:** Direct mappings for target assets.
- **Name Server Records:** Hosting providers and configuration details.

> **Remediation:** Modern DNS servers restrict zone transfers exclusively to authorized secondary servers. However, human error and legacy setups still occasionally leave this vulnerability exposed.

---

## Exploiting Zone Transfers with `dig`
You can query a name server for a full zone transfer using the `axfr` flag:

```bash
dig axfr @nsztm1.digi.ninja zonetransfer.me