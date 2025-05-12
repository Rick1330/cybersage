# CyberSage Tools Layer

This directory contains the implementation of tools that CyberSage agents can utilize to interact with the external environment, gather information, or perform actions. These tools are typically wrappers around standard cybersecurity command-line utilities, APIs, or internal platform functions.

## Table of Contents

1.  [Purpose](#1-purpose)
2.  [Core Abstraction: `BaseTool`](#2-core-abstraction-basetool)
3.  [Tool Registry & Discovery](#3-tool-registry--discovery)
4.  [Built-in Tools](#4-built-in-tools)
5.  [Security Considerations](#5-security-considerations)
6.  [Adding Custom Tools](#6-adding-custom-tools)

---

## 1. Purpose

The primary goals of the tools layer are:

*   **Encapsulation:** Wrap the complexities of using external tools or APIs within a consistent Python interface.
*   **Standardization:** Provide a uniform way for AI agents (e.g., LangChain agents) to discover and invoke tools.
*   **Security:** Implement necessary safeguards, input validation, and potentially sandboxing when executing external commands or interacting with APIs.
*   **Extensibility:** Make it straightforward to add new tools to expand CyberSage's capabilities.
*   **Parsing & Formatting:** Handle the parsing of raw tool output into formats more easily understood by LLMs or subsequent workflow steps (e.g., converting Nmap XML to JSON).

---

## 2. Core Abstraction: `BaseTool`

Most tools within CyberSage should inherit from a base class, likely LangChain's `BaseTool` or a custom derivative (`tools/base_tool.py`). This base class typically requires subclasses to implement specific methods and properties:

*   **`name` (Property):** A unique, descriptive name for the tool (e.g., `nmap_scanner`, `shodan_lookup`). This is how the agent identifies the tool.
*   **`description` (Property):** A detailed description of what the tool does, its parameters, and expected input/output. This description is crucial as it's provided to the LLM to help it decide *when* and *how* to use the tool.
*   **`_run(self, *args, **kwargs)` (Method):** The synchronous execution logic for the tool. This method performs the actual work (e.g., running a subprocess, making an API call).
*   **`_arun(self, *args, **kwargs)` (Method):** The asynchronous version of the execution logic, preferred for non-blocking operations, especially within an async framework like FastAPI.
*   **`args_schema` (Property, Optional):** A Pydantic model defining the expected input arguments for the tool, enabling automatic validation and clear documentation.

By adhering to this interface, all tools become interchangeable from the agent's perspective.

---

## 3. Tool Registry & Discovery

CyberSage needs a mechanism to make tools available to agents. This might involve:

*   **Explicit Instantiation:** Creating instances of tool classes and passing them directly to the `AgentManager` when an agent is created.
*   **Dynamic Loading:** A registry system that can discover and load tool classes based on configuration or naming conventions.
*   **Tool Service:** A dedicated service responsible for managing and providing access to available tools.

The `AgentManager` uses the `name` and `description` properties of the available tools to inform the LLM about the agent's capabilities.

*See `/tools/tool_registry.md` for a catalog of available tools.*

---

## 4. Built-in Tools

This directory contains implementations for various standard tools, such as:

*   `nmap_tool.py`: Wrapper for the Nmap network scanner.
*   `whois_tool.py`: Wrapper for WHOIS lookups.
*   `shodan_tool.py`: Wrapper for the Shodan API.
*   `virustotal_tool.py`: Wrapper for the VirusTotal API.
*   `dns_lookup_tool.py`: Wrapper for DNS query tools (e.g., `dig`, `nslookup`).
*   *(Add more as they are implemented)*

Each tool file typically contains the class definition inheriting from `BaseTool` and implementing the required methods and properties.

---

## 5. Security Considerations

Executing external tools or interacting with APIs based on LLM-generated input carries significant security risks. Key considerations include:

*   **Command Injection:** Preventing malicious input from altering the intended command executed by tools like Nmap.
*   **Input Sanitization:** Validating and sanitizing all inputs passed to tools.
*   **Least Privilege:** Running tools with the minimum necessary permissions.
*   **Sandboxing:** Executing potentially risky tools within isolated environments (e.g., Docker containers via `tool-execution-runtimes/`).
*   **Resource Limits:** Applying timeouts and resource constraints (CPU, memory) to prevent DoS conditions.
*   **API Key Security:** Securely managing and using API keys required by tools.

*See `/tools/SECURITY_GUIDELINES.md` for detailed security practices for tool development.*

---

## 6. Adding Custom Tools

CyberSage is designed to be extensible. To add a new custom tool:

1.  Create a new Python file in the `/tools` directory (e.g., `my_custom_tool.py`).
2.  Define a class that inherits from `BaseTool` (or the project's custom base).
3.  Implement the required properties (`name`, `description`) and methods (`_run`, `_arun`).
4.  Optionally define an `args_schema` using Pydantic for input validation.
5.  Ensure the tool follows the security guidelines.
6.  Register or make the new tool available to the `AgentManager` (the exact mechanism depends on the registry/discovery implementation).

*See `/tools/custom/README.md` for a template and detailed guide on creating custom tools.*
