# CyberSage Services Layer

This directory contains foundational backend services that provide essential, decoupled functionalities required by various parts of the CyberSage platform, particularly the `/core` engine and potentially the `/interfaces/api`. These services abstract interactions with external APIs, databases, caches, and other infrastructure components.

## Table of Contents

1.  [Purpose](#1-purpose)
2.  [Key Services](#2-key-services)
3.  [Design Principles](#3-design-principles)
4.  [Dependency Overview](#4-dependency-overview)
5.  [Service Interaction](#5-service-interaction)

---

## 1. Purpose

The primary goals of the services layer are:

*   **Abstraction:** Hide the implementation details of interacting with external systems (like OpenAI's API, Redis, PostgreSQL/pgvector).
*   **Decoupling:** Allow core logic (`/core`) to depend on stable service interfaces rather than directly on specific libraries or infrastructure details.
*   **Reusability:** Provide common functionalities (like LLM interaction, caching, vector search) that can be used by multiple components (agents, workflows, API endpoints).
*   **Configuration Management:** Centralize the configuration (e.g., API keys, connection strings) needed for these external interactions.
*   **Testability:** Enable easier mocking and testing of components that depend on these services.

---

## 2. Key Services

This layer typically includes services such as:

*   **[`OpenAIService`](./openai_service.md):** Manages interactions with the OpenAI API (or potentially other LLM providers), handling authentication, model selection, API calls (`chat`, `completion`), and error handling.
*   **[`VectorStoreService`](./vectorstore_service.md):** Provides an interface for embedding text data and performing similarity searches using a vector database backend (e.g., PostgreSQL/pgvector, FAISS, ChromaDB). Essential for Retrieval-Augmented Generation (RAG).
*   **[`MemoryService`](./memory_service.md):** Offers methods for storing, retrieving, and managing persistent agent memory and session state, typically using a fast key-value store like Redis.
*   **[`LoggingService`](./logging_service.md):** Configures and provides access to the platform's structured logging system, allowing consistent logging practices across different modules.

*(Other services might be added as needed, e.g., a dedicated configuration service client, a notification service, etc.)*

---

## 3. Design Principles

*   **Interface-Based:** Services should ideally expose clear, well-defined interfaces (e.g., abstract base classes or protocols).
*   **Dependency Injection:** Services are typically instantiated at application startup and injected into the components that need them, promoting loose coupling.
*   **Configuration Driven:** Service behavior (API keys, connection details, model names) should be configurable via environment variables or configuration files (`/configs`).
*   **Error Handling:** Services should handle expected errors from external systems (e.g., API rate limits, connection errors) and potentially raise standardized exceptions.
*   **Asynchronous:** Service methods interacting with I/O (network calls, database access) should be asynchronous (`async def`) to work well within the platform's async framework (e.g., FastAPI).

---

## 4. Dependency Overview

The services layer interacts with external systems and infrastructure:

*   **`OpenAIService`** -> OpenAI API
*   **`MemoryService`** -> Redis (or other configured key-value store)
*   **`VectorStoreService`** -> PostgreSQL/pgvector (or other configured vector DB)
*   **`LoggingService`** -> File System / Console / Remote Log Aggregator (e.g., ELK, Sentry)

Internal dependencies:

*   `/core` components (AgentManager, ContextManager, Chains) -> Use `OpenAIService`, `MemoryService`, `VectorStoreService`.
*   `/interfaces/api` endpoints -> May use services directly or indirectly via `/core`.
*   All components -> Use `LoggingService`.

---

## 5. Service Interaction

Components needing a service typically receive an instance via dependency injection during their initialization.

**Conceptual Example (in an API endpoint):**

```python
from fastapi import FastAPI, Depends
from services.openai_service import OpenAIService
# Assume get_openai_service is a dependency provider function

app = FastAPI()

@app.post("/ask")
async def ask_llm(
    query: str,
    openai_service: OpenAIService = Depends(get_openai_service)
):
    # Use the injected service
    response = await openai_service.chat_completion(messages=[{"role": "user", "content": query}])
    return {"response": response}
```
