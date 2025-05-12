# CyberSage: Your AI-Powered Cybersecurity Co-Pilot

[![Build Status](https://img.shields.io/github/actions/workflow/status/rick1330/cybersage/.github/workflows/ci-main.yml?branch=main&style=flat-square)](https://github.com/rick1330/cybersage/actions/workflows/ci-main.yml)
[![Code Coverage](https://img.shields.io/codecov/c/github/rick1330/cybersage?style=flat-square)](https://codecov.io/gh/rick1330/cybersage)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue?style=flat-square)](./LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/rick1330/cybersage?style=flat-square)](https://github.com/rick1330/cybersage/issues)
[![GitHub Stars](https://img.shields.io/github/stars/rick1330/cybersage?style=flat-square)](https://github.com/rick1330/cybersage/stargazers)

**CyberSage integrates Large Language Models (LLMs) with standard cybersecurity tools and workflows to automate, assist, and enhance security operations.**

---

## Table of Contents

-   [1. Overview](#1-overview)
    -   [What is CyberSage?](#what-is-cybersage)
    -   [Goals](#goals)
    -   [Core Features](#core-features)
-   [2. Quick Start](#2-quick-start)
    -   [Prerequisites](#prerequisites)
    -   [Installation](#installation)
    -   [Configuration (`.env`)](#configuration-env)
    -   [Running CyberSage](#running-cybersage)
    -   [First Run Example](#first-run-example)
-   [3. Architecture](#3-architecture)
    -   [High-Level Overview](#high-level-overview)
    -   [Core Modules](#core-modules)
-   [4. Usage](#4-usage)
    -   [Command Line Interface (CLI)](#command-line-interface-cli)
    -   [REST API](#rest-api)
    -   [Web Interface](#web-interface)
-   [5. Contributing](#5-contributing)
-   [6. License](#6-license)
-   [7. Contact](#7-contact)

---

## 1. Overview

### What is CyberSage?

CyberSage is an advanced platform designed to augment cybersecurity professionals by leveraging the power of Artificial Intelligence. It acts as a co-pilot, streamlining security tasks, automating repetitive analysis, and providing intelligent insights by combining LLM reasoning capabilities with the practical execution of security tools. Think of it as an intelligent assistant that can understand security goals, plan execution steps, run tools, analyze results, and manage context over complex operations.

### Goals

*   **Automate:** Reduce manual effort for routine security tasks like reconnaissance, log analysis, and basic vulnerability assessment.
*   **Assist:** Provide support to analysts during complex investigations, threat hunting, and incident response procedures.
*   **Enhance:** Improve overall security posture through proactive threat identification, correlation, and intelligent workflow orchestration.
*   **Empower:** Offer a flexible and extensible framework for integrating custom tools, knowledge bases, and security workflows tailored to specific environments.

### Core Features

*   **AI Agent Framework:** Utilizes LLM-powered agents (built on LangChain) capable of planning, reasoning, and executing tasks using cybersecurity tools.
*   **Integrated Security Tools:** Includes secure wrappers for standard tools like Nmap, Shodan, WHOIS, VirusTotal, with clear interfaces for adding more.
*   **Workflow Engine:** Orchestrates sequences of tasks involving multiple tools, AI analysis steps, and conditional logic based on defined workflow schemas.
*   **Vector Search (RAG):** Embeds security data, documentation, and past findings for context-aware AI responses and knowledge retrieval.
*   **Multiple Interfaces:** Offers flexibility through a Command Line Interface (CLI), a comprehensive REST API, and a user-friendly Web UI.
*   **Microservices Architecture:** Designed for scalability, resilience, and independent development/deployment of components.
*   **Persistent Memory & Context:** Maintains conversational context and state for AI agents across interactions using backend stores like Redis.
*   **Extensibility:** Provides SDKs (Python, JavaScript, WASM planned) for developing and integrating custom plugins, tools, and runtimes.
*   **Platform Services:** Includes foundational services for identity management, configuration, billing/usage tracking, telemetry, and more.
*   **Task Queue:** Leverages Celery for handling background jobs, scheduled tasks (e.g., periodic scans), and asynchronous processing.

---

## 2. Quick Start

Follow these steps to get a local instance of CyberSage running.

### Prerequisites

*   **Git:** For cloning the repository. [Install Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
*   **Python:** Version 3.9 or higher (check with `python --version`). [Install Python](https://www.python.org/downloads/)
*   **Docker & Docker Compose:** Required for running the platform's containerized dependencies (Redis, Vector DB) and the application itself. [Install Docker](https://docs.docker.com/get-docker/)
*   **API Keys & Credentials:**
    *   `OPENAI_API_KEY`: **Required** for core LLM functionality. Get from [OpenAI](https://platform.openai.com/api-keys).
    *   `SHODAN_API_KEY`: Optional, needed for the Shodan tool. Get from [Shodan](https://account.shodan.io/register).
    *   `VIRUSTOTAL_API_KEY`: Optional, needed for the VirusTotal tool. Get from [VirusTotal](https://developers.virustotal.com/reference).
    *   *(Review `.env.example` or `.env.template` for all potential keys)*

### Installation

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/rick1330/cybersage.git
    cd cybersage
    ```

2.  **Set up a Python Virtual Environment (Recommended):**
    ```bash
    # Create a virtual environment named 'venv'
    python -m venv venv
    # Activate it (syntax varies by OS/shell)
    # Linux/macOS (bash/zsh)
    source venv/bin/activate
    # Windows (Command Prompt)
    # venv\Scripts\activate.bat
    # Windows (PowerShell)
    # venv\Scripts\Activate.ps1
    ```

3.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Configuration (`.env`)

Sensitive configuration and API keys are managed via environment variables loaded from a `.env` file.

1.  **Create `.env` from the template:**
    ```bash
    cp .env.template .env
    # Or use: cp .env.example .env (if .env.template doesn't exist)
    ```

2.  **Edit the `.env` file:**
    Open the newly created `.env` file in your text editor and fill in the required values, especially your API keys.

    ```dotenv
    # .env Example Snippet
    OPENAI_API_KEY=<YOUR_OPENAI_KEY_HERE>
    OPENAI_ORG_ID=<YOUR_OPENAI_ORG_ID_HERE> # Optional

    REDIS_URL=redis://redis:6379 # Default for docker-compose

    # Security - CHANGE THESE TO STRONG, UNIQUE SECRETS
    JWT_SECRET=replace-with-a-very-strong-random-string-for-jwt
    ENCRYPTION_KEY=replace-with-a-different-strong-random-string-for-encryption

    # External APIs (Optional but recommended for full functionality)
    SHODAN_API_KEY=<YOUR_SHODAN_KEY_HERE>
    VIRUSTOTAL_API_KEY=<YOUR_VIRUSTOTAL_KEY_HERE>
    ALIENTVAULT_API_KEY=<YOUR_ALIENVAULT_KEY_HERE>

    # Monitoring (Optional)
    SENTRY_DSN=
    ELASTIC_APM_SERVER_URL=

    # Development Settings (Defaults are usually fine for local dev)
    DEBUG=true
    ENVIRONMENT=development
    LOG_LEVEL=DEBUG
    ```

    **Security Warning:** Never commit your `.env` file to version control. The `.gitignore` file should already prevent this. Ensure `JWT_SECRET` and `ENCRYPTION_KEY` are cryptographically strong random strings.

### Running CyberSage

CyberSage uses Docker Compose to orchestrate its services for local development.

1.  **Build and Start Services:**
    From the project root directory:
    ```bash
    docker-compose up --build -d
    ```
    *   `--build`: Forces Docker to rebuild images if the Dockerfiles have changed.
    *   `-d`: Runs the containers in detached mode (in the background).

2.  **Verify Services are Running:**
    ```bash
    docker-compose ps
    ```
    You should see services like `api`, `redis`, `vector-db` listed with state `Up` or `running`.

3.  **View Logs (Optional):**
    ```bash
    docker-compose logs -f api # Follow logs for the API service
    ```
    ```bash
    docker-compose logs # View logs for all services
    ```

4.  **Stopping Services:**
    ```bash
    docker-compose down
    ```
    This stops and removes the containers defined in `docker-compose.yml`. Add `-v` to also remove associated volumes (data).

### First Run Example

With the services running via Docker Compose, you can interact with CyberSage.

**Example: Use the CLI to perform a WHOIS lookup:**

```bash
# Ensure your virtual environment is activated (source venv/bin/activate)
# The CLI interacts with the running API service
python interfaces/cli.py investigate --query "Get WHOIS information for example.com" --tools whois
```

This command uses the `investigate` function of the CLI, specifies a natural language query, and restricts the agent to using only the `whois` tool. The CLI will communicate with the backend API running in Docker to execute this task.

---

## 3. Architecture

### High-Level Overview

CyberSage utilizes a microservices architecture designed for modularity and scalability. The main functional areas are:

1.  **User Interfaces:** Provide interaction points for users (CLI, Web UI, Mobile UI). Located in `/interfaces`, `/ui-web`, `/ui-mobile`.
2.  **API Layer:** Acts as the entry point for requests. Includes an API Gateway (`/api-gateway`) for routing, authentication, and potentially GraphQL/WebSockets, and the core Backend API (`/interfaces/api`) built with FastAPI.
3.  **Core Logic:** Contains the central intelligence of CyberSage (`/core`). This includes the Agent Manager, Prompt Templates, Chain Builder, and Context Manager, leveraging LangChain.
4.  **Core Services:** Specialized backend services essential for platform operations, such as the Workflow Engine (`/core-services/workflow-engine-svc`) and Audit Log Service (`/core-services/audit-log-svc`).
5.  **Foundational Services:** General-purpose backend support services (`/services`) like interfaces to OpenAI, the vector store, agent memory (Redis), and logging.
6.  **Platform Services:** Handle cross-cutting concerns like identity, configuration, billing, and telemetry (`/platform-services`).
7.  **Tooling:** Includes wrappers for external security tools (`/tools`) and dedicated runtimes for their execution (`/tool-execution-runtimes`).
8.  **Data Stores:** Persistent storage including Redis (for caching and memory) and PostgreSQL with pgvector (for vector embeddings).
9.  **Background Processing:** A task queue system (Celery, `/tasks`) for handling asynchronous jobs and scheduled tasks.
10. **Shared Components:** Common code, schemas, and definitions located in `/shared`.
11. **Infrastructure:** Infrastructure-as-Code using Terraform and Helm (`/infra`).

*(For a more detailed breakdown and data flow diagrams, please refer to `docs/architecture.md` - to be generated)*

### Core Modules

*   `/core`: AI agent logic, prompts, context management.
*   `/tools`: Wrappers for cybersecurity tools (Nmap, Shodan, etc.).
*   `/services`: Interfaces for LLMs, memory, vector storage, logging.
*   `/interfaces`: API, CLI definitions.
*   `/core-services`: Workflow engine, audit logging.
*   `/platform-services`: Identity, configuration, billing, telemetry.
*   `/ui-web` & `/ui-mobile`: Frontend applications.
*   `/infra`: Infrastructure as Code (Terraform, Helm).
*   `/shared`: Common libraries, schemas, types.


---

## 4. Usage

Interact with CyberSage through its various interfaces:

### Command Line Interface (CLI)

Ideal for quick tasks, scripting, and terminal-based workflows.

**Example: Scan a target using Nmap via the CLI agent**
*(Assumes CLI is properly installed/configured)*

```bash
# Ensure venv is active: source venv/bin/activate
python interfaces/cli.py scan --target <TARGET_IP_OR_HOSTNAME> --scan-type service
```
**Example: Ask the investigation agent a question**
```bash
python interfaces/cli.py investigate --query "What are the known vulnerabilities for Apache Struts version 2.3.34?" --tools shodan virustotal
*See `/interfaces/cli.md` for detailed CLI command reference.* (*to be generated*)
```
### REST API

The most flexible way to integrate CyberSage into other applications or custom scripts. The API is served by the FastAPI backend, typically accessible via the API Gateway running in Docker (`http://localhost:8000` by default in `docker-compose.yml`).

**Example: Create a new agent via API (Replace <YOUR_JWT>)**

```bash
curl -X POST http://localhost:8000/api/v1/agents \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <YOUR_JWT>" \
     -d '{
           "agent_id": "my_custom_scanner",
           "agent_type": "security_scanner",
           "tools": ["nmap_tool", "whois_tool"],
           "options": { "default_nmap_args": "-T4 -A" }
         }'

```
**Example: Execute a task using the created agent (Replace <YOUR_JWT>)**

```bash
     curl -X POST http://localhost:8000/api/v1/tasks \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <YOUR_JWT>" \
     -d '{
           "task_id": "my_task_123",
           "agent_id": "my_custom_scanner",
           "task": "Perform a comprehensive scan including OS and service detection on 10.0.1.5",
           "parameters": { "target": "10.0.1.5" }
         }'
```
*See `/interfaces/api/README.md` and related API documentation for details.* (*to be generated*)

### Web Interface

Provides a graphical interface for managing agents, building/running workflows, viewing results, and interacting conversationally.

1.  **Access:** Navigate your browser to the URL where the `ui-web` service is hosted (e.g., `http://localhost:3000` if running separately or as per deployment configuration).
2.  **Login:** Authenticate using the configured identity provider.
3.  **Explore:** Use the navigation menus to access dashboards, agent chat, workflow builder, etc.

*See `/ui-web/README.md` for web UI specifics.* (*to be generated*)

---

## 5. Contributing

Contributions are welcome! Whether it's reporting bugs, suggesting features, improving documentation, or submitting code changes, please refer to our contribution guidelines.

*   **Contribution Guidelines:** [CONTRIBUTING.md](./CONTRIBUTING.md)
*   **Code of Conduct:** [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md)
*   **Issue Tracker:** [GitHub Issues](https://github.com/rick1330/cybersage/issues)

---

## 6. License

CyberSage is licensed under the Apache License Version 2.0. See the [LICENSE](./LICENSE) file for the full license text.

---

## 7. Contact

*   **Maintainers:** [Rick](https://github.com/rick1330)
*   **Project Repository:** [https://github.com/rick1330/cybersage](https://github.com/rick1330/cybersage)
*   **Reporting Security Issues:** Please follow the instructions in [SECURITY.md](./SECURITY.md).

  
