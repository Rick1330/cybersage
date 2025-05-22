# Core: Chain Builder

The `ChainBuilder` (`core/chain_builder.py`) is a utility component within the CyberSage core engine responsible for constructing and configuring complex sequences of operations, often referred to as "chains," using frameworks like LangChain. Chains allow for more sophisticated interactions than single LLM calls by linking together LLMs, tools, prompt templates, memory, and output parsers.

## Table of Contents

1.  [Purpose](#1-purpose)
2.  [Core Concepts (LangChain)](#2-core-concepts-langchain)
    -   [Chains](#chains)
    -   [LLMs](#llms)
    -   [Prompt Templates](#prompt-templates)
    -   [Tools](#tools)
    -   [Memory](#memory)
    -   [Output Parsers](#output-parsers)
3.  [Role of the Chain Builder](#3-role-of-the-chain-builder)
4.  [Common Chain Types Used](#4-common-chain-types-used)
    -   [`LLMChain`](#llmchain)
    -   [`SequentialChain`](#sequentialchain)
    -   [`RouterChain`](#routerchain)
    -   [Agent Execution Chains](#agent-execution-chains)
5.  [Usage Examples](#5-usage-examples)
    -   [Building a Simple LLMChain](#building-a-simple-llmchain)
    -   [Building a Sequential Chain](#building-a-sequential-chain)
6.  [Configuration and Extension](#6-configuration-and-extension)
7.  [Error Handling](#7-error-handling)
8.  [Integration with Other Components](#8-integration-with-other-components)

---

## 1. Purpose

While simple tasks might involve a direct call to an LLM or an agent, more complex workflows often require multiple steps. The `ChainBuilder` facilitates the creation of these multi-step processes by:

*   **Abstraction:** Hiding the lower-level details of LangChain (or similar framework) chain construction.
*   **Reusability:** Providing methods to build common types of chains needed within CyberSage (e.g., a chain to analyze tool output, a chain to plan steps).
*   **Configuration:** Ensuring chains are correctly configured with the appropriate LLM instances, prompts, tools, memory, and output parsers sourced from other CyberSage components.
*   **Consistency:** Promoting a standardized way to define and build interaction flows involving LLMs and tools.

It acts as a factory or helper class for creating pre-configured chain objects that can then be used by agents or other services.

---

## 2. Core Concepts (LangChain)

The `ChainBuilder` primarily works with concepts from the LangChain library:

### Chains

The core abstraction in LangChain. A chain represents a sequence of calls, which can be to LLMs, tools, or other chains. They manage the flow of data between steps.

### LLMs

The language models themselves (e.g., `ChatOpenAI` instance provided by `OpenAIService`). Chains use these models for generation, reasoning, or analysis.

### Prompt Templates

Structured templates (`PromptTemplate`, `ChatPromptTemplate`) used to format the input to LLMs within a chain. Sourced from `/core/prompt_templates.py`.

### Tools

Functions or capabilities that a chain (especially an agent chain) can invoke. Sourced from `/tools/`.

### Memory

Mechanisms for persisting state between calls within a chain or across multiple chain executions. Provided via `MemoryService`.

### Output Parsers

Components that parse the string output from an LLM into a more structured format (e.g., JSON, a list, a custom object).

---

## 3. Role of the Chain Builder

The `ChainBuilder` class itself might not have a complex public API like the `AgentManager`. Its primary role is internal to the `core` module or potentially used during the initialization phase. It might offer methods like:

*   `build_llm_chain(prompt: PromptTemplate, llm: BaseLanguageModel, **kwargs) -> LLMChain`: Creates a basic chain consisting of a prompt and an LLM.
*   `build_summarization_chain(llm: BaseLanguageModel, **kwargs) -> BaseCombineDocumentsChain`: Creates a chain specifically designed for summarizing text or tool output.
*   `build_sequential_chain(chains: List[Chain], input_variables: List[str], output_variables: List[str], **kwargs) -> SequentialChain`: Links multiple chains together sequentially.
*   `get_agent_executor(agent: ...) -> AgentExecutor`: While agent initialization might be in `AgentManager`, the `ChainBuilder` could potentially be involved in configuring the `AgentExecutor` chain that actually runs the agent loop.

It acts as a helper to assemble these pre-configured chain objects using the correctly initialized components (LLMs, prompts, etc.) from the rest of the CyberSage platform.

---

## 4. Common Chain Types Used

CyberSage likely utilizes several types of LangChain chains, constructed via the `ChainBuilder`:

### `LLMChain`

*   **Description:** The most fundamental chain type. Takes user input, formats it with a `PromptTemplate`, and passes it to an `LLM`.
*   **Use Case:** Simple Q&A, text generation based on a template, initial processing steps.

### `SequentialChain`

*   **Description:** Runs multiple chains in a defined sequence, where the output of one chain becomes the input to the next.
*   **Use Case:** Multi-step analysis (e.g., run Nmap -> summarize Nmap output -> check findings against CVE database).

### `RouterChain`

*   **Description:** Uses an LLM to determine which specific chain or prompt to use next based on the input.
*   **Use Case:** Directing a user query to the most appropriate specialized agent or workflow (e.g., routing to a "vulnerability analysis" chain vs. a "log summarization" chain).

### Agent Execution Chains

*   **Description:** Chains like `AgentExecutor` manage the "Thought -> Action -> Observation" loop for autonomous agents, deciding when to call the LLM for reasoning and when to execute a tool.
*   **Use Case:** Powering the core logic of agents created by the `AgentManager`.

---

## 5. Usage Examples

*(Note: These examples show conceptual usage. The actual implementation might involve calling methods on a `chain_builder` instance.)*

### Building a Simple LLMChain

```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
# Assume llm is an initialized BaseLanguageModel (e.g., ChatOpenAI)
# Assume prompt_template_string is defined in core.prompt_templates

# Define the prompt template
prompt = PromptTemplate(
    input_variables=["query"],
    template="Answer the following cybersecurity question: {query}"
)

# Build the chain (conceptually what ChainBuilder might do)
llm_chain = LLMChain(llm=llm, prompt=prompt)

# Run the chain
response = llm_chain.run("What is the purpose of the Shodan search engine?")
print(response)
```
### Building a Sequential Chain
```python
from langchain.chains import LLMChain, SimpleSequentialChain
from langchain.prompts import PromptTemplate
# Assume llm is initialized

# Chain 1: Generate a security topic
prompt1 = PromptTemplate(input_variables=["subject"], template="Generate a specific security topic related to {subject}.")
chain1 = LLMChain(llm=llm, prompt=prompt1)

# Chain 2: Write a brief explanation of the topic
prompt2 = PromptTemplate(input_variables=["topic"], template="Write a brief, one-paragraph explanation of the security topic: {topic}")
chain2 = LLMChain(llm=llm, prompt=prompt2)

# Build the sequential chain (conceptually what ChainBuilder might do)
sequential_chain = SimpleSequentialChain(chains=[chain1, chain2], verbose=True)

# Run the chain
response = sequential_chain.run("web application firewalls")
print(response)
```
---

## 6. Configuration and Extension

*   The `ChainBuilder` depends on correctly configured and injected services (like `OpenAIService`, `MemoryService`) and components (like specific `PromptTemplate` instances, `BaseTool` instances).
*   New methods can be added to the `ChainBuilder` class to encapsulate the logic for building new, reusable types of chains as CyberSage's workflow requirements evolve.
*   Configuration parameters specific to chains (e.g., `verbose=True`, specific memory configurations) can be accepted by the builder methods and passed during chain instantiation.
---

## 7. Error Handling

*   Errors encountered during the *execution* of a chain typically originate from the components within that chain, such as:
    *   LLM API errors (rate limits, connection issues, invalid requests) handled by the LLM service.
    *   Errors raised by tool wrappers during execution.
    *   Parsing errors from `OutputParser`s if the LLM output doesn't match the expected format.
*   The LangChain library itself might raise exceptions for configuration issues (e.g., `ValidationError` for missing input variables).
*   The `ChainBuilder` methods themselves could raise errors if required dependencies (like a specific prompt template or LLM instance) cannot be resolved or are misconfigured during the build process.
*   It is the responsibility of the code *calling* and *running* the chains (e.g., within an agent or workflow step) to implement robust `try-except` blocks to handle potential runtime errors gracefully.
---

## 8. Integration with Other Components

*   **`AgentManager` (`/core/agent_manager.py`):** While the `AgentManager` might handle the primary initialization of agents (e.g., using `initialize_agent`), it could potentially utilize the `ChainBuilder` to construct or configure the underlying `AgentExecutor` chain that powers the agent's run loop.
*   **`Prompt Templates` (`/core/prompt_templates.py`):** Prompt templates are essential inputs provided to the `ChainBuilder` for constructing chains that involve LLM interactions, particularly `LLMChain`.
*   **LLM Services (`/services/openai_service.py`):** The `ChainBuilder` requires access to configured LLM instances (e.g., `ChatOpenAI`) provided by these services to pass into the chains being built.
*   **Tool Wrappers (`/tools/`):** For chains that need to execute actions (like agent chains), the relevant `BaseTool` instances are passed to the `ChainBuilder` or directly into the chain configuration.
*   **`MemoryService` (`/services/memory_service.py`):** The `ChainBuilder` can configure chains to use specific memory objects retrieved from or managed by the `MemoryService`, enabling stateful chain executions.
*   **Workflow Engine (`/core-services/workflow-engine-svc/`):** The Workflow Engine might leverage the `ChainBuilder` to dynamically construct specific chain-based steps as part of executing a larger, predefined workflow definition.
  
```
