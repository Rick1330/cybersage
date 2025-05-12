# CyberSage Tool Registry

This document serves as a catalog of the built-in tools available for use by CyberSage agents. Agents leverage these tools to interact with external systems, APIs, and data sources to perform cybersecurity tasks.

## Overview

Each tool listed here adheres to the `BaseTool` interface defined in `/tools/base_tool.py` (or LangChain's `BaseTool`). The `description` provided for each tool is crucial, as it's used by the LLM agent to understand the tool's capabilities and determine when and how to use it effectively. Input parameters are often validated using Pydantic schemas (`args_schema`).

*Note: This registry is primarily for documentation purposes. The actual mechanism for making tools available to agents might involve dynamic loading or explicit registration within the `AgentManager` or a dedicated tool service.*

---

## Built-in Tool Catalog

*(This list should be updated as new tools are added or existing ones are modified.)*

---

### 1. Nmap Network Scanner (`nmap_tool`)

*   **Class:** `NmapTool` (`tools/nmap_tool.py`)
*   **Description:** Executes Nmap scans against specified targets to discover hosts, open ports, services, and operating systems. Useful for network reconnaissance and vulnerability assessment preparation. Handles various scan types and outputs results. *Security Note: Executes external commands; requires careful input sanitization and potentially sandboxing.*
*   **Input Parameters (`args_schema`):**
    *   `target` (str, required): The IP address, hostname, or network range to scan (e.g., `192.168.1.1`, `scanme.nmap.org`, `10.0.0.0/24`).
    *   `ports` (str, optional): Specific ports or port ranges to scan (e.g., `80,443`, `1-1024`, `T:80,U:53`). Defaults to Nmap's default port list if not specified.
    *   `scan_type` (str, optional): Defines the type of Nmap scan. Common values:
        *   `basic`: Simple SYN scan for open ports (e.g., `-sS`).
        *   `service`: Includes service and version detection (e.g., `-sV`).
        *   `os`: Includes OS detection (e.g., `-O`). Requires root/admin privileges usually.
        *   `full`: Comprehensive scan including service, OS, and default scripts (e.g., `-A`).
        *   `custom`: Allows specifying raw Nmap arguments via `custom_args`. Defaults to `basic`.
    *   `custom_args` (str, optional): Raw Nmap command-line arguments to append or use (used when `scan_type` is `custom` or for advanced tuning). Use with extreme caution due to injection risks.
*   **Output:** String containing the parsed Nmap scan results (often summarized text or potentially structured JSON depending on implementation).
*   **Example Agent Task:** `"Run a service detection scan on 10.1.1.5 focusing on ports 80, 443, and 8080."`
*   **Example Direct Call (Conceptual):** `nmap_tool.run(target="scanme.nmap.org", scan_type="service", ports="80,443")`

---

### 2. Shodan Search Engine (`shodan_tool`)

*   **Class:** `ShodanTool` (`tools/shodan_tool.py`)
*   **Description:** Queries the Shodan API to find internet-connected devices based on various filters (IP, hostname, port, OS, service banners, etc.). Useful for external reconnaissance and discovering exposed assets. Requires a Shodan API key configured in the environment.
*   **Input Parameters (`args_schema`):**
    *   `query` (str, required): The Shodan search query string (e.g., `hostname:example.com`, `port:22 country:US`, `org:"Google LLC"`).
    *   `query_type` (str, optional): Specifies the type of Shodan query. Common values:
        *   `host`: Search for information about a specific IP address (`/shodan/host/{ip}`). Requires `query` to be an IP.
        *   `search`: Perform a general banner search (`/shodan/search`). `query` is the search filter.
        *   *(Other types like `search_count`, `ports` might be added)*. Defaults to `search`.
    *   `limit` (int, optional): Maximum number of results to return for `search` queries. Defaults to a reasonable value (e.g., 10).
*   **Output:** String containing summarized results from the Shodan API (e.g., list of IPs, host details, open ports found).
*   **Example Agent Task:** `"Find devices associated with example.com using Shodan."`
*   **Example Direct Call (Conceptual):** `shodan_tool.run(query="org:\"Example Corp\"", query_type="search", limit=5)`

---

### 3. WHOIS Lookup (`whois_tool`)

*   **Class:** `WhoisTool` (`tools/whois_tool.py`)
*   **Description:** Performs a WHOIS lookup for a given domain name or IP address to retrieve registration details, contact information, and related network information. Useful for reconnaissance and ownership investigation.
*   **Input Parameters (`args_schema`):**
    *   `query` (str, required): The domain name (e.g., `google.com`) or IP address (e.g., `8.8.8.8`) to look up.
*   **Output:** String containing the raw or parsed WHOIS record information.
*   **Example Agent Task:** `"Get the WHOIS registration details for cybersage.example.com."`
*   **Example Direct Call (Conceptual):** `whois_tool.run(query="example.com")`

---

### 4. VirusTotal Analysis (`virustotal_tool`)

*   **Class:** `VirusTotalTool` (`tools/virustotal_tool.py`)
*   **Description:** Queries the VirusTotal API to check the reputation of files (hashes), URLs, domains, or IP addresses against multiple antivirus engines and blocklists. Useful for malware analysis and threat intelligence. Requires a VirusTotal API key configured in the environment.
*   **Input Parameters (`args_schema`):**
    *   `resource` (str, required): The resource to query (e.g., a file hash MD5/SHA1/SHA256, URL, domain name, or IP address).
    *   `resource_type` (str, optional): Specifies the type of resource being queried. Common values:
        *   `hash`: File hash.
        *   `url`: A URL.
        *   `domain`: A domain name.
        *   `ip_address`: An IP address.
        *   If not provided, the tool might attempt to infer the type.
*   **Output:** String summarizing the VirusTotal report (e.g., detection ratio for hashes/URLs, resolutions/passive DNS for domains/IPs, key findings).
*   **Example Agent Task:** `"Check the VirusTotal reputation for the SHA256 hash <hash_value>."` or `"What does VirusTotal know about the domain malicious.example?"`
*   **Example Direct Call (Conceptual):** `virustotal_tool.run(resource="<sha256_hash_here>", resource_type="hash")`

---

*(we'll Add entries for other implemented tools like `dns_lookup_tool`, etc., following the same format next time)*

---
