# Contributing to CyberSage

First off, thank you for considering contributing to CyberSage! We welcome contributions from everyone. By participating in this project, you agree to abide by our [Code of Conduct](./CODE_OF_CONDUCT.md).

This document outlines the process for contributing to the project, including reporting issues, submitting pull requests, coding standards, and testing procedures.

## Table of Contents

1.  [Issue Reporting & Triaging](#1-issue-reporting--triaging)
    -   [Bug Reports](#bug-reports)
    -   [Feature Requests](#feature-requests)
    -   [Security Vulnerabilities](#security-vulnerabilities)
2.  [Development Workflow](#2-development-workflow)
    -   [Setting Up Your Environment](#setting-up-your-environment)
    -   [Branching Model](#branching-model)
    -   [Making Changes](#making-changes)
3.  [Coding Standards](#3-coding-standards)
    -   [Python Style](#python-style)
    -   [TypeScript/JavaScript Style](#typescriptjavascript-style)
    -   [Commit Messages](#commit-messages)
4.  [Pull Request (PR) Process](#4-pull-request-pr-process)
    -   [Before Submitting](#before-submitting)
    -   [Submitting the PR](#submitting-the-pr)
    -   [Review Process](#review-process)
5.  [Testing & Code Coverage](#5-testing--code-coverage)
    -   [Running Tests](#running-tests)
    -   [Adding New Tests](#adding-new-tests)
    -   [Coverage Requirements](#coverage-requirements)
6.  [Documentation](#6-documentation)

---

## 1. Issue Reporting & Triaging

Before creating a new issue, please search existing [GitHub Issues](https://github.com/rick1330/cybersage/issues) to see if your problem or suggestion has already been reported.

### Bug Reports

If you find a bug, please open an issue using the **Bug Report** template available when creating a new issue ([`.github/ISSUE_TEMPLATE/bug_report.yml`](./.github/ISSUE_TEMPLATE/bug_report.yml)). Provide as much detail as possible, including:

*   A clear and descriptive title.
*   Steps to reproduce the bug reliably.
*   What you expected to happen.
*   What actually happened (including error messages, logs, screenshots).
*   Your environment details (OS, Python version, Docker version, relevant dependencies).

### Feature Requests

If you have an idea for a new feature or enhancement, please open an issue using the **Feature Request** template available when creating a new issue ([`.github/ISSUE_TEMPLATE/feature_request.yml`](./.github/ISSUE_TEMPLATE/feature_request.yml)). Describe:

*   The problem you are trying to solve.
*   The proposed solution or feature.
*   Any alternative solutions or features you've considered.
*   The potential benefits to users.

### Security Vulnerabilities

**Do not report security vulnerabilities through public GitHub issues.** Please refer to our [SECURITY.md](./SECURITY.md#reporting-a-vulnerability) file for instructions on how to report security issues privately.

---

## 2. Development Workflow

### Setting Up Your Environment

1.  **Fork the repository:** Create your own fork of the `rick1330/cybersage` repository on GitHub.
2.  **Clone your fork:**
    ```bash
    git clone git@github.com:<YOUR_USERNAME>/cybersage.git
    cd cybersage
    ```
3.  **Add the upstream remote:**
    ```bash
    git remote add upstream https://github.com/rick1330/cybersage.git
    git fetch upstream
    ```
4.  **Follow the Installation steps** in the main [README.md](./README.md#installation) to set up dependencies, virtual environments, and Docker services.
5.  **Install development dependencies:** (If separate from `requirements.txt`, e.g., in `requirements-dev.txt`)
    ```bash
    # Ensure your virtual environment is activated
    pip install -r requirements.txt # Install core deps first
    # If a dev requirements file exists:
    # pip install -r requirements-dev.txt
    # Otherwise, install common dev tools:
    pip install pytest pytest-cov pytest-asyncio black flake8 isort mypy pre-commit
    ```
6.  **Set up pre-commit hooks:** (Ensures code quality checks before committing)
    ```bash
    # Ensure your virtual environment is activated
    pre-commit install
    # Optional: Install commit message hook if configured (e.g., with commitlint)
    # pre-commit install --hook-type commit-msg
    ```

### Branching Model

We follow a branching model based on Gitflow principles, but simplified:

*   `main`: Represents the latest stable release. Direct commits are forbidden. Merges happen only from release branches or hotfix branches.
*   `develop`: Represents the latest development state. This is the primary branch for integrating new features. **PRs are typically merged into `develop`.**
*   **Feature Branches:** Create branches off `develop` for new features or non-trivial bug fixes.
    *   Naming: `feature/<feature-name>` or `feat/<feature-name>` (e.g., `feat/add-metasploit-tool`)
    *   Naming: `fix/<issue-number>-<short-description>` (e.g., `fix/123-nmap-timeout`)
*   **Release Branches:** Branched off `develop` when preparing for a release (e.g., `release/v1.1.0`). Only bug fixes and documentation updates should go here. Once ready, merged into `main` and `develop`, and tagged on `main`.
*   **Hotfix Branches:** Branched off `main` to fix critical bugs in production (e.g., `hotfix/v1.0.1`). Merged back into `main` and `develop`.

**Workflow:**

1.  Sync your local `develop` branch with upstream:
    ```bash
    git checkout develop
    git pull upstream develop
    ```
2.  Create a feature/fix branch off `develop`:
    ```bash
    git checkout -b feat/my-new-feature develop
    ```
3.  Make your changes.
4.  Commit your changes (following [Commit Messages](#commit-messages) guidelines). Pre-commit hooks will run.
5.  Push your branch to your fork:
    ```bash
    git push origin feat/my-new-feature
    ```
6.  Create a Pull Request (PR) from your fork's branch to the `upstream/develop` branch on GitHub.

### Making Changes

*   Write clean, understandable code.
*   Add comments only where necessary to explain complex logic.
*   Ensure your changes adhere to the [Coding Standards](#4-coding-standards).
*   Write or update tests for your changes ([Testing & Code Coverage](#5-testing--code-coverage)).
*   Update documentation if your changes affect user-facing features, APIs, or configuration ([Documentation](#6-documentation)).

---

## 3. Coding Standards

Consistency helps maintain code quality and readability. We use automated tools to enforce standards.

### Python Style

*   **Style Guide:** Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/).
*   **Formatter:** Use [Black](https://github.com/psf/black). Enforced by pre-commit. Configuration is typically in `pyproject.toml`.
*   **Linter:** Use [Flake8](https://flake8.pycqa.org/en/latest/) with common plugins (configured in `.flake8`). Enforced by pre-commit.
*   **Import Sorting:** Use [isort](https://pycqa.github.io/isort/) (config in `pyproject.toml` or `.isort.cfg`). Enforced by pre-commit.
*   **Type Hinting:** Use Python 3.9+ type hints extensively. Check with [MyPy](http://mypy-lang.org/) (config in `mypy.ini` or `pyproject.toml`).
*   **Docstrings:** Use Google or NumPy style docstrings for all public modules, classes, and functions. Example:
    ```python
    def example_function(param1: str, param2: int) -> bool:
        """
        Brief description of the function's purpose.

        More detailed explanation if needed, covering edge cases or rationale.

        Args:
            param1: Description of the first parameter and its role.
            param2: Description of the second parameter and its role.

        Returns:
            Description of the boolean value returned.

        Raises:
            ValueError: If param1 is invalid or empty.
            TypeError: If parameter types are incorrect.
        """
        if not isinstance(param1, str) or not isinstance(param2, int):
            raise TypeError("Invalid parameter types provided.")
        if not param1:
            raise ValueError("param1 cannot be empty")
        # ... function logic ...
        result = True # Placeholder
        return result
    ```
*   **Logging:** Use the centralized `LoggingService` (`services/logging_service.py`) instead of `print()` statements for application logging.

### TypeScript/JavaScript Style

*   **Formatter:** Use [Prettier](https://prettier.io/) (config likely in `.prettierrc` or `package.json`). Enforced by pre-commit/lint-staged.
*   **Linter:** Use [ESLint](https://eslint.org/) (config likely in `.eslintrc.js/.json`). Enforced by pre-commit/lint-staged.
*   Follow standard conventions for the framework being used (e.g., React, NestJS).
*   Prefer TypeScript over JavaScript for type safety.

### Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification. This helps automate changelog generation and provides a clear history.

<type>[optional scope]: <description>

[optional body]

[optional footer(s)]


*   **Types:** `feat` (new feature), `fix` (bug fix), `build` (build system/deps), `chore` (maintenance), `ci` (CI/CD changes), `docs` (documentation), `style` (formatting), `refactor` (code structure changes), `perf` (performance improvements), `test` (adding/fixing tests).
*   **Scope (Optional):** Indicates the part of the codebase affected (e.g., `feat(api): ...`, `fix(nmap_tool): ...`).
*   **Description:** Concise summary in imperative mood (e.g., "Add user authentication" not "Added user authentication"). Start with a lowercase letter.
*   **Body (Optional):** Provides more context, motivation, or details about the change.
*   **Footer (Optional):** Used for `BREAKING CHANGE:` notes or referencing issue numbers (e.g., `Fixes #123`, `Refs #456`).

**Example:**

fix(api): correct pagination logic for list agents endpoint

The previous implementation did not handle the offset parameter correctly,
leading to duplicate results on subsequent pages. This commit adjusts
the database query to use the offset properly.

Fixes #135

*(A commit message lint hook might be configured via `commitlint` and Husky in `.husky/commit-msg`)*

---

## 4. Pull Request (PR) Process

### Before Submitting

*   **Sync with Upstream:** Ensure your branch is up-to-date with the latest `upstream/develop`:
    ```bash
    # Ensure you are on your feature branch
    git fetch upstream
    git rebase upstream/develop # Or git merge upstream/develop
    ```
    Resolve any merge conflicts locally.
*   **Run Linters & Formatters:** Make sure `pre-commit run --all-files` passes without errors.
*   **Run Tests:** Ensure all tests pass locally: `pytest tests/` (or the relevant test command for the component you modified).
*   **Check Coverage:** Ensure your changes meet the coverage requirements (run `pytest --cov=...`).
*   **Update Documentation:** If your changes affect user-facing features, APIs, configuration, or architecture.
*   **Add Changelog Entry:** If your change is user-facing or significant, add an entry to `CHANGELOG.md` under the `[Unreleased]` section, following the "Keep a Changelog" format.

### Submitting the PR

1.  Push your final changes to your fork:
    ```bash
    git push origin your-feature-branch
    ```
2.  Go to the `rick1330/cybersage` repository on GitHub.
3.  GitHub should prompt you to create a PR from your recently pushed branch. If not, navigate to the "Pull requests" tab and click "New pull request".
4.  Set the **base repository** to `rick1330/cybersage` and **base branch** to `develop`.
5.  Set the **head repository** to your fork and **compare branch** to your feature/fix branch.
6.  Fill out the PR template ([`.github/PULL_REQUEST_TEMPLATE.md`](./.github/PULL_REQUEST_TEMPLATE.md)):
    *   Provide a clear title summarizing the change (often derived from your primary commit message).
    *   Link to the relevant issue(s) using keywords like `Closes #123` or `Fixes #123`.
    *   Describe the changes made and the motivation behind them.
    *   Include screenshots or steps for manual testing if applicable.
7.  Check the box to "Allow edits by maintainers" - this can speed up minor fixes during review.
8.  Submit the Pull Request.

### Review Process

*   **Automated Checks:** GitHub Actions (CI) will run linters, tests, type checks, and other validations automatically. Ensure these pass (look for the green checkmark). Address any failures by pushing fixes to your branch.
*   **Code Review:** One or more maintainers or designated reviewers will examine your code for correctness, style, performance, security, and adherence to project goals.
*   **Address Feedback:** Respond to review comments constructively. Make necessary changes by pushing new commits to your branch (the PR will update automatically). Avoid force-pushing unless specifically requested by a maintainer to clean up history.
*   **Approval & Merge:** Once the PR is approved by the required reviewers and all checks pass, a maintainer will merge your PR into the `develop` branch.
*   **Thank You!** Your contribution is now part of CyberSage!

---

## 5. Testing & Code Coverage

We aim for comprehensive test coverage to ensure stability and prevent regressions.

### Running Tests

*   **Python Backend (Unit & Integration):**
    ```bash
    # Ensure necessary services (like Redis, DB if needed for integration tests) are running
    # Often managed via docker-compose -f docker-compose.test.yml up -d or similar
    pytest tests/
    ```
*   **JavaScript/TypeScript Frontend/Gateway:**
    ```bash
    # Navigate to the specific service directory (e.g., ui-web/ or api-gateway/)
    npm test
    # or
    yarn test
    ```
*   **End-to-End Tests:** (May require a fully running stack)
    ```bash
    # Instructions likely in tests/e2e/README.md
    # Example using Cypress: cd ui-web && npx cypress open
    ```

### Adding New Tests

*   **Unit Tests:** Test individual functions or classes in isolation. Place them in the `tests/` directory, mirroring the source structure (e.g., `tests/core/test_agent_manager.py`). Use mocking (`unittest.mock` or `pytest-mock`) extensively to isolate dependencies.
*   **Integration Tests:** Test the interaction between multiple components or services (e.g., API endpoint calling a service that uses the database). Place them in `tests/integration/`. These often require running dependent services.
*   **Fixtures:** Use pytest fixtures (defined in `tests/conftest.py` or locally in test files) to set up reusable test contexts, data, or mocked objects.
*   Follow the **Arrange-Act-Assert** pattern for structuring tests.
*   Test edge cases, invalid inputs, boundary conditions, and error handling paths.

### Coverage Requirements

*   We strive for high code coverage (aiming for >80-90% where practical). Pull requests should ideally maintain or increase the overall coverage percentage.
*   Run coverage checks locally:
    ```bash
    # Adjust 'src' to your main source directory/package name(s)
    pytest --cov=core --cov=services --cov=tools --cov-report=term-missing tests/
    ```
*   CI checks will likely report coverage status and potentially fail the build if coverage drops below a defined threshold. Ensure all new code paths introduced by your changes are covered by tests.

---

## 6. Documentation

Good documentation is essential for usability and maintainability.

*   **Code Comments:** Use docstrings (Google or NumPy style for Python) for all public modules, classes, and functions. Add inline comments only for complex or non-obvious logic sections.
*   **READMEs:** Update the main `README.md` or relevant subdirectory `README.md` files if your changes affect installation, configuration, usage, or architecture.
*   **`/docs` Directory:** For significant features or architectural changes, consider adding or updating detailed documentation in the `/docs` directory (e.g., architecture diagrams, design decisions/ADRs, usage guides).
*   **API Documentation:** Ensure OpenAPI schemas (`interfaces/api/schemas.py`) and endpoint definitions (`interfaces/api/routes.py`) are updated for API changes. Documentation might be auto-generated from this.

---

Thank you again for your interest in contributing to CyberSage!
