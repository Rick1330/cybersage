# CyberSage Security Model & Architecture

This document provides a detailed overview of the security architecture, threat model, and secure development practices for the CyberSage platform. It expands upon the general security policy outlined in the main `SECURITY.md` file.

## 1. Security Principles

*   **Defense in Depth:** Employ multiple layers of security controls.
*   **Least Privilege:** Grant only necessary permissions to users and services.
*   **Secure by Design & Default:** Integrate security into the entire development lifecycle and configure systems securely by default.
*   **Secure Communication:** Encrypt data in transit and ensure authenticated communication channels.
*   **Data Protection:** Classify and protect sensitive data throughout its lifecycle.
*   **Regular Audits & Monitoring:** Continuously monitor for and respond to security events.
*   **Vulnerability Management:** Proactively identify and remediate vulnerabilities.

## 2. Detailed Threat Model

This section expands on the [Threat Model Overview in SECURITY.md](/SECURITY.md#3-threat-model-overview).

### Key Assets
*   User credentials and API keys.
*   Sensitive data processed by agents (e.g., scan results, target information).
*   LLM models and prompts.
*   Agent memory and context data (Redis).
*   Vector store embeddings and source documents (PostgreSQL/pgvector).
*   Configuration data, including service credentials.
*   Source code and intellectual property.
*   Audit logs.

### Threat Actors
*   External attackers (script kiddies, organized crime, state-sponsored).
*   Malicious insiders (disgruntled employees, compromised accounts).
*   Vulnerabilities in third-party dependencies or tools.

### Attack Vectors & Mitigations

#### a. Input Injection
*   **Vector:** Malicious inputs to API, CLI, UI, or directly to LLMs (Prompt Injection). Command injection via tool parameters.
*   **Mitigation:**
    *   Strict input validation and sanitization at API Gateway and backend services (using Pydantic models as mentioned in `tools/SECURITY_GUIDELINES.md`).
    *   Parameterized queries for database interactions.
    *   Contextual output encoding.
    *   Specific defenses against prompt injection (e.g., instruction filtering, output parsing, using separate privileged LLMs for sensitive operations - *[Placeholder: Detail specific prompt injection defenses if implemented or planned]*).
    *   Secure subprocess execution for tools as per `tools/SECURITY_GUIDELINES.md` (no `shell=True`, argument lists).
    *   Regular SAST/DAST scanning (`.github/workflows/codeql-analysis.yml`, `.github/workflows/security-dast-iast.yml`).

#### b. Tool Execution Security
*   **Vector:** Vulnerabilities in wrapped tools; sandbox escapes from `tool-execution-runtimes/`.
*   **Mitigation:**
    *   Sandboxed runtimes (Docker-based isolation is implied).
    *   Strict adherence to `tools/SECURITY_GUIDELINES.md` for all tool wrappers.
    *   Principle of least privilege for tool execution environments.
    *   Regular updates and patching of underlying tools and runtime environments.
    *   *[Placeholder: Detail specific sandbox configurations and inter-runtime communication controls if available.]*

#### c. Authentication & Authorization Bypass
*   **Vector:** Weak credentials, session hijacking, privilege escalation, insecure API endpoints.
*   **Mitigation:**
    *   Strong password policies and secure credential storage (delegated to `platform-services/identity-svc/`).
    *   JWT-based authentication for APIs, managed by API Gateway and Identity Service.
    *   Role-Based Access Control (RBAC) for API endpoints and service interactions - *[Placeholder: Detail RBAC model if defined, e.g., roles like 'admin', 'user', 'agent_executor']*.
    *   Secure inter-service communication (e.g., mTLS, token-based) - *[Placeholder: Specify inter-service auth mechanism if defined]*.
    *   Regular security testing of authentication mechanisms.

#### d. Data Security & Leakage
*   **Vector:** Unauthorized access to data at rest or in transit; leakage of sensitive data via LLM outputs or logs.
*   **Mitigation:** See [Section 4: Data Security](#4-data-security).
    *   Minimize collection and retention of sensitive data.
    *   Redact sensitive information from LLM prompts and outputs where possible.
    *   Secure logging practices (avoid logging sensitive data). Audit logging via `core-services/audit-log-svc/`.

#### e. AI Model Security
*   **Vector:** Adversarial attacks against LLMs, model theft, data poisoning of RAG vector stores, extraction of sensitive information via model queries.
*   **Mitigation:**
    *   Access controls for LLM APIs and models.
    *   Monitoring of LLM usage for anomalous activity.
    *   For RAG: Careful curation of data sources for vector stores. Input validation before querying vector stores.
    *   Research and implement defenses against known adversarial attacks as they become relevant and practical.
    *   *[Placeholder: Detail any specific model fine-tuning security measures or output filtering for sensitive content.]*

#### f. Dependency Vulnerabilities
*   **Vector:** Exploitation of known vulnerabilities in third-party libraries or base Docker images.
*   **Mitigation:**
    *   Automated dependency scanning (Dependabot in `.github/dependabot.yml`, `pip-audit`, `npm audit`).
    *   Regularly update dependencies and base images.
    *   Use minimal base images for containers.

#### g. Infrastructure Security
*   **Vector:** Misconfigurations in cloud resources, Kubernetes, or network settings.
*   **Mitigation:**
    *   Infrastructure as Code (Terraform, Helm) for repeatable and auditable setups.
    *   Least privilege IAM roles for cloud resources.
    *   Secure network configurations (VPCs, subnets, firewalls).
    *   Regular infrastructure security audits.

#### h. Denial of Service (DoS/DDoS)
*   **Vector:** Overloading services with excessive requests or resource-intensive tasks.
*   **Mitigation:**
    *   Rate limiting at the API Gateway and backend services.
    *   Timeouts and resource limits for tool executions and AI tasks.
    *   Scalable infrastructure design.
    *   Use of WAF/CDN for DDoS protection in production - *[Placeholder: Specify if WAF/CDN is part of the architecture]*.

## 3. Trust Boundaries

*   **User <> Platform:** Users interact via UIs or CLI, authenticating at the API Gateway.
*   **API Gateway <> Backend Services:** API Gateway acts as a reverse proxy and policy enforcement point. Assumes secure internal network.
*   **Internal Services <> Internal Services:** Services within the Kubernetes cluster. Communication should be secured (e.g., mTLS).
*   **Platform <> LLM APIs (OpenAI):** External communication, relies on HTTPS and API key security.
*   **Platform <> External Tools (Shodan, VirusTotal):** External communication, relies on HTTPS and API key security.
*   **Tool Runtimes <> Host System/Network:** Sandboxed environments designed to limit access. Network policies should restrict egress.

## 4. Data Security

### 4.1. Data Classification
*   **Highly Sensitive:** User credentials, API keys for external services, LLM API keys, sensitive configuration secrets.
*   **Sensitive:** User inputs/queries, agent memory content, detailed scan results, PII in user data.
*   **Operational:** Non-sensitive logs, metrics, aggregated usage data.
*   **Public:** Open-source code, public documentation.

### 4.2. Data In Transit
*   **External:** All communication with user browsers/clients, external LLM APIs, and third-party tools MUST use HTTPS/TLS.
*   **Internal:** Communication between services (e.g., API Gateway to backend, service-to-service) SHOULD be encrypted (e.g., using mTLS within the Kubernetes cluster). *[Placeholder: Confirm current internal encryption status.]*

### 4.3. Data At Rest
*   **Secrets (API Keys, Credentials):**
    *   Managed via environment variables injected into containers (from Kubernetes Secrets or similar).
    *   Use of `.env` files for local development, not for production.
    *   Consider integration with a dedicated secrets manager (e.g., HashiCorp Vault, cloud provider KMS) for production. *[Placeholder: Specify current production secrets management.]*
    *   GitGuardian/TruffleHog (`.gitleaks.toml`, `.git-secrets/`) used to prevent accidental secret commits.
*   **Agent Memory (Redis):**
    *   Redis itself may not encrypt data at rest by default. Consider Redis ACLs and network isolation.
    *   If highly sensitive data is stored, consider application-level encryption before storing in Redis. *[Placeholder: Specify if application-level encryption for memory is used.]*
*   **Vector Store (PostgreSQL/pgvector):**
    *   Utilize PostgreSQL's built-in security features (authentication, authorization).
    *   Consider Transparent Data Encryption (TDE) if offered by the cloud provider, or application-level encryption for sensitive documents before embedding. *[Placeholder: Specify encryption for vector store data.]*
*   **Audit Logs:** Protected by service-level authentication and authorization.
*   **Databases (General):** Use strong credentials, network isolation, and consider encryption at rest features provided by the database or cloud provider.

### 4.4. Key Management
*   *[Placeholder: Describe how cryptographic keys (e.g., for JWT signing, data encryption) are generated, stored, rotated, and accessed securely. If using a KMS, describe its usage.]*

### 4.5. Data Retention & Disposal
*   *[Placeholder: Define data retention policies for different data types (e.g., logs, agent memory, user data). Describe how data is securely disposed of when no longer needed.]*

## 5. Authentication and Authorization (AuthN/AuthZ)

*   **User Authentication:** Primarily handled by `platform-services/identity-svc/` using JWTs. Supports [mention supported methods, e.g., username/password, OAuth with providers].
*   **Service Authentication:** For inter-service communication, [mention mechanism, e.g., mTLS, service accounts with JWTs].
*   **API Authorization:**
    *   API Gateway enforces initial auth checks.
    *   Backend services implement fine-grained authorization based on user roles and permissions.
    *   *[Placeholder: Link to or describe the RBAC model and permissions structure in more detail.]*
*   **Tool Authorization:** Agents are configured with specific tools. Access to tool execution runtimes is controlled.

## 6. Secure Development Practices

*   **Code Reviews:** All code changes reviewed for security implications before merging.
*   **Static Analysis (SAST):** CodeQL integrated into CI/CD (`.github/workflows/codeql-analysis.yml`).
*   **Dynamic Analysis (DAST/IAST):** Scans integrated into CI/CD (`.github/workflows/security-dast-iast.yml`).
*   **Dependency Management:** Dependabot for automated updates (`.github/dependabot.yml`). Regular review of dependencies.
*   **Secret Scanning:** GitGuardian/TruffleHog configured (`.gitleaks.toml`, `.git-secrets`).
*   **Security Guidelines:** Adherence to `tools/SECURITY_GUIDELINES.md` for tool development.
*   **Developer Training:** Developers are encouraged to stay updated on secure coding practices.
*   **Incident Response Plan:** *[Placeholder: Briefly outline or link to an incident response plan if one exists.]*

## 7. Secure Deployment

*   Refer to `docs/src/operations_guide/README.md` for secure deployment and operational practices.
*   Use of IaC (Terraform, Helm) promotes auditable and repeatable secure infrastructure.
*   Regular patching and updating of production systems.

---

*This document is a living document and will be updated as the CyberSage platform evolves.*
```
