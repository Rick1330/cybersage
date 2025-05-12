# Tools Layer: Security Guidelines

Developing tool wrappers for CyberSage requires careful attention to security. Since these tools often interact with external systems, execute commands, or handle potentially untrusted input (sometimes influenced by LLM outputs), they represent a significant attack surface. Adhering to these guidelines is crucial for maintaining the security and integrity of the CyberSage platform.

## Table of Contents

1.  [Input Sanitization & Validation](#1-input-sanitization--validation)
2.  [Preventing Command Injection](#2-preventing-command-injection)
3.  [Secure Subprocess Execution](#3-secure-subprocess-execution)
4.  [Sandboxing & Isolation](#4-sandboxing--isolation)
5.  [API Key & Credential Management](#5-api-key--credential-management)
6.  [Safe Output Handling & Parsing](#6-safe-output-handling--parsing)
7.  [Principle of Least Privilege](#7-principle-of-least-privilege)
8.  [Implement Dry-Run Mode](#8-implement-dry-run-mode)
9.  [Security Testing](#9-security-testing)
10. [Dependency Security](#10-dependency-security)

---

## 1. Input Sanitization & Validation

*   **Never Trust Input:** Treat all inputs to tool wrappers (arguments passed to `_run` or `_arun`) as potentially untrusted, especially if they originate from user queries or LLM outputs.
*   **Use Pydantic Schemas:** Define a strict `args_schema` (Pydantic model) for your tool's `BaseTool` implementation. This provides automatic type validation and structure enforcement.
*   **Validate Data Types:** Ensure inputs match expected types (e.g., integers for ports, valid IP address formats, specific string patterns).
*   **Sanitize String Inputs:**
    *   For inputs used in file paths, database queries, or API calls, use appropriate escaping mechanisms or parameterized queries.
    *   For inputs used in shell commands, see the [Command Injection Prevention](#2-preventing-command-injection) section.
*   **Character Whitelisting:** Where possible, restrict inputs to a known set of allowed characters (e.g., alphanumeric, specific punctuation for hostnames). Avoid blacklisting, as it's easy to miss dangerous characters.
*   **Check Lengths:** Impose reasonable length limits on inputs to prevent buffer overflows or denial-of-service attacks.

---

## 2. Preventing Command Injection

This is critical for tools that execute external command-line utilities (like Nmap, dig, etc.).

*   **Avoid `shell=True`:** **Never** use `subprocess.run(..., shell=True)` or similar constructs with unvalidated input. This is the most common way command injection occurs.
*   **Pass Arguments as a List:** When using `subprocess.run`, `subprocess.Popen`, or `asyncio.create_subprocess_exec`, pass the command and its arguments as a list of strings. The operating system will handle quoting and prevent shell interpretation of arguments.
    ```python
    # SAFE Example:
    import subprocess
    target_ip = "8.8.8.8" # Assume validated input
    command = ["nmap", "-sV", "--top-ports", "10", target_ip]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    ```
*   **Strict Argument Validation:** If you *must* construct parts of a command string dynamically (strongly discouraged), apply extremely strict validation and sanitization to the dynamic parts. Ensure they cannot contain shell metacharacters (`;`, `|`, `&`, `$`, `(`, `)`, ``` ` ```, `<`, `>`, etc.).
*   **Use Tool-Specific Libraries:** If a reliable Python library exists for interacting with the tool (e.g., `python-nmap`), prefer using it over raw subprocess calls, as the library often handles argument construction more safely.

---

## 3. Secure Subprocess Execution

*   **Timeouts:** Always specify a reasonable `timeout` parameter in `subprocess.run` or implement equivalent timeout logic for asynchronous subprocesses. This prevents tools from hanging indefinitely and causing resource exhaustion.
*   **Resource Limits:** If possible (especially within sandboxed environments), apply CPU and memory limits to subprocesses.
*   **Capture Output Securely:** Use `capture_output=True` and handle `stdout` and `stderr` appropriately. Avoid writing directly to shared files if possible.
*   **Check Return Codes:** Use `check=True` in `subprocess.run` to automatically raise an exception if the command returns a non-zero exit code, or manually check the `returncode` attribute. Handle tool errors gracefully.

---

## 4. Sandboxing & Isolation

For tools that pose a higher risk (e.g., network scanners, tools running complex external code):

*   **Leverage `tool-execution-runtimes/`:** Design tools to run within dedicated, isolated environments defined in this directory.
*   **Docker Containers:** Execute the tool inside a minimal Docker container with restricted network access and capabilities. The wrapper communicates with the container (e.g., via Docker API or volume mounts).
*   **Namespaces/Jails:** Utilize OS-level sandboxing features like Linux namespaces or BSD jails if appropriate for the deployment environment.
*   **Restricted User Accounts:** Run external processes as dedicated, low-privilege user accounts.

---

## 5. API Key & Credential Management

*   **Never Hardcode Secrets:** Do not embed API keys, passwords, or other credentials directly in the tool's source code.
*   **Use Environment Variables:** Load secrets from environment variables configured securely in the deployment environment (e.g., via `.env` loaded by the main application, Kubernetes secrets, cloud provider secret managers). Access them via `os.getenv()`.
*   **Configuration Service:** Leverage the platform's `ConfigurationService` if it provides secure credential handling.
*   **Limit Scope:** If possible, use API keys with the minimum required permissions for the tool's function.

---

## 6. Safe Output Handling & Parsing

*   **Parse Carefully:** Be cautious when parsing output from external tools, especially if the format is complex (e.g., XML, unstructured text). Use robust parsing libraries (e.g., `xml.etree.ElementTree`, `json`) and handle potential parsing errors (`try-except` blocks).
*   **Avoid Re-injection:** Ensure that data extracted from tool output is not insecurely used in subsequent commands, queries, or LLM prompts without appropriate sanitization or encoding.
*   **Validate Parsed Data:** Check that the parsed data conforms to expected structures and value ranges.

---

## 7. Principle of Least Privilege

*   Ensure the process running the CyberSage tool wrapper (and any subprocesses it spawns) operates with the minimum privileges necessary to perform its function.
*   Avoid running tools as `root` unless absolutely necessary (e.g., certain raw socket operations in Nmap), and if required, carefully isolate and restrict those specific operations.

---

## 8. Implement Dry-Run Mode

*   Where feasible, consider adding a `dry_run` parameter to your tool's execution methods.
*   In dry-run mode, the tool should log the command it *would* have executed or the API call it *would* have made, without actually performing the action. This is invaluable for debugging and understanding agent behavior without side effects.

---

## 9. Security Testing

*   **Unit Tests:** Write unit tests specifically targeting input validation and sanitization logic. Test edge cases and known malicious inputs (e.g., inputs containing shell metacharacters).
*   **Integration Tests:** Test the tool's interaction with external processes or APIs, including error handling and timeout behavior.
*   **Fuzzing:** Consider fuzz testing for tools that parse complex input or output formats.
*   **Manual Review:** Perform manual security code reviews focused on potential injection points and insecure handling of external interactions.

---

## 10. Dependency Security

*   Be mindful of the third-party libraries used within your tool wrapper.
*   Keep dependencies updated and monitor them for known vulnerabilities using tools like Dependabot or `pip-audit`.

---

By following these guidelines, developers can contribute powerful tools to CyberSage while minimizing the associated security risks.
