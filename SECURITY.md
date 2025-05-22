# Security Policy for CyberSage

The CyberSage team takes security seriously. We appreciate your efforts to responsibly disclose your findings, and we will make every effort to acknowledge your contributions.

## Table of Contents

1.  [Reporting a Vulnerability](#1-reporting-a-vulnerability)
2.  [Supported Versions](#2-supported-versions)
3.  [Threat Model Overview & Security Architecture](#3-threat-model-overview--security-architecture)
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

## 3. Threat Model Overview & Security Architecture

CyberSage interacts with potentially sensitive data, executes external tools, and relies on AI models. A comprehensive discussion of our threat model, security architecture, data security practices, and mitigations is detailed in our main security documentation:

**➡️ [CyberSage Security Model & Architecture](/docs/src/security/README.md)**

Key areas considered include:
*   Input Injection (Prompt Injection, Command Injection)
*   Tool Execution Security & Sandbox Escapes
*   Authentication & Authorization Bypass
*   Data Security & Leakage (at rest, in transit, via LLMs)
*   AI Model Security (Adversarial Attacks, Data Poisoning)
*   Dependency Vulnerabilities
*   Infrastructure Security
*   Denial of Service

## 4. Security Mitigations & Practices

Our strategies for mitigating security risks are detailed in the **[CyberSage Security Model & Architecture](/docs/src/security/README.md)** document. These include, but are not limited to:
*   Input Sanitization & Validation
*   Tool Sandboxing & Secure Runtimes
*   Strong Authentication & Authorization (JWT, RBAC)
*   Secrets Management & Encryption
*   Dependency Scanning & SAST/DAST
*   Rate Limiting & HTTPS Enforcement
*   Secure Infrastructure (IaC)
*   Regular Audits & Testing

We are continuously working to improve the security posture of CyberSage.
```
