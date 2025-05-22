# CyberSage System Architecture

This document outlines the architecture of the CyberSage platform, an AI-powered cybersecurity co-pilot. It details the system's components, their interactions, design principles, and technology stack.

## 1. High-Level Overview

*   **Purpose:** CyberSage integrates Large Language Models (LLMs) with standard cybersecurity tools and workflows to automate, assist, and enhance security operations. It acts as a co-pilot to streamline security tasks, automate repetitive analysis, and provide intelligent insights.
*   **Main Components:**
    *   **User Interfaces:**
        *   Web UI (`ui-web/`): Main graphical interface for users.
        *   CLI (`interfaces/cli.py`): Command-line interface for scripting and direct interaction.
        *   Mobile UI (`ui-mobile/`): Companion mobile application.
    *   **API Gateway (`api-gateway/`):** Single entry point for all client requests, routing them to appropriate backend services. Built with NestJS.
    *   **Backend API (`interfaces/api/`):** Main backend service exposing RESTful APIs for platform functionalities. Built with FastAPI.
    *   **Core AI Engine & Logic (`core/`):** Houses the central AI capabilities, including:
        *   `AgentManager`: Manages the lifecycle and orchestration of AI agents.
        *   `ChainBuilder`: Constructs sequences of LLM calls and tool executions.
        *   Prompt Engineering: Manages and optimizes prompts for AI tasks.
    *   **Core Services (`core-services/`):** Specialized backend services supporting core functionalities:
        *   Workflow Engine (`workflow-engine-svc/`): Orchestrates complex, multi-step security workflows.
        *   Audit Log Service (`audit-log-svc/`): Tracks significant actions and events.
        *   (Scheduler: Implied by Celery for background tasks, though not a distinct service in `core-services/`)
    *   **Platform Services (`platform-services/`):** Cross-cutting services for platform operation:
        *   Identity Service: Manages user authentication and authorization.
        *   Configuration Service: Handles dynamic configuration management.
        *   Telemetry Service: Collects metrics and logs for monitoring.
    *   **Tool Execution Runtimes (`tool-execution-runtimes/`):** Sandboxed environments for secure execution of integrated cybersecurity tools.
    *   **Data Services/Stores:**
        *   Redis: Used for caching, session management, and as a message broker for Celery (`services/memory_service.py` also implies its use for agent memory).
        *   Vector Database (e.g., PostgreSQL with pgvector): For Retrieval-Augmented Generation (RAG) to provide context to LLMs (`services/vectorstore_service.py`).
        *   PostgreSQL: Primary relational database for persistent storage (inferred from pgvector usage and common practice).
    *   **Background Task Processing (`tasks/`):** Celery workers for handling asynchronous jobs and scheduled tasks.
*   **Primary Interactions:**
    *   User Interfaces (Web, CLI, Mobile) interact with the API Gateway.
    *   The API Gateway authenticates requests and routes them to the Backend API or other relevant services.
    *   The Backend API utilizes the Core AI Engine for complex tasks, invoking agents and chains.
    *   The Core AI Engine and agents leverage Core Services (e.g., Workflow Engine) and Platform Services (e.g., Identity).
    *   AI Agents use Tools, which are executed within their dedicated Tool Execution Runtimes.
    *   Data Services provide storage and retrieval for application state, user data, AI memory, and knowledge bases.
    *   Background Task Processing system (Celery) handles long-running operations offloaded by the Backend API or Core Services.

## 2. Architectural Principles

*   **Microservices Architecture:** The system is composed of multiple small, independent, and deployable services (e.g., API Gateway, Backend API, various Core and Platform services).
*   **Modularity & Reusability:** Components are designed to be loosely coupled and reusable across different parts of the platform (e.g., shared libraries in `shared/`, distinct services).
*   **Scalability:** Designed for horizontal scaling of services, particularly the stateless backend components and task workers.
*   **Resilience:** Aims for fault tolerance through service separation, redundancy (where applicable), and graceful degradation of non-critical functions.
*   **Security by Design:** Integrating security considerations throughout the development lifecycle. Key documents include `SECURITY.md` and `tools/SECURITY_GUIDELINES.md`. Secure sandboxed runtimes for tools are a core feature.
*   **AI-First:** Leveraging LLMs and AI agents (LangChain framework) as central elements for reasoning, task execution, and automation.
*   **Extensibility:** Designed to allow new tools, workflows, and AI agents to be added with relative ease, supported by SDKs in `plugins/sdk/`.
*   **Asynchronous Operations:** Utilizing background task processing (Celery in `tasks/`) for long-running operations, ensuring responsiveness of user-facing interfaces.

## 3. Logical Architecture View

*   **Conceptual Diagram:** [A conceptual diagram will be added here showing the major functional blocks like User Interfaces, API Gateway, Backend Services, AI Core, Data Stores, and Tool Runtimes, and their primary data flows.]
*   **Service Interaction Model:**
    *   **User-Initiated Task Flow:**
        1.  A user initiates a task (e.g., "scan target X") via a User Interface (Web UI, CLI).
        2.  The request is sent to the API Gateway.
        3.  The API Gateway authenticates the user and routes the request to the Backend API.
        4.  The Backend API validates the request, potentially creates a task entry, and may invoke the Core AI Engine (e.g., `AgentManager` to execute a task with an agent).
        5.  The `AgentManager` selects or creates an agent, equips it with tools, and passes the task.
        6.  The agent, using its LLM, plans and executes steps. If a tool is needed, it requests execution via the Tool Execution Runtimes.
        7.  Results are returned through the chain, potentially stored in Data Stores (e.g., agent memory in Redis, findings in PostgreSQL), and passed back to the user via the API Gateway and User Interface.
        8.  Long-running tasks are offloaded to Celery workers.
    *   **Workflow Execution:**
        1.  Workflows are defined in structured formats (e.g., YAML, JSON) within the `workflows/` directory.
        2.  The Workflow Engine (`core-services/workflow-engine-svc/`) loads and interprets these definitions.
        3.  It orchestrates the execution of workflow steps, which can include invoking AI agents, running specific tools, calling other services, or waiting for human input.
    *   **Agent Tool Usage:**
        1.  Agents, when needing to use a tool, call the tool's interface.
        2.  The platform ensures this tool execution happens within a designated, secure, and sandboxed Tool Execution Runtime to isolate it from the core system and other tools.

## 4. Technology Stack

*   **Backend:**
    *   Python: FastAPI (for `interfaces/api/`), Celery (for `tasks/`).
    *   Node.js: NestJS (for `api-gateway/`).
*   **Frontend (`ui-web/`):**
    *   TypeScript, React (Assumed, based on common practices for modern web UIs and presence of TypeScript in project standards. To be confirmed by inspecting `ui-web/package.json`).
*   **AI/LLM:**
    *   LangChain (core framework used in `core/`).
    *   OpenAI (primary LLM provider, via `services/openai_service.py`).
*   **Data Stores:**
    *   Redis (caching, message broker, agent memory, via `services/memory_service.py` and main `README.md`).
    *   PostgreSQL with pgvector extension (vector database for RAG, persistent storage, via main `README.md` and `services/vectorstore_service.py`).
*   **Messaging/Tasks:**
    *   Celery (for asynchronous task processing, `tasks/`).
*   **Containerization:**
    *   Docker (`Dockerfile`).
    *   Docker Compose (`docker-compose.yml` for local development).
*   **Infrastructure as Code (IaC) & Deployment (`infra/`):**
    *   Terraform (for managing cloud infrastructure).
    *   Helm (for Kubernetes deployments).
*   **Documentation:**
    *   Docusaurus (`docs/`).

## 5. Deployment View (High-Level)

*   **Containerization:** All backend services, and potentially frontend applications, are designed to be containerized using Docker. This ensures consistency across environments.
*   **Orchestration:** Kubernetes is the target orchestration platform for production environments. Helm charts for deploying CyberSage components to Kubernetes are maintained in `infra/helm/`.
*   **Environments:**
    *   Local Development: Docker Compose (`docker-compose.yml`) is used to set up a local development environment.
    *   Cloud Environments (Dev, Staging, Prod): Terraform scripts in `infra/terraform/environments/` are used to provision and manage the necessary cloud infrastructure for these environments.

---
## Architecture Decision Records (ADRs)

Significant architectural decisions for the CyberSage platform are documented using Architecture Decision Records (ADRs). This approach helps maintain a clear history of why certain technical choices were made.

*   **Location:** ADRs are stored in the `.adr-tools/` directory in the root of the repository.
*   **Format:** We use a lightweight ADR format, typically including title, status, date, context, decision, and consequences.
*   **Process:** New ADRs are proposed via pull requests and reviewed by the development team.

The first ADR, `0001-adopt-docusaurus-and-documentation-strategy.md`, documents the decision to standardize our documentation practices.
```
