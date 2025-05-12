# Security Policy for CyberSage

The CyberSage team takes security seriously. We appreciate your efforts to responsibly disclose your findings, and we will make every effort to acknowledge your contributions.

## Table of Contents

1.  [Reporting a Vulnerability](#1-reporting-a-vulnerability)
2.  [Supported Versions](#2-supported-versions)
3.  [Threat Model Overview](#3-threat-model-overview)
4.  [Security Mitigations & Practices](#4-security-mitigations--practices)

---

## 1. Reporting a Vulnerability

**DO NOT report security vulnerabilities through public GitHub issues.**

If you believe you have found a security vulnerability in CyberSage, please report it to us privately. This gives us time to address the issue before it becomes public knowledge.

**How to Report:**

1.  **Email:** Send an email detailing the vulnerability to:
    `Rickriener8@gmail.com`

2.  **Encryption (Optional but Recommended):** For sensitive reports, you can encrypt your email using our PGP key (details below). *Note: Key details are placeholders and will be updated.*
    *   **PGP Key Fingerprint:** `[<<< PGP KEY FINGERPRINT WILL BE ADDED HERE >>>]`
    *   **PGP Public Key:**
        ```pgp
        -----BEGIN PGP PUBLIC KEY BLOCK-----

        [<<< PGP PUBLIC KEY BLOCK WILL BE ADDED HERE >>>]
        (This block will contain the ASCII-armored public key once generated)

        -----END PGP PUBLIC KEY BLOCK-----
        ```

3.  **Details to Include:** Please provide as much information as possible to help us understand and reproduce the issue:
    *   Type of vulnerability (e.g., XSS, SQL Injection, RCE, Authentication Bypass).
    *   Detailed steps to reproduce the vulnerability.
    *   Affected component(s) or service(s) (e.g., API, Web UI, Nmap tool wrapper).
    *   Potential impact of the vulnerability.
    *   Any proof-of-concept code or screenshots.
    *   Your name/handle for acknowledgement (optional).

**Our Commitment:**

*   We will strive to acknowledge receipt of your report within 48 business hours.
*   We will investigate the report promptly and work towards a fix.
*   We will maintain communication with you regarding the status of the vulnerability.
*   We will publicly acknowledge your contribution (unless you prefer to remain anonymous) once the vulnerability is fixed and disclosed, if appropriate.

We ask that you follow responsible disclosure practices and refrain from publicly disclosing the vulnerability until we have had a reasonable amount of time to address it.

---

## 2. Supported Versions

Security updates are typically applied only to the most recent stable release branch (`main`) and potentially the active development branch (`develop`). We encourage users to stay updated with the latest stable version of CyberSage to benefit from security patches.

| Version | Supported          |
| :------ | :----------------- |
| `>=1.0.0` | :white_check_mark: |
| `<1.0.0` | :x:                |
| `develop` | Best Effort        |

*(Adjust this table as the project matures and has actual version releases)*

---

## 3. Threat Model Overview

CyberSage interacts with potentially sensitive data, executes external tools, and relies on AI models. Key areas considered in our threat model include:

*   **Input Injection:** Malicious inputs provided to the API, CLI, or UI intended to manipulate AI prompts, tool commands, or database queries (e.g., prompt injection, command injection).
*   **Tool Execution Security:** Vulnerabilities in the wrappers or runtimes for external tools (e.g., Nmap, Shodan) leading to unintended system access or information disclosure. Escape vulnerabilities from sandboxed environments.
*   **Authentication & Authorization:** Bypassing authentication mechanisms or escalating privileges within the platform's services (API Gateway, Backend API, Platform Services).
*   **Data Security:** Unauthorized access to or leakage of sensitive data stored by the platform (e.g., API keys in configuration, agent memory in Redis, vector embeddings, audit logs).
*   **AI Model Security:** Adversarial attacks against the LLM, data poisoning of the vector store, or extraction of sensitive information through model interaction.
*   **Dependency Vulnerabilities:** Security flaws in third-party libraries or base Docker images used by the project.
*   **Infrastructure Security:** Misconfigurations in cloud resources (managed via Terraform) or Kubernetes deployments (managed via Helm).
*   **Denial of Service (DoS):** Overloading services through excessive API requests, complex AI tasks, or resource-intensive tool executions.

*(A more detailed threat model may reside in `/docs/security_model.md`)*

---

## 4. Security Mitigations & Practices

We employ various strategies to mitigate security risks:

*   **Input Sanitization:** Inputs to tools and potentially sensitive API endpoints are validated and sanitized.
*   **Tool Sandboxing:** Exploring the use of dedicated, potentially containerized runtimes (`tool-execution-runtimes/`) to isolate tool execution. Timeouts and resource limits are applied.
*   **Secure Authentication:** Utilizing standard authentication protocols (e.g., JWT) via dedicated identity services (`platform-services/identity-svc/`).
*   **Authorization Checks:** Implementing role-based or permission-based access control within services.
*   **Secrets Management:** Using environment variables (`.env`) and potentially integrating with dedicated secrets management solutions (like HashiCorp Vault or cloud provider secrets managers) instead of hardcoding credentials. `.gitleaks` and `.git-secrets` are used to prevent accidental commits.
*   **Dependency Scanning:** Using tools like Dependabot (`.github/dependabot.yml`) and potentially `pip-audit` or `npm audit` to identify vulnerable dependencies.
*   **Static Analysis (SAST):** Using tools like CodeQL (`.github/workflows/codeql-analysis.yml`) to find potential security flaws in the codebase.
*   **Dynamic Analysis (DAST/IAST):** Incorporating DAST/IAST scanning in CI/CD pipelines (`.github/workflows/security-dast-iast.yml`).
*   **Rate Limiting:** Implementing rate limiting at the API Gateway or backend API level to prevent abuse.
*   **HTTPS Enforcement:** Ensuring encrypted communication for web interfaces and APIs in production deployments.
*   **Infrastructure Security:** Following best practices for IaC security (e.g., least privilege IAM roles, secure network configurations).
*   **Regular Audits & Testing:** Performing periodic security reviews and potentially penetration testing (`tests/security/`).
*   **Responsible AI Practices:** Implementing safeguards against prompt injection where possible and being mindful of potential biases or harmful content generation (though primary focus is on tool execution security).

We are continuously working to improve the security posture of CyberSage.
