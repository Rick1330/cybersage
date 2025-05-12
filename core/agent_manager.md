# Core: Agent Manager

The `AgentManager` (`core/agent_manager.py`) is a crucial component of the CyberSage core engine. It is responsible for the lifecycle management and orchestration of AI agents. These agents are specialized AI entities designed to perform specific cybersecurity tasks by leveraging Large Language Models (LLMs) and integrated tools.

## Table of Contents

1.  [Purpose](#1-purpose)
2.  [Key Responsibilities](#2-key-responsibilities)
3.  [Core Concepts](#3-core-concepts)
    -   [Agents](#agents)
    -   [Tools](#tools)
    -   [Memory](#memory)
4.  [Public API Overview](#4-public-api-overview)
    -   [`create_agent()`](#create_agent)
    -   [`get_agent()`](#get_agent)
    -   [`execute_task()`](#execute_task)
    -   [`delete_agent()`](#delete_agent)
    -   [`agent_session()`](#agent_session-context-manager)
    -   [`get_agent_metadata()`](#get_agent_metadata)
5.  [Code Examples](#5-code-examples)
    -   [Creating a New Agent](#creating-a-new-agent)
    -   [Executing a Task with an Agent](#executing-a-task-with-an-agent)
    -   [Using an Agent within a Session](#using-an-agent-within-a-session)
6.  [Error Handling](#6-error-handling)
7.  [Integration with Other Core Components](#7-integration-with-other-core-components)
8.  [Future Enhancements](#8-future-enhancements)

---

## 1. Purpose

The primary purpose of the `AgentManager` is to provide a centralized system for:

*   **Creating** AI agents with specific configurations, tools, and LLM settings.
*   **Retrieving** existing agents for reuse.
*   **Executing** tasks through these agents.
*   **Managing** the state and resources associated with each agent, including their memory.
*   **Deleting** agents and cleaning up their resources when no longer needed.

It abstracts the complexities of initializing LangChain agents (or similar AI agent frameworks) and provides a consistent interface for other parts of the CyberSage platform (like the API or Workflow Engine) to interact with AI capabilities.

---

## 2. Key Responsibilities

*   **Agent Instantiation:** Initializes agent objects, configuring them with the appropriate LLM (via `OpenAIService`), tools (from `/tools`), and memory (via `MemoryService`).
*   **Agent Registry:** Maintains a collection of active agents, allowing them to be identified and accessed by a unique `agent_id`.
*   **Task Delegation:** Receives task descriptions and delegates them to the appropriate agent for execution.
*   **Memory Management Interface:** Coordinates with the `MemoryService` to create, load, and save conversational memory for each agent.
*   **Tool Provisioning:** Ensures agents are equipped with the correct set of tools they are authorized and configured to use.
*   **Lifecycle Management:** Handles the creation, retrieval, and deletion of agents, including associated resource cleanup.
*   **Metadata Tracking:** Stores and provides metadata about each managed agent (e.g., type, creation time, status).

---

## 3. Core Concepts

### Agents

In CyberSage, an agent is an AI entity powered by an LLM that can:

*   **Reason:** Understand tasks and plan steps to achieve goals.
*   **Use Tools:** Interact with integrated cybersecurity tools (e.g., Nmap, Shodan) to gather information or perform actions.
*   **Maintain Context:** Remember previous interactions and results using its assigned memory.
*   **Communicate:** Generate responses and report findings.

The `AgentManager` typically uses a framework like LangChain to initialize agents (e.g., `initialize_agent` with types like `ZERO_SHOT_REACT_DESCRIPTION`).

### Tools

Tools are specific functionalities that an agent can use. These are typically wrappers around external cybersecurity tools or internal platform functions. The `AgentManager` ensures that when an agent is created, it is provided with a list of `BaseTool` instances it can utilize.

*   See: `/tools/README.md` and `/tools/base_tool.py`

### Memory

Each agent can be equipped with memory to retain context from its interactions. The `AgentManager` collaborates with the `MemoryService` (which often uses Redis) to provide this capability. This allows agents to have conversations, remember previous steps in a multi-turn task, and build upon prior knowledge within a session.

*   See: `/services/memory_service.md`

---

## 4. Public API Overview

The `AgentManager` class (`core/agent_manager.py`) exposes the following primary methods:

### `create_agent()`

```python
async def create_agent(
    self,
    agent_id: str,
    agent_type: str, # e.g., 'scanner', 'investigator', 'reporter'
    tools: List[BaseTool],
    description: Optional[str] = None,
    **kwargs # Additional LLM or agent configuration
) -> Any: # Returns the created agent instance
```
*   **Purpose:** Creates and registers a new AI agent.
*   **Parameters:**
    *   `agent_id`: A unique identifier for the new agent.
    *   `agent_type`: A string categorizing the agent's general purpose.
    *   `tools`: A list of instantiated tool objects (derived from `BaseTool`) that this agent can use.
    *   `description`: An optional textual description of the agent's purpose.
    *   `**kwargs`: Additional parameters for configuring the agent or its underlying LLM (e.g., specific model, temperature).
*   **Returns:** The initialized agent object.
*   **Raises:** `ValueError` if `agent_id` already exists, `AgentError` on failure.

### `get_agent() ` 
```python
async def get_agent(self, agent_id: str) -> Any: # Returns the agent instance
```
*   **Purpose:** Retrieves an existing agent by its ID.
*   **Parameters:**
    *   `agent_id`: The ID of the agent to retrieve.
*   **Returns:** The agent object.
*   **Raises:** `AgentNotFoundError` if the agent with the specified ID is not found.

### `execute_task()`
```python
async def execute_task(self, agent_id: str, task: str) -> str: # Returns the task result
```
*   **Purpose:** Assigns a task (described as a natural language string) to a specified agent for execution.
*   **Parameters:**
    *   `agent_id`: The ID of the agent that should execute the task.
    *   `task`: A string describing the task to be performed.
*   **Returns:** A string containing the result or output of the task execution.
*   **Raises:** `AgentNotFoundError` if the agent doesn't exist, `AgentError` if task execution fails.

### `delete_agent()`
```python
async def delete_agent(self, agent_id: str) -> None:
```
*   **Purpose:** Deletes an agent and cleans up its associated resources (e.g., its memory from `MemoryService`).
*   **Parameters:**
    *   `agent_id`: The ID of the agent to delete.
*   **Raises:** `AgentNotFoundError` if the agent doesn't exist, `AgentError` on failure.

### `agent_session()` (Context Manager)
```python
@asynccontextmanager
async def agent_session(self, agent_id: str): # Yields the agent instance
```
*   **Purpose:** Provides a context manager for using an agent within a session, potentially handling setup and teardown logic like saving memory.
*   **Parameters:**
    *   `agent_id`: The ID of the agent to use in the session.
*   **Yields:** The agent instance.
*   **Usage:**

### `get_agent_metadata()`
```python
def get_agent_metadata(self, agent_id: str) -> Dict[str, Any]:
```
*   **Purpose:** Retrieves metadata associated with a specific agent.
*   **Parameters:**
    *   `agent_id`: The ID of the agent.
*   **Returns:** A dictionary containing metadata such as agent type, creation time, status, tool count, etc.
*   **Raises:** `AgentNotFoundError` if the agent doesn't exist.

---

## 5. Code Examples

*(Note: These examples assume `agent_manager` is an instantiated `AgentManager` object, and necessary services like `OpenAIService` and `MemoryService` are configured. Tool instances like `NmapTool` are also assumed to be available.)*

### Creating a New Agent
```python
from core.agent_manager import AgentManager
from services.openai_service import OpenAIService
from services.memory_service import MemoryService
from tools.nmap_tool import NmapTool # Example tool

# Initialize services (typically done at application startup)
openai_service = OpenAIService(api_key="YOUR_OPENAI_KEY")
memory_service = MemoryService(redis_url="redis://localhost:6379")

agent_manager = AgentManager(openai_service, memory_service)

async def setup_scanner_agent():
    nmap = NmapTool()
    try:
        scanner_agent = await agent_manager.create_agent(
            agent_id="network_scanner_01",
            agent_type="scanner",
            tools=[nmap],
            description="Agent specialized for network scanning using Nmap."
        )
        print(f"Agent '{scanner_agent.agent_id}' created successfully.")
        return scanner_agent
    except ValueError as e:
        print(f"Error creating agent: {e}")
        # Optionally retrieve existing agent if error is due to pre-existence
        scanner_agent = await agent_manager.get_agent("network_scanner_01")
        return scanner_agent
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

# To run: asyncio.run(setup_scanner_agent())
```
### Executing a Task with an Agent
```python
async def run_scan_task(agent_id: str, target_ip: str):
    task_description = f"Perform a basic SYN scan on {target_ip} and report open ports."
    try:
        print(f"Executing task with agent '{agent_id}': {task_description}")
        result = await agent_manager.execute_task(agent_id, task_description)
        print("\n--- Scan Result ---")
        print(result)
        print("-------------------")
    except Exception as e:
        print(f"Error executing task: {e}")

# Assuming 'network_scanner_01' agent exists:
# To run: asyncio.run(run_scan_task("network_scanner_01", "scanme.nmap.org"))
```
### Using an Agent within a Session
```python
async def perform_tasks_in_session(agent_id: str):
    try:
        async with agent_manager.agent_session(agent_id) as agent:
            print(f"Using agent '{agent.agent.llm_chain.prompt.template}' in session.") # Example access
            response1 = await agent.arun("What was the previous instruction?") # Will use memory
            print(f"Response 1: {response1}")
            
            response2 = await agent.arun("Okay, now scan scanme.nmap.org for common web ports.")
            print(f"Response 2: {response2}")
        print(f"Session for agent '{agent_id}' ended. Memory should be saved.")
    except Exception as e:
        print(f"Error during agent session: {e}")

# To run: asyncio.run(perform_tasks_in_session("network_scanner_01"))
```
---

## 6. Error Handling

The `AgentManager` defines custom exceptions for specific error conditions:

*   `AgentError`: Base exception for general agent-related errors.
*   `AgentNotFoundError`: Raised when an operation attempts to use an `agent_id` that does not correspond to an existing agent.

Standard Python exceptions like `ValueError` may also be raised for invalid input parameters. Callers should implement appropriate `try-except` blocks to handle these potential errors.

---

## 7. Integration with Other Core Components

*   **`OpenAIService` (`/services/openai_service.py`):** The `AgentManager` uses this service to get configured LLM instances (e.g., `ChatOpenAI`) required for initializing LangChain agents.
*   **`MemoryService` (`/services/memory_service.py`):** Used to create, manage, and persist the conversational memory for each agent. The `AgentManager` typically requests a memory instance from this service when creating an agent.
*   **Tool Wrappers (`/tools/*.py`):** The `AgentManager` is provided with a list of instantiated tool objects (derived from `BaseTool`) when creating an agent. These tools are then made available to the LangChain agent.
*   **`ChainBuilder` (`/core/chain_builder.py`):** While the `AgentManager` directly initializes agents using `initialize_agent` from LangChain in the current implementation, it could potentially leverage the `ChainBuilder` for more complex or custom agent setups in the future.
*   **`ContextManager` (`/core/context_manager.py`):** The `AgentManager` focuses on agent lifecycle, while the `ContextManager` handles broader session context, security state, and analytical context. They are related but serve distinct levels of abstraction. The `AgentManager`'s memory operations are a subset of what the `ContextManager` might manage.

---

## 8. Future Enhancements

*   **Agent Pooling:** Implement a pool of pre-initialized agents for common types to reduce creation latency.
*   **Dynamic Tool Loading:** Allow agents to dynamically discover and load tools based on task requirements.
*   **More Sophisticated Agent Types:** Support for different LangChain agent types or custom agent implementations.
*   **Resource Limits per Agent:** Integration with resource management to control CPU/memory usage by agents.
*   **Agent Monitoring & Metrics:** Expose metrics about agent activity, task success/failure rates, and token usage.
*   **Integration with `ChainBuilder`:** For more complex agent setups or when agents need to invoke predefined chains.
