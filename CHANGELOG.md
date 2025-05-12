# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
-   *(Add new features here as they are developed)*
-   Initial project structure setup based on repository analysis.
-   Core AI agent manager (`core/agent_manager.py`).
-   Tool wrappers for Nmap, WHOIS, Shodan, VirusTotal (`tools/`).
-   Foundational services for OpenAI, Memory (Redis), Vector Store (pgvector), Logging (`services/`).
-   Initial FastAPI backend API (`interfaces/api/`) and CLI (`interfaces/cli.py`).
-   API Gateway structure (`api-gateway/`).
-   Web and Mobile UI placeholders (`ui-web/`, `ui-mobile/`).
-   Core service placeholders (Workflow Engine, Audit Log, etc. in `core-services/`).
-   Platform service placeholders (Identity, Config, etc. in `platform-services/`).
-   Docker Compose setup for local development (`docker-compose.yml`).
-   Production Dockerfile (`Dockerfile`).
-   Basic testing structure and fixtures (`tests/`).
-   Initial configuration files (`configs/`).
-   Root documentation files: README, CONTRIBUTING, CODE_OF_CONDUCT, LICENSE.

### Changed
-   *(Add changes in existing functionality here)*

### Deprecated
-   *(Add features soon to be removed here)*

### Removed
-   *(Add features removed in this release here)*

### Fixed
-   *(Add bug fixes here)*

### Security
-   *(Add security vulnerability fixes here)*

## [0.1.0] - YYYY-MM-DD  <!-- Placeholder: Update date upon actual release -->

### Added
-   **Initial Release:** First functional version of CyberSage intended for testing/evaluation.
-   Core agent framework capable of executing basic tasks using integrated tools.
-   API endpoints for agent creation and task execution.
-   Redis-backed memory for agent context persistence.
-   Basic CLI for interacting with agents.
-   Docker setup for running core backend services locally.

---

*Instructions:*
*   *Before tagging a release (e.g., `v0.1.0`), replace `[Unreleased]` with the new version tag (e.g., `[0.1.0] - YYYY-MM-DD`).*
*   *Create a new `## [Unreleased]` section at the top.*
*   *Populate the sections (Added, Changed, Fixed, etc.) under the new version tag with the relevant changes made since the last release.*
*   *Update the date `YYYY-MM-DD` to the actual release date.*
