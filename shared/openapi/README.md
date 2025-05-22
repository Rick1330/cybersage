# OpenAPI Specifications

This directory stores the OpenAPI Specification (OAS) files for the CyberSage platform's REST APIs. The primary API definition is `cybersage-api-v1.oas.yaml`.

## Purpose

The OpenAPI specification provides a standardized, language-agnostic way to:
*   **Define API Contracts:** Describe endpoints, operations, request/response payloads, authentication methods, etc.
*   **Generate API Documentation:** Serve as a source for generating interactive API documentation (e.g., using Swagger UI, Redoc). This is planned for the Docusaurus site.
*   **Generate Client SDKs:** Enable automatic generation of client libraries in various programming languages.
*   **Facilitate API Testing:** Provide a contract for API testing tools.

## Current Specifications

*   **`cybersage-api-v1.oas.yaml`**: Defines Version 1 of the main CyberSage external API, exposed via the API Gateway.

## Usage & Management

*   **Authoring:** The OAS file can be edited manually or generated/updated using API design tools.
*   **Validation:** It's recommended to validate the OAS file against the OpenAPI specification using linters or validators.
*   **Integration:**
    *   The API Gateway (`api-gateway/`) implements this specification.
    *   The backend API (`interfaces/api/`) provides the underlying implementation for the operations defined here.
    *   The Docusaurus documentation site will integrate this specification for a browsable API reference (see `docs/src/api_reference/README.md`).

---
*This document and the OpenAPI specifications should be updated whenever the API contract changes.*
