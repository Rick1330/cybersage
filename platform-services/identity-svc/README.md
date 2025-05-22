# Identity Service

The `Identity Service` (`platform-services/identity-svc/`) is a foundational component of the CyberSage platform, responsible for managing user identities, authentication, and potentially authorization. It serves as the central authority for verifying users and issuing security tokens.

**Note:** *The source code for this service (beyond this README) was not available at the time of this documentation generation. Therefore, many details below are based on common practices for identity management services in a microservices architecture and will need to be verified against the actual implementation.*

## Table of Contents

1.  [Purpose](#1-purpose)
2.  [Key Responsibilities](#2-key-responsibilities)
3.  [Core Concepts](#3-core-concepts)
    -   [JSON Web Tokens (JWTs)](#json-web-tokens-jwts)
    -   [Password Hashing](#password-hashing)
    -   [Authentication Flows](#authentication-flows)
    -   [User Model](#user-model)
    -   [Roles & Permissions](#roles--permissions)
4.  [Public API Overview (Conceptual)](#4-public-api-overview-conceptual)
    -   [`POST /register`](#post-register)
    -   [`POST /login`](#post-login)
    -   [`POST /token/refresh`](#post-tokenrefresh)
    -   [`GET /users/me`](#get-usersme)
    -   [`POST /users/me/change-password`](#post-usersmechange-password)
5.  [Code Examples & Usage (Conceptual)](#5-code-examples--usage-conceptual)
    -   [Running the Service](#running-the-service)
    -   [Example API Calls](#example-api-calls)
6.  [Error Handling](#6-error-handling)
7.  [Integration with Other Components](#7-integration-with-other-core-components)
8.  [Configuration (Conceptual)](#8-configuration-conceptual)
9.  [Future Enhancements](#9-future-enhancements)

---

## 1. Purpose

The primary purpose of the `Identity Service` is to provide a centralized and secure system for:
*   Managing the lifecycle of user accounts.
*   Authenticating users accessing the CyberSage platform.
*   Issuing and validating security tokens (likely JWTs) for secure API access.
*   Potentially managing user roles and permissions for authorization decisions.

It decouples identity concerns from other services, allowing them to rely on a trusted authority.

---

## 2. Key Responsibilities

*   **User Registration:** Handling the creation of new user accounts, including validation of input data (e.g., username, email, password policies).
*   **User Authentication:** Verifying user credentials (e.g., username and password) against stored records.
*   **Token Management:**
    *   Issuing access tokens (and potentially refresh tokens) upon successful authentication.
    *   Validating tokens presented by clients.
    *   Managing token revocation and refresh mechanisms.
*   **Password Management:**
    *   Securely storing user passwords using strong cryptographic hashing algorithms.
    *   Providing mechanisms for users to change their passwords.
    *   Facilitating secure password reset processes.
*   **User Profile Management:** Storing and providing access to basic user profile information (e.g., user ID, username, email, associated roles).
*   **(Potentially) Role/Permission Management:** Defining roles (e.g., 'admin', 'analyst', 'viewer') and associating permissions with these roles. This information would then be used by other services to make authorization decisions.

---

## 3. Core Concepts

### JSON Web Tokens (JWTs)
JWTs are likely used as the primary mechanism for session management and API authentication.
*   **Access Tokens:** Short-lived tokens containing claims about the user (e.g., user ID, roles) used to authorize API requests.
*   **Refresh Tokens:** Longer-lived tokens used to obtain new access tokens without requiring the user to re-enter credentials. These must be stored securely by the client.

### Password Hashing
User passwords must never be stored in plaintext. Strong, salted hashing algorithms like bcrypt or Argon2 are standard practice for protecting password databases.

### Authentication Flows
*   **Registration:** New user provides details -> Service validates -> Hashes password -> Stores user record.
*   **Login:** User provides credentials -> Service validates against stored hash -> Issues JWT (access and refresh tokens).
*   **Token Refresh:** Client presents valid refresh token -> Service issues new access token.
*   **API Access:** Client includes access token in API request header -> API Gateway or service validates token with Identity Service (or using its public key).

### User Model
A data structure representing a user, typically including:
*   `user_id` (unique identifier)
*   `username`
*   `email`
*   `password_hash`
*   `roles` (list of associated roles)
*   `is_active` (boolean status)
*   Timestamps (`created_at`, `updated_at`)

### Roles & Permissions
*   **Roles:** Groups of users with similar access needs (e.g., "Administrator", "SecurityAnalyst").
*   **Permissions:** Specific actions a user can perform (e.g., "read:scan_results", "execute:workflow", "manage:users"). Roles are typically assigned a set of permissions. This information, often included in JWT claims, is used by other services to enforce access control.

---

## 4. Public API Overview (Conceptual)

*(Assuming a RESTful HTTP API based on common practice for such services. Endpoints and payloads are illustrative.)*

### `POST /register`
*   **Purpose:** Registers a new user.
*   **Request Body:** `{ "username": "newuser", "email": "newuser@example.com", "password": "StrongPassword123" }`
*   **Response (Success):** `201 Created` - `{ "user_id": "uuid", "username": "newuser", "email": "newuser@example.com" }`
*   **Response (Error):** `400 Bad Request` (e.g., validation errors, user already exists).

### `POST /login`
*   **Purpose:** Authenticates a user and returns tokens.
*   **Request Body:** `{ "username": "user", "password": "Password123" }`
*   **Response (Success):** `200 OK` - `{ "access_token": "jwt_access_token", "refresh_token": "jwt_refresh_token", "token_type": "Bearer" }`
*   **Response (Error):** `401 Unauthorized` (invalid credentials).

### `POST /token/refresh`
*   **Purpose:** Issues a new access token using a refresh token.
*   **Request Body:** `{ "refresh_token": "jwt_refresh_token" }`
*   **Response (Success):** `200 OK` - `{ "access_token": "new_jwt_access_token", "token_type": "Bearer" }`
*   **Response (Error):** `401 Unauthorized` (invalid or expired refresh token).

### `GET /users/me`
*   **Purpose:** Retrieves profile information for the authenticated user.
*   **Authorization:** Requires a valid access token.
*   **Response (Success):** `200 OK` - `{ "user_id": "uuid", "username": "user", "email": "user@example.com", "roles": ["analyst"] }`

### `POST /users/me/change-password`
*   **Purpose:** Allows an authenticated user to change their password.
*   **Authorization:** Requires a valid access token.
*   **Request Body:** `{ "current_password": "OldPassword123", "new_password": "NewStrongPassword456" }`
*   **Response (Success):** `204 No Content`
*   **Response (Error):** `400 Bad Request` (e.g., current password incorrect, new password policy violation), `401 Unauthorized`.

---

## 5. Code Examples & Usage (Conceptual)

### Running the Service
*(Specific instructions depend on the actual implementation, framework, and presence of a Dockerfile or deployment scripts, which are currently missing.)*

If it were a Python FastAPI service with Docker:
```bash
# Navigate to the service directory
# cd platform-services/identity-svc

# Build Docker image (assuming Dockerfile exists)
# docker build -t cybersage-identity-svc .

# Run Docker container
# docker run -d -p 8001:8001 --env-file .env cybersage-identity-svc
```
The service would then be accessible, for example, at `http://localhost:8001`.

### Example API Calls
```bash
# Login example using curl
curl -X POST http://localhost:8001/login \
     -H "Content-Type: application/json" \
     -d '{ "username": "testuser", "password": "password123" }'

# Get user profile (replace <ACCESS_TOKEN> with actual token)
curl -X GET http://localhost:8001/users/me \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

---

## 6. Error Handling

Common HTTP status codes returned by the Identity Service:
*   **200 OK / 201 Created / 204 No Content:** Successful operations.
*   **400 Bad Request:** Invalid input, validation errors (e.g., password too weak, email format incorrect, username taken).
*   **401 Unauthorized:** Authentication failed (e.g., invalid credentials, missing/invalid/expired token).
*   **403 Forbidden:** Authenticated user does not have permission for the action (less common if this service primarily handles authentication, but could apply to user management endpoints).
*   **404 Not Found:** Resource not found (e.g., user ID in a URL parameter).
*   **500 Internal Server Error:** Unexpected server-side error.

Error responses should be in a structured format (e.g., JSON) and avoid leaking sensitive internal details.

---

## 7. Integration with Other Core Components

*   **`api-gateway/`:** The API Gateway is a primary consumer. It would delegate authentication of incoming requests to the Identity Service by:
    *   Forwarding credentials for login/registration.
    *   Requesting validation of JWTs found in request headers.
*   **Other Backend Services:** Any service requiring user authentication or user-specific data would interact with the Identity Service or consume information from JWTs it issues.
*   **Databases (Conceptual):** A persistent database (e.g., PostgreSQL, MySQL) is essential for storing user credentials (hashed passwords), profile information, roles, and potentially refresh tokens.
*   **`Logging Service` (`services/logging_service.py`):** For auditing security-sensitive events like logins, registrations, password changes, and token issuance.

---

## 8. Configuration (Conceptual)

Key environment variables or configuration settings would likely include:
*   **`DATABASE_URL`:** Connection string for the user database.
*   **`JWT_SECRET_KEY`:** Secret key used to sign and verify JWTs. This must be kept highly confidential.
*   **`JWT_ALGORITHM`:** Algorithm used for JWTs (e.g., `HS256`, `RS256`).
*   **`ACCESS_TOKEN_EXPIRE_MINUTES`:** Lifetime of access tokens.
*   **`REFRESH_TOKEN_EXPIRE_DAYS`:** Lifetime of refresh tokens.
*   **`PASSWORD_HASHING_ROUNDS`:** (Or equivalent cost factor) For algorithms like bcrypt.
*   **`LOG_LEVEL`:** Verbosity of service logs.

---

## 9. Future Enhancements

*   **Multi-Factor Authentication (MFA):** Support for OTPs (TOTP/HOTP), SMS, or other second factors.
*   **OAuth 2.0 / OpenID Connect (OIDC) Provider:** Allow CyberSage to act as an OAuth/OIDC provider for first-party or trusted third-party applications.
*   **Integration with External Identity Providers (IdP):** Support for login via SAML, OAuth2/OIDC from external IdPs (e.g., Google, Okta, Azure AD).
*   **User Account Locking & Throttling:** Policies to lock accounts after multiple failed login attempts.
*   **Passwordless Authentication:** Options like magic links or WebAuthn.
*   **Granular Role and Permission Management UI:** If not already present, an interface for managing roles and permissions.
*   **Security Event Streaming:** Publish security events (e.g., login failures, password resets) to a message queue for real-time monitoring.
```
