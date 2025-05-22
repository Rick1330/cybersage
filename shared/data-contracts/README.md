# Data Contracts

This directory contains shared data contracts, schemas, and interface definitions for the CyberSage platform. These contracts ensure consistency in data structures exchanged between different microservices and components.

## Purpose

Maintaining well-defined data contracts is crucial for:
*   **Interoperability:** Ensuring that services can communicate reliably.
*   **Clear Interfaces:** Providing clear expectations for data producers and consumers.
*   **Decoupling:** Allowing services to evolve independently as long as they adhere to the contracts.
*   **Validation:** Facilitating data validation at service boundaries.

## Types of Contracts

This directory may include:
*   **Protocol Buffer Definitions (`.proto`):** For gRPC-based communication or efficient data serialization.
*   **JSON Schemas (`.json`):** For validating JSON payloads in REST APIs or message queues.
*   **Avro Schemas (`.avsc`):** For event-driven architectures with Kafka or similar.
*   **Shared Python Pydantic Models:** Located in `shared/python-common/` if applicable, defining DTOs.
*   **TypeScript Interfaces/Types:** Located in `shared/js-common-types/` for frontend and Node.js services.

*(Adjust the list above based on actual or intended contract types. If none are evident yet, keep it general).*

## Usage

*   Services should import or generate code from these contracts to define their data exchange formats.
*   Changes to data contracts should be versioned and managed carefully to avoid breaking compatibility between services. Consider using a schema registry if the number of contracts grows.

## Structure

*   Currently, specific contract files or subdirectories are not present directly within `shared/data-contracts/`.
*   If contracts are primarily defined within shared libraries like `shared/python-common/` or `shared/js-common-types/`, users should refer to those directories. Future dedicated contract files (e.g., `.proto`, `.json` schemas) would be organized into appropriate subdirectories here.

---
*This documentation should be updated as new data contracts are defined or existing ones are modified.*
