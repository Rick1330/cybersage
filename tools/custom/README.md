# Adding Custom Tools to CyberSage

CyberSage is designed to be extensible, allowing users and developers to integrate their own custom tools, scripts, or API clients into the platform. This guide provides instructions and best practices for creating and registering new tools.

## Overview

Custom tools allow you to extend CyberSage's capabilities beyond the built-in toolset. You can wrap existing command-line utilities, interact with proprietary APIs, or implement unique analytical functions that your AI agents can then leverage.

The core requirement is to create a Python class that adheres to the `BaseTool` interface used within CyberSage (typically based on LangChain's `BaseTool`).

## Steps to Create a Custom Tool

1.  **Choose a Location:**
    *   For tools intended for general inclusion in the main CyberSage repository (subject to contribution review), place your tool file directly within the `/tools` directory (e.g., `/tools/my_scanner_tool.py`).
    *   For user-specific or locally developed tools not intended for merging into the main repo, you might create a separate directory (e.g., `/custom_tools`) and configure CyberSage to load tools from there (this loading mechanism may need specific implementation in the tool registry/discovery process). This guide assumes placement within `/tools` for contribution.

2.  **Create the Tool File:**
    *   Create a new Python file (e.g., `my_custom_tool.py`).

3.  **Define the Tool Class:**
    *   Import the necessary base class:
        ```python
        from langchain_core.tools import BaseTool
        # Or potentially: from tools.base_tool import CustomBaseTool if CyberSage uses a custom base
        from pydantic import BaseModel, Field # For input schema
        from typing import Type # For args_schema type hint
        ```
    *   Define your class, inheriting from `BaseTool`:
        ```python
        class MyCustomToolInput(BaseModel):
            """Input schema for MyCustomTool."""
            target_host: str = Field(description="The hostname or IP address to target.")
            api_key: str = Field(description="API key for the custom service.")
            # Add other parameters needed by your tool

        class MyCustomTool(BaseTool):
            """
            A brief description of what MyCustomTool does.
            This description is shown to the LLM.
            """
            name: str = "my_custom_tool"
            description: str = (
                "Use this tool to interact with the My Custom Service API. "
                "Provide the target_host and api_key. "
                "It returns specific metrics about the host."
            )
            args_schema: Type[BaseModel] = MyCustomToolInput

            def _run(self, target_host: str, api_key: str, **kwargs) -> str:
                """Synchronous execution logic."""
                print(f"Executing MyCustomTool synchronously for {target_host}")
                # --- Implement your tool's logic here ---
                # Example: Make an API call using target_host and api_key
                # result = my_custom_api_client.get_metrics(target_host, api_key)
                # return f"Metrics for {target_host}: {result}"
                # -----------------------------------------
                # Placeholder implementation:
                if not api_key:
                    raise ValueError("API key is required for MyCustomTool.")
                return f"Synchronous result for {target_host} using key ending in ...{api_key[-4:]}"

            async def _arun(self, target_host: str, api_key: str, **kwargs) -> str:
                """Asynchronous execution logic."""
                print(f"Executing MyCustomTool asynchronously for {target_host}")
                # --- Implement your tool's async logic here ---
                # Example: Use httpx or aiohttp for async API calls
                # result = await my_async_custom_api_client.get_metrics(target_host, api_key)
                # return f"Metrics for {target_host}: {result}"
                # --------------------------------------------
                # Placeholder implementation:
                if not api_key:
                    raise ValueError("API key is required for MyCustomTool.")
                # Simulate async work
                import asyncio
                await asyncio.sleep(0.1)
                return f"Asynchronous result for {target_host} using key ending in ...{api_key[-4:]}"

            # Optional: Add helper methods specific to your tool
        ```

4.  **Implement Logic:**
    *   Fill in the `_run` (synchronous) and `_arun` (asynchronous) methods with the actual logic for your tool.
    *   Prioritize implementing `_arun` if your tool involves I/O operations (network requests, file access, subprocesses) to avoid blocking CyberSage's main async event loop. If only `_run` is implemented, LangChain might wrap it to run in a thread pool when called asynchronously, but a native async implementation is usually better.

5.  **Define Input Schema (`args_schema`):**
    *   Create a Pydantic `BaseModel` defining the expected input arguments, their types, and descriptions (using `Field(description=...)`). This enables automatic validation and helps the LLM understand how to structure the `Action Input`.

6.  **Write Clear `name` and `description`:**
    *   `name`: Use a concise, unique, snake_case name.
    *   `description`: Write a clear and detailed description. This is **critical** as the LLM relies heavily on this to decide when and how to use your tool. Explain what it does, what input it needs (referencing the `args_schema` fields), and what it returns.

7.  **Follow Security Guidelines:**
    *   Carefully review and implement the practices outlined in `/tools/SECURITY_GUIDELINES.md`, especially regarding input sanitization, command injection (if applicable), and credential handling.

8.  **Add Tests:**
    *   Create unit tests for your tool in the `/tests/tools/` directory (e.g., `test_my_custom_tool.py`).
    *   Test input validation (`args_schema`).
    *   Test the core logic of `_run` and `_arun`. Mock external dependencies (API calls, subprocesses) appropriately.
    *   Test error handling scenarios.

9.  **Register the Tool:**
    *   Make CyberSage aware of your new tool. The exact mechanism depends on how tool discovery is implemented:
        *   **Option A (Manual Import/Registration):** You might need to import your tool class in a central registry file (e.g., `/tools/__init__.py` or a dedicated registry module) and add an instance to a list of available tools.
        *   **Option B (Dynamic Loading):** If CyberSage uses dynamic loading (e.g., scanning the `/tools` directory), ensure your file and class follow the expected naming conventions.
    *   Consult the main project documentation or code (`AgentManager`, tool loading logic) to determine the correct registration method.

10. **Update Documentation:**
    *   Add an entry for your new tool in `/tools/tool_registry.md`, following the format of existing entries.

## Testing Custom Tools

*   **Unit Tests:** Use `pytest` and mocking libraries (`unittest.mock`, `pytest-mock`) to test your tool class in isolation.
*   **Integration Tests:** If your tool interacts with external services, write integration tests (potentially marked to be skipped in standard CI) that require those services to be available or mocked at a higher level.
*   **Agent Testing:** Manually test your tool by creating an agent equipped with it and giving it tasks that should trigger its use. Observe the agent's reasoning (`Thought` process if using ReAct) and the tool's execution and output. Use the `dry_run` mode if implemented.

By following these steps, you can effectively extend CyberSage with your own specialized capabilities. Remember to prioritize security and clear documentation for your custom tools.
