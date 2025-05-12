# CyberSage Core Engine

This directory contains the central intelligence and orchestration logic for the CyberSage platform. It's responsible for managing AI agents, constructing interaction flows (chains), handling conversational context, and defining how the AI interacts with tools and data.

## Overview

The core components work together to enable AI-driven cybersecurity tasks:

1.  **Prompt Templates (`prompt_templates.py`):** Define the structured instructions given to the Large Language Model (LLM) for various security tasks (e.g., scanning, analysis, reporting). These templates ensure consistent and effective AI behavior.
2.  **Chain Builder (`chain_builder.py`):** Assembles sequences of LLM calls and tool executions using frameworks like LangChain. This allows for multi-step reasoning and complex workflow construction involving AI analysis and practical tool use.
3.  **Agent Manager (`agent_manager.py`):** Creates, manages, and orchestrates AI agents. Agents are equipped with specific tools and prompts, enabling them to perform specialized functions (e.g., a scanning agent, an investigation agent).
4.  **Context Manager (`context_manager.py`):** Handles the state and memory associated with agent interactions. It ensures agents remember previous steps, maintain security context, and manage session data, often interacting with the `MemoryService`.

## Interaction Flow

A typical interaction involves the following flow within the core engine:

1.  **Task Reception:** An incoming task (e.g., from the API or CLI) is received by the system.
2.  **Agent Orchestration (`Agent Manager`):**
    *   The `Agent Manager` selects an existing agent or creates a new one suitable for the task.
    *   It initiates the agent's execution process.
3.  **Chain Construction (`Chain Builder`):**
    *   The agent, often with the help of the `Chain Builder`, assembles a sequence of steps. These steps can involve:
        *   Calls to the Large Language Model (LLM).
        *   Execution of specific tools.
4.  **LLM Interaction (using `Prompt Templates`):**
    *   If an LLM call is needed, `Prompt Templates` are used to structure the input to the LLM, ensuring clear instructions and context.
5.  **Contextualization (`Context Manager` & `Memory Service`):**
    *   The `Context Manager` retrieves relevant conversational history, previous findings, or session state from the `Memory Service`.
    *   This context is provided to the agent and/or the LLM to inform its reasoning and actions.
6.  **Tool Execution (via Tool Wrappers):**
    *   If a tool is required, the agent invokes the appropriate tool wrapper located in the `/tools` directory.
    *   The `Context Manager` might also provide specific context or parameters for tool execution.
7.  **Result Processing:**
    *   Outputs from the LLM and the executed tools are collected and processed by the agent.
8.  **State Update (`Context Manager` & `Memory Service`):**
    *   The `Context Manager` updates the session state, including new findings or conversational turns, by saving them to the `Memory Service`.
9.  **Response Generation:**
    *   The final result or response is formulated and sent back to the originating interface (API/CLI).

This flow allows CyberSage to handle complex, multi-step tasks by combining AI reasoning with practical tool execution and maintaining relevant context throughout the process.
## Key Components

*   **[`agent_manager.py`](./agent_manager.md):** Manages the lifecycle and execution of AI agents. *(Detailed docs pending)*
*   **[`prompt_templates.py`](./prompt_templates.md):** Contains predefined prompt structures for guiding LLM behavior. *(Detailed docs pending)*
*   **[`chain_builder.py`](./chain_builder.md):** Responsible for assembling LangChain chains for specific tasks. *(Detailed docs pending)*
*   **[`context_manager.py`](./context_manager.md):** Handles session state, memory, and security context. *(Detailed docs pending)*

Refer to the individual documentation files linked above for detailed explanations of each component's API, usage, and configuration.
