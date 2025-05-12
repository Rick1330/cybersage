# CyberSage: AI-Powered Cybersecurity Co-Pilot

[![Build Status](https://img.shields.io/github/actions/workflow/status/rick1330/cybersage/.github/workflows/ci-main.yml?branch=main&style=flat-square)](https://github.com/rick1330/cybersage/actions/workflows/ci-main.yml)
[![Code Coverage](https://img.shields.io/codecov/c/github/rick1330/cybersage?style=flat-square)](https://codecov.io/gh/rick1330/cybersage)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue?style=flat-square)](./LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/rick1330/cybersage?style=flat-square)](https://github.com/rick1330/cybersage/issues)
[![GitHub Stars](https://img.shields.io/github/stars/rick1330/cybersage?style=flat-square)](https://github.com/rick1330/cybersage/stargazers)
<!-- Add other relevant badges like version, chat, etc. -->

**CyberSage integrates Large Language Models (LLMs) with standard cybersecurity tools and workflows to automate, assist, and enhance security operations.**

---

## Table of Contents

1.  [Overview](#1-overview)
2.  [Features](#2-features)
3.  [Directory Architecture](#3-directory-architecture)
4.  [Visual Architecture](#4-visual-architecture)
5.  [Quick Start](#5-quick-start)
6.  [Usage](#6-usage)
7.  [Contributing](#7-contributing)
8.  [Documentation](#8-documentation)
9.  [Roadmap](#9-roadmap)
10. [License](#10-license)
11. [Credits & Acknowledgements](#11-credits--acknowledgements)

---

## 1. Overview

CyberSage is an advanced platform designed to augment cybersecurity professionals by leveraging the power of Artificial Intelligence. It acts as a co-pilot, streamlining security tasks, automating repetitive analysis, and providing intelligent insights by combining LLM reasoning capabilities with the practical execution of security tools.

Built with a modular, AI-first architecture, CyberSage aims to:

*   **Automate** routine security tasks like reconnaissance and log analysis.
*   **Assist** analysts during complex investigations and incident response.
*   **Enhance** security posture through proactive threat identification and workflow orchestration.
*   **Empower** teams with a flexible framework for integrating custom tools and knowledge.

---

## 2. Features

CyberSage offers a range of features designed for modern security operations:

**AI & Agents:**

*   **🤖 AI Agent Framework:** Leverages LLM-powered agents (based on LangChain) capable of planning, reasoning, and executing complex tasks.
*   **🧠 Contextual Memory:** Persistent memory (Redis backend) allows agents to maintain context across long-running tasks and conversations.
*   **💡 Prompt Engineering:** Optimized prompts tailored for cybersecurity tasks ensure accurate and relevant AI responses.
*   **🔗 Chain & Workflow Building:** Tools for constructing sequences of LLM calls and tool executions (`core/chain_builder.py`).

**Tooling & Execution:**

*   **🛠️ Integrated Security Tools:** Secure wrappers for standard tools like Nmap, Shodan, WHOIS, VirusTotal, etc. (`tools/`).
*   **🏃 Sandboxed Runtimes:** Dedicated execution environments for different tool categories (network scanning, forensics) enhance security and resource management (`tool-execution-runtimes/`).
*   **🔌 Extensible Tooling:** SDKs and clear interfaces for adding custom tools and plugins (`plugins/sdk/`).

**Workflows & Orchestration:**

*   **⚙️ Workflow Engine:** A dedicated service (`core-services/workflow-engine-svc/`) orchestrates complex, multi-step security workflows defined in structured formats (`workflows/`).
*   **🔄 Background Task Processing:** Uses Celery (`tasks/`) for handling asynchronous jobs and scheduling recurring tasks (e.g., periodic scans, report generation).

**Data Handling & Knowledge:**

*   **💾 Vector Store Integration:** Utilizes vector databases (e.g., pgvector) for Retrieval-Augmented Generation (RAG), allowing AI to access relevant security knowledge (`services/vectorstore_service.py`).
*   **📜 Structured Logging:** Centralized and structured logging service (`services/logging_service.py`) with support for different levels and outputs (file, console, potentially remote).
*   **🔍 Audit Logging:** Dedicated service (`core-services/audit-log-svc/`) for tracking significant actions and events within the platform.

**Interfaces & Platform:**

*   **💻 Command Line Interface (CLI):** Provides quick access to core functionalities for scripting and terminal users (`interfaces/cli.py`).
*   **🌐 REST API:** A comprehensive FastAPI backend (`interfaces/api/`) exposed via an API Gateway (`api-gateway/`) for programmatic interaction.
*   **🖥️ Web Interface:** A user-friendly UI (`ui-web/`) for managing agents, building workflows, viewing results, and chat interaction.
*   **📱 Mobile Interface:** Companion mobile app (`ui-mobile/`) for on-the-go access (details TBD).
*   **🧩 Microservices Architecture:** Scalable and resilient design with distinct core and platform services.
*   **☁️ Infrastructure as Code (IaC):** Terraform and Helm configurations (`infra/`) for repeatable deployments across environments.
*   **🤝 Shared Components:** Common libraries, data contracts, and type definitions (`shared/`) ensure consistency across the platform.

---

## 3. Directory Architecture

The project follows a modular structure:

*   `rick1330-cybersage/`
    *   `.github/`: CI/CD workflows, issue templates
    *   `api-gateway/`: NestJS API Gateway service
    *   `configs/`: Application configuration files (settings, logging)
    *   `core/`: Core AI agent logic, prompts, context management
    *   `core-services/`: Specialized backend services (Workflow Engine, Audit Log)
    *   `docs/`: Detailed documentation (Architecture, Guides)
    *   `infra/`: Infrastructure as Code (Terraform, Helm)
    *   `interfaces/`: Backend API (FastAPI) and CLI definitions
    *   `legal/`: Legal documents (License, Privacy Policy)
    *   `platform-services/`: Cross-cutting platform services (Identity, Config)
    *   `plugins/`: SDKs for extending CyberSage
    *   `scripts/`: Utility and operational scripts
    *   `services/`: Foundational backend services (OpenAI, DBs, Logging)
    *   `shared/`: Shared code, schemas, types across services
    *   `tasks/`: Celery background tasks definitions
    *   `tests/`: Automated tests (unit, integration, e2e, etc.)
    *   `tool-execution-runtimes/`: Sandboxed environments for tool execution
    *   `tools/`: Wrappers for external cybersecurity tools
    *   `ui-mobile/`: Mobile application source
    *   `ui-web/`: Web application source
    *   `workflows/`: Definitions for automated workflows
    *   `.env.template`: Environment variable template
    *   `Dockerfile`: Production Docker build definition
    *   `docker-compose.yml`: Docker Compose for local development
    *   `requirements.txt`: Python dependencies
    *   `README.md`: This file

---



## 4. Visual Architecture

CyberSage employs a microservices architecture where user interfaces interact with backend services via an API Gateway. The core logic orchestrates AI agents, tools, and data services to perform cybersecurity tasks.

*(A detailed diagram can be found in `/docs/architecture.md`. The basic flow is: User Interface -> API Gateway -> Backend API -> Core Logic / Services -> Data Stores / External Tools / LLM API)*

---

## 5. Quick Start

Get CyberSage running locally for development or testing.

**Prerequisites:**

*   Git
*   Python 3.9+
*   Docker & Docker Compose
*   Required API Keys (OpenAI minimum, others optional) - see `README.md#prerequisites` for details.

**Steps:**

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/rick1330/cybersage.git
    cd cybersage
    ```

2.  **Set up Python Environment & Install Dependencies:**
    ```bash
    # Create and activate a virtual environment (recommended)
    python -m venv venv
    source venv/bin/activate # Or .\venv\Scripts\activate on Windows

    # Install dependencies
    pip install -r requirements.txt
    ```

3.  **Configure Environment Variables:**
    ```bash
    # Copy the template
    cp .env.template .env

    # Edit the .env file with your editor and add your API keys/secrets
    # Example: nano .env
    ```
    *Minimum required:*
    ```dotenv
    OPENAI_API_KEY=<YOUR_OPENAI_KEY_HERE>
    JWT_SECRET=<generate_a_strong_random_secret>
    ENCRYPTION_KEY=<generate_a_different_strong_random_secret>
    ```
    *(Fill in other keys like `SHODAN_API_KEY`, `VIRUSTOTAL_API_KEY` for full tool functionality)*

4.  **Run Services with Docker Compose:**
    ```bash
    docker-compose up --build -d
    ```
    *(This starts the API, Redis, Vector DB, etc.)*

5.  **First Run Example (CLI):**
    ```bash
    # Ensure venv is active
    python interfaces/cli.py investigate --query "WHOIS lookup for google.com" --tools whois
    ```

---

## 6. Usage

Interact with CyberSage via its different interfaces:

*   **CLI (`interfaces/cli.py`):** For quick tasks and scripting.
    ```bash
    # Example: Basic Nmap scan
    python interfaces/cli.py scan --target scanme.nmap.org --scan-type basic
    ```
*   **REST API (`interfaces/api/` via Gateway):** For programmatic integration. Default local URL: `http://localhost:8000`.
    ```bash
    # Example: Execute a task via API (replace <YOUR_JWT>)
    curl -X POST http://localhost:8000/api/v1/tasks \
         -H "Content-Type: application/json" \
         -H "Authorization: Bearer <YOUR_JWT>" \
         -d '{ "task_id": "api-scan-01", "agent_id": "default_scanner", "task": "Scan 192.168.1.1 for open web ports", "parameters": {"target": "192.168.1.1", "ports": "80,443,8080"} }'
    ```
*   **Web UI (`ui-web/`):** Graphical interface for workflows, agents, and results. Access via its configured URL (e.g., `http://localhost:3000`).

**Example Use Cases:**

*   Automated reconnaissance on a target domain.
*   Vulnerability scanning and analysis.
*   Log summarization and anomaly detection.
*   Threat intelligence gathering on IPs, domains, or hashes.
*   Guided incident response steps.

---

## 7. Contributing

We welcome contributions! Please read our [CONTRIBUTING.md](./CONTRIBUTING.md) guide to understand our development process, branching model (`develop` branch is primary), coding standards, and how to submit pull requests.

*   Report bugs or request features via [GitHub Issues](https://github.com/rick1330/cybersage/issues).
*   Propose changes via Pull Requests against the `develop` branch.

---

## 8. Documentation

Detailed documentation beyond this README can be found in the `/docs` directory, including:

*   `/docs/architecture.md`: In-depth architecture diagrams and explanations.
*   `/docs/security_model.md`: Threat model and security considerations.
*   `/docs/developer_guide/`: Guides for developing specific components.
*   API Reference (potentially generated from OpenAPI spec).

*(Links to hosted documentation can be added here if available)*

---

## 9. Roadmap

This is a high-level overview of planned features and improvements (subject to change):

*   **More Tool Integrations:** Metasploit, OSINT tools, Cloud security scanners.
*   **Advanced Workflow Capabilities:** Conditional logic, parallel execution, human-in-the-loop steps.
*   **Enhanced RAG:** Fine-tuning embeddings, integrating more diverse knowledge sources.
*   **Improved UI/UX:** Visual workflow editor enhancements, better results visualization.
*   **Multi-LLM Support:** Allow configuration of different LLM providers/models.
*   **Reporting Module:** Automated generation of security assessment reports.
*   **Compliance Workflows:** Pre-defined workflows for common compliance checks (e.g., CIS Benchmarks).
*   **Performance Optimizations:** Caching strategies, asynchronous processing improvements.

---

## 10. License

This project is licensed under the **Apache License 2.0**. See the [LICENSE](./LICENSE) file for the full license text.

---

## 11. Credits & Acknowledgements

CyberSage builds upon the capabilities of many fantastic open-source projects and services, including:

*   [LangChain](https://github.com/langchain-ai/langchain) for the core LLM agent and chain framework.
*   [FastAPI](https://fastapi.tiangolo.com/) for the Python backend API.
*   [NestJS](https://nestjs.com/) for the API Gateway.
*   [OpenAI](https://openai.com/) for the underlying Large Language Models.
*   [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/) for containerization.
*   [Redis](https://redis.io/) for caching and message brokering.
*   [PostgreSQL](https://www.postgresql.org/) & [pgvector](https://github.com/pgvector/pgvector) for vector storage.
*   [Celery](https://docs.celeryq.dev/) for background tasks.
*   Inspiration from projects like AutoGPT and BabyAGI.
*   The developers of the integrated security tools (Nmap, Shodan, etc.).

We thank the open-source community and all contributors.
