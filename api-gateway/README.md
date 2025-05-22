# API Gateway

The `API Gateway` (`api-gateway/`) is a crucial component of the CyberSage platform, serving as the primary and unified entry point for all external client requests. This includes interactions from the Web UI (`ui-web/`), Mobile UI (`ui-mobile/`), Command Line Interface (CLI), and any third-party integrations. It is built using the NestJS framework.

## Table of Contents

1.  [Purpose](#1-purpose)
2.  [Key Responsibilities](#2-key-responsibilities)
3.  [Core Concepts](#3-core-concepts)
    -   [NestJS Framework](#nestjs-framework)
    -   [Modules](#modules)
    -   [Guards](#guards)
    -   [Interceptors](#interceptors)
    -   [GraphQL Federation](#graphql-federation)
    -   [WebSockets](#websockets)
4.  [Configuration](#4-configuration)
5.  [Running Locally](#5-running-locally)
6.  [Error Handling](#6-error-handling)
7.  [Integration with Other Components](#7-integration-with-other-core-components)
8.  [Future Enhancements](#8-future-enhancements)

---

## 1. Purpose

The primary purpose of the `API Gateway` is to provide a secure, consistent, and managed interface for all client interactions with the CyberSage backend services. It abstracts the complexity of the microservices architecture, offering a single point of contact.

Key functions include:
*   **Centralized Request Handling:** Managing all incoming HTTP/S, GraphQL, and WebSocket traffic.
*   **Security Enforcement:** Offloading authentication and coarse-grained authorization from backend services.
*   **Traffic Management:** Implementing rate limiting and potentially caching to protect backend resources.
*   **Decoupling Clients from Services:** Allowing backend services to evolve without directly impacting client-side integrations.

---

## 2. Key Responsibilities

*   **Request Routing:** Dynamically routes incoming requests to the appropriate backend microservices, primarily the main `Backend API` (`interfaces/api/`).
*   **Authentication:** Verifies the identity of clients by validating credentials, typically JWTs. This is likely done in coordination with the `Identity Service` (`platform-services/identity-svc/`). The presence of `api-gateway/src/modules/auth/` confirms dedicated authentication logic.
*   **Authorization:** Enforces access control policies, determining whether an authenticated client has permission to access the requested resource or perform an operation. This is often implemented using NestJS Guards.
*   **Rate Limiting:** Protects backend services from overload and abuse by limiting the number of requests a client can make in a given time period. *(Assumption: Standard NestJS rate limiting modules would be used).*
*   **SSL/TLS Termination:** Handles HTTPS connections, decrypting incoming traffic before forwarding requests to internal services over a secure internal network, and encrypting responses sent back to clients.
*   **Request/Response Transformation:** May modify incoming requests or outgoing responses, such as adding headers, logging, or transforming data formats. The `api-gateway/src/interceptors/logging.interceptor.ts` indicates request/response logging.
*   **API Aggregation/Composition (Potentially):** While not explicitly confirmed, a gateway can combine responses from multiple backend services into a single client response. The `graphql_federation` module suggests this capability for GraphQL endpoints.

---

## 3. Core Concepts

### NestJS Framework
The API Gateway is built using [NestJS](https://nestjs.com/), a progressive Node.js framework for building efficient, reliable, and scalable server-side applications. It uses TypeScript and is heavily inspired by Angular.

### Modules
NestJS organizes code into modules. Key modules identified from the directory structure include:
*   `AppModule` (`api-gateway/src/app.module.ts`): The root module. *(Note: File content was reported as empty, details are assumed based on NestJS conventions).*
*   `AuthModule` (`api-gateway/src/modules/auth/auth.module.ts`): Handles authentication logic.
*   Other feature modules may exist for routing to different backend services.

### Guards
NestJS Guards are responsible for determining whether a given request should be handled by the route handler or not, based on certain conditions (e.g., authentication status, roles/permissions). They are critical for implementing authorization.

### Interceptors
Interceptors in NestJS provide a way to bind extra logic to requests and responses. They can transform data, log requests/responses (as seen with `logging.interceptor.ts`), implement caching, etc.

### GraphQL Federation
The presence of `api-gateway/src/graphql_federation/index.ts` suggests the API Gateway may support GraphQL Federation. This allows multiple underlying GraphQL services to be combined into a single, unified GraphQL schema exposed to clients.

### WebSockets
The `api-gateway/src/sockets/websocket.gateway.ts` indicates that the API Gateway handles WebSocket connections, enabling real-time, bidirectional communication between clients and the server for features like live notifications or interactive sessions.

---

## 4. Configuration

Key configuration points for the API Gateway likely include:
*   **Port and Environment:** Configured via environment variables, as seen in `api-gateway/src/config/app.config.ts` (e.g., `PORT`, `NODE_ENV`).
*   **Backend Service URLs:** Environment variables or configuration files would specify the addresses of downstream services like the main Backend API (`interfaces/api/`).
*   **JWT Secrets/Keys:** Securely configured secrets for signing and validating JSON Web Tokens, likely managed via environment variables and used by the `AuthModule`.
*   **Rate Limiting Parameters:** Thresholds and duration for rate limiting.
*   **Logging Levels:** Configuration for the `LoggingInterceptor` and general application logging.
*   **CORS Policy:** Configuration for Cross-Origin Resource Sharing.

*(Note: Specifics depend on the content of `main.ts` and `app.module.ts` which were reported as empty.)*

---

## 5. Running Locally

To run the API Gateway locally for development (assuming standard NestJS project structure and scripts in `package.json`):
```bash
# Navigate to the API Gateway directory
cd api-gateway

# Install dependencies (if not already done)
npm install

# Run in development mode (with hot-reloading)
npm run start:dev
```
The gateway would then typically be accessible at `http://localhost:PORT` where `PORT` is defined in the configuration (e.g., 3000 from `app.config.ts`).

**Example Request Flow (Conceptual):**
1. Client sends `POST /api/v1/tasks` with a JWT to `http://<gateway-host>:<port>/api/v1/tasks`.
2. API Gateway receives the request.
3. The `AuthModule` guard validates the JWT (possibly interacting with `platform-services/identity-svc/`).
4. If authenticated and authorized, the gateway proxies the request to the main Backend API (`interfaces/api/`) at its internal address (e.g., `http://cybersage-backend-api:8000/tasks`).
5. The Backend API processes the request and returns a response.
6. The API Gateway receives the response from the backend and forwards it to the client, after any transformations by interceptors (e.g., logging).

---

## 6. Error Handling

The API Gateway is responsible for handling or consistently passing through various error types:
*   **401 Unauthorized:** If authentication fails (e.g., invalid or missing JWT).
*   **403 Forbidden:** If an authenticated user lacks permissions for a specific resource.
*   **404 Not Found:** If a route does not exist on the gateway or the downstream service returns a 404.
*   **429 Too Many Requests:** If rate limiting is triggered.
*   **5xx Server Errors:** If the gateway itself encounters an issue, or if a downstream service returns a 5xx error, the gateway should ideally return a standardized error response to the client, possibly masking internal error details.

Error responses should be structured (e.g., JSON) and avoid leaking sensitive information.

---

## 7. Integration with Other Core Components

The API Gateway is a central hub and interacts with several other components:

*   **`Backend API` (`interfaces/api/`):** This is the primary downstream service that the gateway routes most application-specific requests to.
*   **`Identity Service` (`platform-services/identity-svc/`):** Crucial for authentication, as the gateway likely relies on this service to validate JWTs and fetch user identity information.
*   **`Logging Service` (`services/logging_service.py` or a similar centralized logging solution):** The `logging.interceptor.ts` suggests that request and response metadata is logged, likely to a centralized logging system.
*   **User Interfaces (`ui-web/`, `ui-mobile/`):** These are the primary clients that send requests to the CyberSage platform via the API Gateway.
*   **CLI (`interfaces/cli.py`):** The CLI also acts as a client, making requests through the API Gateway.
*   **External Tools/Integrations:** Any third-party services or tools integrating with CyberSage would do so via the API Gateway.

---

## 8. Future Enhancements

*   **Advanced Caching:** Implement more sophisticated caching strategies (e.g., Redis-based) for frequently accessed, non-sensitive data to reduce load on backend services.
*   **Enhanced Metrics & Tracing:** Integrate more detailed metrics collection (e.g., Prometheus) and distributed tracing (e.g., OpenTelemetry) for better observability.
*   **Web Application Firewall (WAF) Integration:** Place a WAF in front of the API Gateway for protection against common web exploits (XSS, SQLi, etc.).
*   **Service Discovery Integration:** Dynamically discover backend service instances, especially in a more complex microservices environment.
*   **Request Schema Validation:** More rigorous validation of request payloads at the gateway level before forwarding.
*   **Circuit Breaking:** Implement circuit breaker patterns for more resilient routing to backend services.

```
