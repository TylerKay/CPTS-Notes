## Introduction
The `.well-known` standard, defined in **RFC 8615**, provides a standardized directory (`/.well-known/`) within a website's root domain to centralize critical metadata, configuration files, and service information. 

- **Purpose:** Simplifies automated discovery for browsers, tools, and clients without requiring custom paths or guessing.
- **Maintained By:** The Internet Assigned Numbers Authority (IANA) hosts an official registry of `.well-known` URIs.

---

## Common IANA-Registered `.well-known` URIs

| URI Suffix | Description | Status | Reference |
| :--- | :--- | :--- | :--- |
| **`security.txt`** | Contains contact details for security researchers to report vulnerabilities. | Permanent | [RFC 9116](https://datatracker.ietf.org/doc/html/rfc9116) |
| **`change-password`** | Directs users to a standard password change page. | Provisional | [W3C Spec](https://w3c.github.io/webappsec-change-password-url/) |
| **`openid-configuration`** | Defines configuration details and metadata for OpenID Connect (OIDC). | Permanent | [OIDC Discovery](http://openid.net/specs/openid-connect-discovery-1_0.html) |
| **`assetlinks.json`** | Used for verifying ownership of digital assets (e.g., mobile apps) tied to a domain. | Permanent | [Google Digital Asset Links](https://github.com/google/digitalassetlinks) |
| **`mta-sts.txt`** | Specifies SMTP MTA Strict Transport Security policies to secure email. | Permanent | [RFC 8461](https://datatracker.ietf.org/doc/html/rfc8461) |

---

## Web Reconnaissance Value
During web assessments, `.well-known` endpoints are goldmines for exposing hidden architecture, authentication endpoints, and security policies.

### Highlight: OpenID Connect Configuration (`/.well-known/openid-configuration`)
For applications leveraging OIDC or OAuth 2.0, this endpoint returns a structured JSON document detailing server capabilities, paths, and cryptographic details.

**Example JSON Response:**
```json
{
  "issuer": "[https://example.com](https://example.com)",
  "authorization_endpoint": "[https://example.com/oauth2/authorize](https://example.com/oauth2/authorize)",
  "token_endpoint": "[https://example.com/oauth2/token](https://example.com/oauth2/token)",
  "userinfo_endpoint": "[https://example.com/oauth2/userinfo](https://example.com/oauth2/userinfo)",
  "jwks_uri": "[https://example.com/oauth2/jwks](https://example.com/oauth2/jwks)",
  "response_types_supported": ["code", "token", "id_token"],
  "subject_types_supported": ["public"],
  "id_token_signing_alg_values_supported": ["RS256"],
  "scopes_supported": ["openid", "profile", "email"]
}