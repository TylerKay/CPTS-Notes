When a web application trusts unfiltered XML data from user input, we may be able to reference an external XML DTD document and define new custom XML entities.

## Identifying

The first step in identifying potential XXE vulnerabilities is finding web pages that accept an XML user input.

If we fill the contact form and click on `Send Data`, then intercept the HTTP request with Burp, we get the following request: 

As we can see, the form appears to be sending our data in an XML format to the web server, making this a potential XXE testing target.

We see that the value of the `email` element is being displayed back to us on the page. To print the content of an external file to the page, we should `note which elements are being displayed, such that we know which elements to inject into`




Here is a concise, structured summary of the reading material to add to your study notes:

## XML External Entity (XXE) Overview

**XML External Entity (XXE)** vulnerabilities occur when a web application accepts unfiltered XML user input and uses outdated XML libraries without proper sanitization. This allows attackers to define custom external XML entities and reference internal or external resources.

### 1. Identifying XXE Vulnerabilities

- **Target Identification:** Look for HTTP requests sending XML data (e.g., contact forms, API requests).
    
    - _Tip:_ Even if an app uses JSON, changing `Content-Type` to `application/xml` may work if the backend accepts XML.
        
- **Testing Execution:**
    
    1. Identify which XML elements are reflected in the HTTP response (e.g., `<email></email>`).
        
    2. Declare a custom DTD entity (e.g., `<!ENTITY company "Inlane Freight">`).
        
    3. Reference the entity in a reflected element (`&company;`).
        
    4. If the rendered output replaces the reference with the custom value, the app is vulnerable.
        

### 2. Reading Sensitive Files (Local File Disclosure)

- **Mechanism:** Use the `SYSTEM` keyword in the entity declaration to point to a local file system path:
    
    XML
    
    ```
    <!DOCTYPE email [ <!ENTITY company SYSTEM "file:///etc/passwd"> ]>
    ```
    
- **Impact:** Discloses sensitive system files (e.g., `/etc/passwd`, SSH keys like `id_rsa`, or system configuration files).
    
- **Java Exception:** In some Java environments, referencing a directory path instead of a file may render a directory listing.
    

### 3. Reading Source Code & Binary Files

- **Challenge:** Plain XML fails to reference files containing special XML characters (`<`, `>`, `&`) or binary data, causing parsing errors.
    
- **Solution (PHP Filter Wrapper):** Use the Base64 encoding filter in PHP to encode the file before it is parsed by the XML engine:
    
    XML
    
    ```
    <!DOCTYPE email [ <!ENTITY company SYSTEM "php://filter/convert.base64-encode/resource=index.php"> ]>
    ```
    
- **Result:** Returns a Base64 string that can be decoded to view source code, database credentials, or API keys.
    

### 4. Advanced XXE Attack Vectors

#### A. Remote Code Execution (RCE)

- **PHP Expect Module:** Uses `expect://` (e.g., `expect://id`) to execute system commands directly. (Rare on modern servers as `expect` is disabled by default).
    
- **Web Shell Staging:** Using `expect://` to run `curl` or `wget` commands that pull a web shell from a remote server onto the target server.
    

#### B. Server-Side Request Forgery (SSRF)

- XXE entities can reference internal IP addresses/ports to map internal networks or interact with restricted internal endpoints.
    

#### C. Denial of Service (Billion Laughs Attack)

- Uses nested, exponentially expanding entity references (e.g., `a0` expands into `a1`, `a1` into `a2`, etc.) to exhaust server memory/CPU.
    
- _Note:_ Modern web servers and parsers generally prevent entity self-referencing loops by default.