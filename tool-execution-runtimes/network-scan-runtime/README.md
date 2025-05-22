# Network Scan Runtime

The `Network Scan Runtime` (`tool-execution-runtimes/network-scan-runtime/`) is a specialized and sandboxed environment within the CyberSage platform, designed for the secure execution of network scanning tools. It ensures that potentially privileged or risky operations are isolated from the core platform and other services.

**Note:** *The `worker.py` for this runtime currently contains placeholder implementations. Specific details regarding supported tools, command execution, and output parsing are based on common practices for such a component and will need to be verified against the actual implementation as it evolves.*

## Table of Contents

1.  [Purpose](#1-purpose)
2.  [Key Responsibilities](#2-key-responsibilities)
3.  [Core Concepts](#3-core-concepts)
    -   [Sandboxing](#sandboxing)
    -   [Supported Tools](#supported-tools)
    -   [Task Queuing & Execution](#task-queuing--execution)
    -   [Configuration (`config.py`)](#configuration-configpy)
4.  [Interface / Invocation](#4-interface--invocation)
    -   [Input Format (Conceptual)](#input-format-conceptual)
    -   [Output Format (Conceptual)](#output-format-conceptual)
5.  [Deployment & Usage](#5-deployment--usage)
    -   [Packaging](#packaging)
    -   [Example Invocation (Conceptual)](#example-invocation-conceptual)
6.  [Error Handling](#6-error-handling)
7.  [Integration with Other Components](#7-integration-with-other-core-components)
8.  [Configuration Details](#8-configuration-details)
9.  [Future Enhancements](#9-future-enhancements)

---

## 1. Purpose

The primary purpose of the `Network Scan Runtime` is to provide a dedicated, secure, and controlled environment for executing network scanning tools (e.g., Nmap, Zmap). This isolation is crucial for:
*   **Security:** Preventing vulnerabilities or exploits in scanning tools from impacting the broader CyberSage platform.
*   **Stability:** Ensuring that resource-intensive scan operations do not degrade the performance of other core services.
*   **Compliance:** Facilitating adherence to security policies that may require separation of scanning infrastructure.

---

## 2. Key Responsibilities

*   **Tool Execution:** Securely running network scanning tools based on requests received from agents (via `core/agent_manager.py`) or workflows (via `core-services/workflow-engine-svc/`). *(Implementation in `worker.py` is currently a placeholder).*
*   **Parameter Handling:** Accepting parameters for scans (e.g., targets, ports, scan types, specific tool arguments) and translating them into appropriate command-line arguments for the chosen scanning tool.
*   **Sandboxing:** Providing an isolated environment for each scan job. *(Likely Docker-based, though not explicitly confirmed by current files).*
*   **Output Parsing (Potentially):** Parsing the raw output of scanning tools (e.g., Nmap XML, Zmap CSV) into a structured JSON format that can be easily consumed by other platform components. *(This would be part of the `NetworkScanWorker`'s `execute` method).*
*   **Resource Management (Potentially):** Managing resources such as CPU, memory, and network bandwidth for scan jobs, possibly leveraging container resource limits. The `config.py` settings (`max_concurrent_scans`, `timeout`) allude to this.
*   **Concurrency Control:** Managing the number of concurrent scans as specified in `config.py` (`max_concurrent_scans`).

---

## 3. Core Concepts

### Sandboxing
To ensure isolation, each network scanning task is expected to run within a sandboxed environment.
*   **Method:** Commonly achieved using containerization technologies like Docker. Each scan job (or worker instance) would run in its own container with restricted privileges and network access. *(This is an assumption as `Dockerfile` is not provided for this specific runtime).*
*   **Benefits:** Prevents direct access to the host system, limits the blast radius of potential tool exploits, and allows for defined resource allocation.

### Supported Tools
This runtime is designed to execute network scanning tools.
*   **Primary Tool (Assumed):** Nmap is a common and versatile network scanner.
*   **Other Potential Tools:** Zmap (for large-scale banner grabbing), Masscan, or other specialized network probing utilities.
*(The `worker.py` would need to be implemented to support specific tools and their command structures).*

### Task Queuing & Execution
Scan jobs are likely received and processed asynchronously.
*   **Mechanism (Assumed):** A message queue (e.g., Celery with RabbitMQ or Redis as a broker) is a common pattern. Tool wrappers in the main platform (e.g., `tools/nmap_tool.py`) would publish scan requests to a queue, and the `NetworkScanWorker` instances would consume from this queue.
*   **Concurrency:** The runtime manages concurrent execution based on `config.py`'s `max_concurrent_scans`.

### Configuration (`config.py`)
The runtime's behavior is configured via `tool-execution-runtimes/network-scan-runtime/config.py`. This file currently includes:
*   `max_concurrent_scans`: Maximum number of scans allowed to run simultaneously.
*   `timeout`: Default timeout for a scan job in seconds.
*   `retries`: Default number of retries for a failed scan job.

---

## 4. Interface / Invocation

*(This runtime likely does not expose a direct HTTP API. Instead, it's invoked internally, possibly via a message queue or direct method calls from trusted services if co-deployed.)*

### Input Format (Conceptual)
If consuming from a message queue, a typical scan request message might look like this:
```json
{
  "task_id": "unique_task_identifier_string",
  "tool": "nmap", // or "zmap", etc.
  "target": "scanme.nmap.org", // or "192.168.1.0/24"
  "scan_type": "SYN_SCAN", // Predefined type or direct arguments
  "ports": "22,80,443", // Optional
  "arguments": ["-A", "-T4"], // Additional tool-specific arguments
  "timeout_seconds": 3600, // Override default from config.py
  "retry_attempts": 2 // Override default from config.py
}
```

### Output Format (Conceptual)
Upon completion or failure, the runtime would typically return a structured result, possibly via another message queue or by updating a status in a database.
```json
{
  "task_id": "unique_task_identifier_string",
  "status": "completed", // or "failed", "timeout"
  "tool": "nmap",
  "target": "scanme.nmap.org",
  "results": {
    // Tool-specific structured output, e.g., parsed Nmap XML as JSON
    "host": "scanme.nmap.org",
    "ip": "45.33.32.156",
    "ports": [
      { "port_id": 22, "protocol": "tcp", "state": "open", "service": "ssh" },
      { "port_id": 80, "protocol": "tcp", "state": "open", "service": "http" }
    ],
    "raw_output_path": "s3://bucket/path/to/raw_output.xml" // Optional
  },
  "error_message": null // Or error details if status is "failed"
}
```

---

## 5. Deployment & Usage

### Packaging
*   **Method (Assumed):** This runtime is likely packaged as a Docker container. A `Dockerfile` (currently missing) would define its environment, dependencies (including the scanning tools like Nmap), and how the `NetworkScanWorker` is started.
*   It would be deployed as a standalone microservice or a set of worker instances.

### Example Invocation (Conceptual)
From a tool wrapper (e.g., `tools/nmap_tool.py`) within the main platform:
```python
# This is conceptual Python code, not part of the runtime itself
class NmapToolWrapper:
    def __init__(self, message_queue_publisher):
        self.publisher = message_queue_publisher

    async def execute_scan(self, target: str, scan_type: str, ports: str = None, arguments: list = None):
        task_id = str(uuid.uuid4())
        scan_request = {
            "task_id": task_id,
            "tool": "nmap",
            "target": target,
            "scan_type": scan_type,
            "ports": ports,
            "arguments": arguments or [],
            "timeout_seconds": 3600, # From config or user input
            "retry_attempts": 3     # From config or user input
        }
        # Publish to a specific queue, e.g., 'network_scan_jobs'
        await self.publisher.publish('network_scan_jobs', scan_request)
        return {"status": "queued", "task_id": task_id}

# Actual results would be received asynchronously, e.g., via another queue or webhook.
```

---

## 6. Error Handling

*   **Tool Errors:** If a scanning tool fails (e.g., command not found, invalid arguments, crashes), the `NetworkScanWorker` should capture stderr and report the error.
*   **Timeouts:** Scan jobs exceeding the configured `timeout` (from `config.py` or request) will be terminated.
*   **Retries:** Failed jobs may be retried based on the `retries` setting in `config.py`.
*   **Configuration Errors:** Invalid configuration in `config.py` or missing tool dependencies within the runtime environment.
*   **Reporting:** Errors are reported back to the calling service, typically including the `task_id` and a descriptive error message in the output structure.

---

## 7. Integration with Other Components

*   **`tools/*.py` (e.g., `tools/nmap_tool.py`):** These tool wrappers in the main platform are the primary clients of this runtime. They would format scan requests and send them to the runtime (likely via a message queue).
*   **`core/agent_manager.py`:** AI agents use tools, which in turn delegate execution to specialized runtimes like this one for network scanning operations.
*   **`core-services/workflow-engine-svc/`:** Workflows may include steps that trigger network scans via the appropriate tool wrappers, thus indirectly using this runtime.
*   **Message Queues (e.g., Celery, RabbitMQ, Redis Streams - Assumed):** Likely used for asynchronous job intake and potentially for returning results.
*   **`Logging Service` (`services/logging_service.py`):** The runtime should log its operational status, scan job progress, and errors to the centralized logging service.
*   **`Data Storage (e.g., S3, MinIO - Conceptual)`:** Raw output files from scans might be stored in an object storage service, with a reference in the results.

---

## 8. Configuration Details

The primary configuration is through `tool-execution-runtimes/network-scan-runtime/config.py`:
```python
CONFIG = {
    "max_concurrent_scans": 10, # Max simultaneous scans
    "timeout": 3600,            # Default job timeout in seconds (1 hour)
    "retries": 3                # Default retry attempts for failed jobs
}
```
Environment variables that would typically be needed for the runtime container (conceptual):
*   `MESSAGE_QUEUE_URL`: URL for connecting to the job queue (e.g., RabbitMQ, Redis).
*   `LOGGING_SERVICE_ENDPOINT`: Address of the centralized logging service.
*   `TOOL_PATHS_NMAP`: Path to Nmap binary if not in standard PATH.
*   `OUTPUT_STORAGE_CONFIG`: Configuration for storing raw scan outputs (e.g., S3 bucket details).

---

## 9. Future Enhancements

*   **Support for More Scanning Tools:** Add support for other tools like Zmap, Masscan, etc.
*   **Advanced Output Analysis:** Integrate basic analysis or vulnerability mapping directly within the runtime for common findings.
*   **Dynamic Scaling of Runtime Instances:** Automatically scale the number of runtime workers based on job queue length.
*   **Network Policy Enforcement:** More granular control over the network access of scan containers (e.g., egress filtering).
*   **User-Defined Scan Policies:** Allow users or the platform to define specific scan configurations and restrictions.
*   **Integration with a Secrets Management System:** For securely handling any credentials needed by tools within the runtime.
*   **Standardized Health Check Endpoint:** If run as a persistent service.
```
