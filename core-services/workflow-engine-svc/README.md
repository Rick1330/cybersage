# Workflow Engine Service

The `Workflow Engine Service` (`core-services/workflow-engine-svc/`) is a vital component of the CyberSage platform, responsible for orchestrating complex, multi-step cybersecurity workflows. These workflows can involve sequences of AI agent tasks, security tool executions, conditional logic, and potentially human interactions.

## Table of Contents

1.  [Purpose](#1-purpose)
2.  [Key Responsibilities](#2-key-responsibilities)
3.  [Core Concepts](#3-core-concepts)
    -   [Workflow Definitions](#workflow-definitions)
    -   [Workflow Instance](#workflow-instance)
    -   [Workflow Step](#workflow-step)
    -   [State Management](#state-management)
4.  [API Overview](#4-public-api-overview)
5.  [Code Examples & Usage](#5-code-examples--usage)
    -   [Running the Service](#running-the-service)
    -   [Conceptual Workflow Definition](#conceptual-workflow-definition)
    -   [Triggering a Workflow](#triggering-a-workflow)
6.  [Error Handling & Retries](#6-error-handling--retries)
7.  [Integration with Other Components](#7-integration-with-other-core-components)
8.  [Configuration](#8-configuration)
9.  [Future Enhancements](#9-future-enhancements)

---

## 1. Purpose

The primary purpose of the `Workflow Engine Service` is to provide a robust and flexible system for defining, executing, and managing the lifecycle of automated security assessment workflows. It allows for the automation of complex processes that would otherwise require manual coordination of multiple tools and tasks.

---

## 2. Key Responsibilities

*   **Workflow Definition Management:** Loading and parsing workflow definitions. These definitions are expected to be stored in a structured format (e.g., YAML or JSON) within the main `/workflows` directory of the repository. *(Assumption: The exact format and location are based on common practice, as direct evidence from `/workflows` is not available).*
*   **Workflow Execution:** Instantiating `SecurityWorkflow` objects from definitions and managing their execution flow as defined in `workflow_engine.py`. This includes sequential execution of steps.
*   **State Management:** Tracking the status (`WorkflowStatus`, `WorkflowStepStatus`) and results of running and completed workflow instances and their individual steps. The `SecurityWorkflow` class in `workflow_engine.py` maintains this state in memory for an instance. *(Note: Persistent state management across service restarts would typically require a database, which is not explicitly shown in `workflow_engine.py` but is a common requirement for robust workflow engines).*
*   **Task Coordination:** Managing the execution of individual `WorkflowStep` tasks, which involve invoking specific tools (`BaseTool` instances) with given parameters.
*   **Error Handling & Retries:** Managing failures within workflow steps, including executing retries with exponential backoff as implemented in `_execute_step` in `workflow_engine.py`.
*   **Context Management:** Interacting with the `ContextManager` (`core/context_manager.py`) to create and update context associated with a workflow run.
*   **Reporting & Logging:** Providing status and results of workflow executions (via `get_status()` and `get_results()` methods). It heavily relies on the `LoggingService` for audit trails.

---

## 3. Core Concepts

### Workflow Definitions
Workflows are predefined sequences of operations. While the exact structure of definitions in the `/workflows` directory is not detailed, they conceptually include:
*   **Name & Description:** Metadata for the workflow.
*   **Steps:** An ordered list of tasks to be performed. Each step would define:
    *   The tool or agent action to execute.
    *   Input parameters for the tool/action.
    *   Conditions for execution (optional).
    *   Retry and timeout configurations.
*   **Transitions:** Logic defining how the workflow moves from one step to the next (currently sequential in `workflow_engine.py`).
*   **Input/Output Schema:** Definition of data expected by the workflow and data it produces.

### Workflow Instance
A `SecurityWorkflow` object represents a single, unique execution of a workflow definition, identified by a `workflow_id` (UUID). It maintains its own state, start/end times, and results.

### Workflow Step
A `WorkflowStep` object represents an individual unit of work within a workflow. It includes the tool to be run (`BaseTool`), parameters, conditions, retry/timeout settings, and its own status and results.

### State Management
The engine manages the state of workflows and steps using enums like `WorkflowStatus` and `WorkflowStepStatus`. Each `SecurityWorkflow` instance holds the state of its steps and overall progress. For persistence beyond the life of a single service instance, a database would typically be used to store this state. *(Note: `workflow_engine.py` does not show database integration for state persistence).*

---

## 4. Public API Overview

The `workflow_engine.py` code primarily defines Python classes and methods for internal use. It does not explicitly set up an HTTP server (FastAPI, Flask, etc.) as `main.py` is empty.

Therefore, this service might be:
*   **Used as a library:** Other services could import `SecurityWorkflow` and related classes directly to execute workflows.
*   **Integrated via a message queue:** It might listen for messages (e.g., from RabbitMQ via Celery, or Redis streams) that trigger workflow executions.
*   **Expose a gRPC or other RPC interface:** (No evidence of this currently).

Key methods available on a `SecurityWorkflow` instance include:
*   `execute()`: Starts or resumes the workflow.
*   `get_status()`: Returns the current status of the workflow and its steps.
*   `get_results()`: Returns the final results of all steps in a completed workflow.
*   `cancel()`: Attempts to cancel a running workflow.
*   `pause()`: Pauses a running workflow.
*   `resume()`: Resumes a paused workflow.

---

## 5. Code Examples & Usage

### Running the Service
*(Assumption: Since `Dockerfile` and `main.py` are empty, the exact method of running this as a standalone service is unclear. If it's run as a worker or library, deployment instructions would vary.)*

If it were to be run as a script (less likely for a "service"):
```bash
# Navigate to the service directory
cd core-services/workflow-engine-svc

# Potentially run a script that initializes and starts workflows
# Example (conceptual - depends on actual entry point if any):
# python -m workflow_engine --workflow-name "PhishingAnalysisWorkflow"
```
More commonly, its classes would be instantiated and used by another service, or it would be part of a worker process.

### Conceptual Workflow Definition
Based on `WorkflowStep` and `SecurityWorkflow` classes, a workflow is defined programmatically in Python.

```python
# Conceptual Example (actual definitions might be in YAML/JSON in /workflows and parsed into these objects)
from core.context_manager import ContextManager # Assuming availability
from services.logging_service import LoggingService # Assuming availability
from tools.nmap_tool import NmapTool # Example tool
from tools.reporting_tool import ReportingTool # Example tool
from core-services.workflow-engine-svc.workflow_engine import WorkflowStep, SecurityWorkflow

# Assuming context_manager and logging_service are initialized
context_mgr = ContextManager(...)
log_svc = LoggingService(...)

# Define Steps
step1 = WorkflowStep(
    name="NetworkScan",
    tool=NmapTool(), # Instance of a BaseTool
    params={"target": "scanme.nmap.org", "scan_type": "basic"},
    retry_count=2,
    timeout=600
)

step2 = WorkflowStep(
    name="GenerateReport",
    tool=ReportingTool(), # Instance of a BaseTool
    params={"input_data_step": "NetworkScan", "report_type": "summary"},
    conditions=[lambda: step1.status == WorkflowStepStatus.COMPLETED and step1.result.get("open_ports")] # Condition based on step1 result
)

# Create Workflow
my_workflow = SecurityWorkflow(
    name="BasicScanAndReport",
    description="Runs an Nmap scan and generates a report.",
    steps=[step1, step2],
    context_manager=context_mgr,
    logging_service=log_svc
)

# Execute workflow (typically this would be triggered by an API call or event)
# async def run():
#     results = await my_workflow.execute()
#     print(results)
# asyncio.run(run())
```

### Triggering a Workflow
Workflows would typically be triggered by:
*   **API Call:** An endpoint in the main `Backend API` (`interfaces/api/`) could receive a request to start a specific workflow by name or ID. This API endpoint would then interact with the Workflow Engine Service.
*   **Event-Driven:** An event on a message bus (e.g., a new threat intelligence feed) could trigger a relevant workflow.
*   **Scheduled Tasks:** A scheduler (potentially `core-services/scheduler-svc/` or Celery Beat) could initiate workflows at predefined times.

---

## 6. Error Handling & Retries

*   **Step Failures:** Individual `WorkflowStep` executions are retried based on their `retry_count` parameter using an exponential backoff strategy (seen in `_execute_step`).
*   **Timeouts:** Steps can timeout based on their `timeout` parameter.
*   **Workflow Errors:** If a step ultimately fails after retries or a timeout, it raises a `WorkflowError`, which causes the entire `SecurityWorkflow` to be marked as `FAILED`.
*   **Cleanup:** `WorkflowStep` can have an optional `cleanup` awaitable function that is called if the step fails.
*   **Logging:** Failures and retries are logged via the `LoggingService`.

---

## 7. Integration with Other Components

*   **`core/context_manager.py`:** Used to create and manage contextual information throughout the workflow lifecycle.
*   **`services/logging_service.py`:** Used extensively for audit logging of workflow and step events (start, completion, failure, cancellation, etc.).
*   **`tools/` (via `BaseTool`):** Individual workflow steps execute tools derived from `BaseTool`. This implies integration with the broader tool execution framework, including `tool-execution-runtimes/`.
*   **`interfaces/api/`:** Likely the primary way workflows are initiated (e.g., by user request or by other services). The API service would then call upon the Workflow Engine Service.
*   **Databases:** *(Implied for persistent state)* For storing workflow definitions (if not just from files), current state of running/completed workflows, and detailed results.
*   **`tasks/` (Celery):** *(Potential integration)* While not explicitly shown in `workflow_engine.py`, Celery could be used by this service to offload long-running workflow steps or to trigger workflows themselves.
*   **`core-services/scheduler-svc/`:** *(Potential integration)* For scheduling workflows to run at specific times or intervals.

---

## 8. Configuration

*(Assumption: Based on typical service needs, as `pyproject.toml` and `Dockerfile` are empty.)*
Key configuration items would likely include:
*   **Database Connection String:** If a database is used for state persistence.
*   **Logging Service Configuration:** Endpoint or settings for the `LoggingService`.
*   **Context Manager Configuration:** Settings for the `ContextManager`.
*   **Tool Configuration:** Paths or settings required by specific tools used in workflows.
*   **Celery Broker/Backend URL:** If integrated with Celery.
*   **Workflow Definition Source:** Path to the `/workflows` directory or database connection for definitions.

These would typically be managed via environment variables or a configuration file.

---

## 9. Future Enhancements

*   **Visual Workflow Editor Integration:** Allow users to define and modify workflows using a graphical interface.
*   **Persistent State Management:** Implement robust state persistence using a database (e.g., PostgreSQL, Redis) to allow workflows to survive service restarts and scale horizontally.
*   **Advanced Conditional Logic:** Support more complex branching, looping, and conditional execution within workflows.
*   **Human-in-the-Loop Steps:** Allow workflows to pause and wait for human input or approval before proceeding.
*   **Parallel Step Execution:** Enable parallel execution of independent workflow steps for improved performance.
*   **Enhanced Reporting & Analytics:** Provide more detailed analytics and visualizations of workflow execution metrics.
*   **Workflow Versioning:** Support for multiple versions of workflow definitions.
*   **Integration with External Event Sources:** Trigger workflows from a wider range of external events or systems.
*   **More Sophisticated Scheduler Integration:** Deeper integration with `core-services/scheduler-svc/` for complex scheduling patterns.
```
