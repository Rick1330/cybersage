# Core: Context Manager

The `ContextManager` (`core/context_manager.py`) plays a vital role in managing the state, history, and relevant information associated with user sessions, specific tasks, or agent interactions within CyberSage. While the `MemoryService` provides the low-level storage (e.g., Redis), the `ContextManager` offers a higher-level abstraction for accessing, manipulating, and persisting this contextual data.

## Table of Contents

1.  [Purpose](#1-purpose)
2.  [Distinction from MemoryService & AgentManager](#2-distinction-from-memoryservice--agentmanager)
3.  [Key Responsibilities](#3-key-responsibilities)
4.  [Types of Context Managed](#4-types-of-context-managed)
    -   [Conversational History](#conversational-history)
    -   [Session State](#session-state)
    -   [Security Context](#security-context)
    -   [Analytical Context](#analytical-context)
5.  [Public API Overview (Conceptual)](#5-public-api-overview-conceptual)
    -   [`load_context()`](#load_context)
    -   [`save_context()`](#save_context)
    -   [`get_context_value()`](#get_context_value)
    -   [`update_context_value()`](#update_context_value)
    -   [`clear_context()`](#clear_context)
    -   [`manage_session()`](#manage_session-context-manager)
6.  [Backend Options & Persistence](#6-backend-options--persistence)
7.  [Context Lifecycle & TTL](#7-context-lifecycle--ttl)
8.  [Integration with Other Components](#8-integration-with-other-components)
9.  [Error Handling](#9-error-handling)

---

## 1. Purpose

The primary goals of the `ContextManager` are:

*   **State Management:** To load, save, and manage the state associated with a user's interaction or a specific task execution.
*   **Context Provisioning:** To provide relevant context (like chat history, previous results, user permissions) to agents, chains, or tools when they need it.
*   **Data Abstraction:** To abstract the underlying storage mechanism (e.g., Redis, database) provided by the `MemoryService` or other data services.
*   **Session Scoping:** To manage context within defined boundaries (e.g., a user session, a specific workflow execution).
*   **Data Consistency:** To ensure context is loaded and saved reliably.

It acts as the central hub for accessing and persisting the dynamic information needed for coherent and stateful interactions within CyberSage.

---

## 2. Distinction from MemoryService & AgentManager

It's important to differentiate the `ContextManager` from related components:

*   **`MemoryService` (`/services/memory_service.py`):** Provides the actual backend storage (e.g., Redis, database) and low-level methods (`get`, `set`, `delete`) for storing key-value data or structured memory objects (like LangChain's memory classes). The `ContextManager` *uses* the `MemoryService`.
*   **`AgentManager` (`/core/agent_manager.py`):** Focuses on the lifecycle (create, get, delete) and execution (`execute_task`) of AI agents. While agents *use* context (especially memory), the `AgentManager` itself doesn't typically manage the broader session or analytical context; it relies on the `ContextManager` or directly on the `MemoryService` for agent-specific memory.

The `ContextManager` operates at a higher level, orchestrating the use of memory and potentially other data sources to provide a complete contextual picture for a given interaction or task.

---

## 3. Key Responsibilities

*   **Context Loading:** Retrieving relevant context data based on identifiers (e.g., `session_id`, `task_id`, `user_id`).
*   **Context Saving:** Persisting updated context back to the appropriate backend storage via services like `MemoryService`.
*   **Context Structuring:** Organizing different types of context (chat history, session variables, security tokens) logically.
*   **Context Injection:** Providing mechanisms or methods for other components (agents, chains) to easily access the context they need.
*   **Lifecycle Management:** Handling the creation, expiration (TTL), and deletion of context data.
*   **Data Source Aggregation:** Potentially retrieving context from multiple sources (e.g., Redis for chat history, a database for user profile info, Vector Store for relevant documents).

---

## 4. Types of Context Managed

The `ContextManager` might handle various types of contextual information:

### Conversational History

*   The sequence of user inputs and agent responses in a chat-like interaction.
*   Often stored using LangChain memory classes (`ConversationBufferMemory`, `ConversationSummaryMemory`) via the `MemoryService`.

### Session State

*   Arbitrary key-value data associated with a user's session (e.g., selected target IP, current workflow state, UI preferences).
*   Typically stored in Redis or another fast key-value store via `MemoryService`.

### Security Context

*   Information related to the user's identity, permissions, roles, or authentication tokens.
*   May involve interaction with the `IdentityService` (`platform-services/identity-svc/`). Crucial for authorization checks.

### Analytical Context

*   Intermediate results, findings, or summaries generated during a multi-step task or workflow.
*   Could include summaries of tool outputs, extracted indicators of compromise (IOCs), or knowledge retrieved from the `VectorStoreService`.

---

## 5. Public API Overview (Conceptual)

The specific API of the `ContextManager` would depend on its implementation, but might include methods like:

### `load_context()`

```python
async def load_context(self, session_id: str, context_keys: Optional[List[str]] = None) -> Dict[str, Any]:
```
* **Purpose**: Loads context data for a given session ID. Can optionally specify which keys to load.

* **Returns**: A dictionary containing the requested context data.

### `save_context()`
```python
async def save_context(self, session_id: str, context_data: Dict[str, Any]) -> None:
```
* **Purpose**: Saves or updates context data for a session ID.

### `get_context_value()`
```python
async def get_context_value(self, session_id: str, key: str, default: Any = None) -> Any:
```
* **Purpose**: Retrieves a specific value from the context.
### `update_context_value()`
```python
async def update_context_value(self, session_id: str, key: str, value: Any) -> None:
```
* **Purpose**: Updates or adds a single key-value pair to the context.
### `clear_context()`
```python
async def clear_context(self, session_id: str, keys: Optional[List[str]] = None) -> None:
```
* **Purpose**: Deletes context data for a session, optionally specifying keys to remove.
### `manage_session() (Context Manager)`
```python
@asynccontextmanager
async def manage_session(self, session_id: str): # Yields a session context object
```
* **Purpose**: Provides an async context manager to automatically load context on entry and potentially save it on exit.

* **Yields**: An object allowing easy access to the session's context.

---

## 6. Backend Options & Persistence

The `ContextManager` relies heavily on backend services for persistence. The choice of backend depends on the type and volatility of the data:

*   **`MemoryService` (e.g., using Redis):** Commonly used for storing frequently accessed, potentially volatile data like conversational history (using LangChain memory objects) and temporary session state due to its high speed. See `/services/memory_service.md`.
*   **Databases (e.g., PostgreSQL):** Might be used for storing more persistent, structured data that forms part of the context, such as user profile information, task metadata, or historical findings.
   ---

## 7. Context Lifecycle & TTL

*   Context data, especially temporary session state and chat history stored in fast backends like Redis, often requires a Time-To-Live (TTL) to prevent indefinite storage consumption and manage data relevance.
*   The `ContextManager`, likely in coordination with the `MemoryService` (which can leverage features like Redis's `EXPIRE` command), is responsible for setting and managing this expiration.
*   Configuration settings within CyberSage (e.g., in `configs/settings.yaml`) should define default TTLs for different types of context data.
   ---

## 8. Integration with Other Components

The `ContextManager` serves as a central hub, interacting with numerous other parts of the CyberSage platform:

*   **`MemoryService` (`/services/memory_service.py`):** The primary backend for storing and retrieving conversational memory and session state data used by the `ContextManager`.
*   **`VectorStoreService` (`/services/vectorstore_service.py`):** May be queried by the `ContextManager` or components using its context to retrieve relevant documents for analytical purposes (RAG).
*   **`AgentManager` & Agents (`/core/agent_manager.py`):** Agents created by the `AgentManager` receive their specific memory objects and potentially other relevant session context provisioned or managed via the `ContextManager`.
*   **`ChainBuilder` & Chains (`/core/chain_builder.py`):** Chains constructed by the `ChainBuilder` can be configured to utilize memory objects managed through the `ContextManager`, enabling stateful chain executions.
*   **API Endpoints (`/interfaces/api/`):** API request handlers often establish the session scope (e.g., based on a `session_id` derived from a user request or JWT) and interact with the `ContextManager` to load the necessary state for processing the request and save updated state afterward.
*   **Workflow Engine (`/core-services/workflow-engine-svc/`):** Uses the `ContextManager` extensively to manage the state of ongoing workflows, passing data and intermediate results between different steps or tasks.
*   **Identity Service (`/platform-services/identity-svc/`):** May provide user identity, roles, and permission information that forms the security context managed or accessed via the `ContextManager`.
  ---

## 9. Error Handling

Potential errors related to the `ContextManager` include:

*   Errors originating from backend services (e.g., `MemoryService` reporting a Redis connection error, database query failures).
*   Context not found errors if data for a requested `session_id` does not exist or has expired.
*   Serialization or deserialization errors if context data involves complex object structures that fail to be stored or retrieved correctly.
*   Permission errors if attempting to access or modify context data without proper authorization (potentially checked against security context).

The `ContextManager` should implement appropriate error handling, potentially logging issues and raising specific custom exceptions (e.g., `ContextNotFoundError`, `ContextStorageError`) to its callers, allowing them to react accordingly.
*   **`VectorStoreService` (e.g., using pgvector):** Used specifically to retrieve relevant documents or knowledge snippets based on semantic similarity, providing analytical context for Retrieval-Augmented Generation (RAG). See `/services/vectorstore_service.md`.

The `ContextManager` abstracts these underlying storage mechanisms, deciding where to fetch or store different types of context based on its internal logic and configuration.
```
