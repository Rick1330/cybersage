# Core: Prompt Templates

Prompt templates are a fundamental part of guiding the behavior of Large Language Models (LLMs) within CyberSage. The `prompt_templates.py` module (or equivalent structure) defines standardized, reusable prompt structures tailored for various cybersecurity tasks.

Using templates ensures consistency, allows for easier updates, and helps inject necessary context (like tool descriptions, previous conversation history, or specific instructions) into the prompts sent to the LLM.

## Table of Contents

1.  [Purpose](#1-purpose)
2.  [Core Concepts](#2-core-concepts)
    -   [Placeholders/Variables](#placeholdersvariables)
    -   [Prompt Formatting](#prompt-formatting)
    -   [Framework Integration (LangChain)](#framework-integration-langchain)
3.  [Catalog of Common Templates](#3-catalog-of-common-templates)
    -   [Agent Scratchpad/Thought Process](#agent-scratchpadthought-process)
    -   [Tool Usage Instruction](#tool-usage-instruction)
    -   [Task Decomposition](#task-decomposition)
    -   [Result Summarization/Analysis](#result-summarizationanalysis)
    -   [Security Report Generation](#security-report-generation)
    -   *(We'll add more specific templates as they are defined)*
4.  [Template Variables](#4-template-variables)
5.  [Usage Examples](#5-usage-examples)
    -   [Formatting a Prompt](#formatting-a-prompt)
6.  [Best Practices for Creating Templates](#6-best-practices-for-creating-templates)
7.  [Integration with Other Components](#7-integration-with-other-components)

---

## 1. Purpose

The primary goals of using prompt templates in CyberSage are:

*   **Consistency:** Ensure that similar tasks are approached by the LLM with the same underlying instructions and structure.
*   **Control:** Guide the LLM's reasoning process, output format, and tool usage effectively.
*   **Context Injection:** Provide a structured way to insert dynamic information (user input, tool descriptions, memory, intermediate results) into the prompt.
*   **Maintainability:** Centralize prompt definitions, making them easier to update, test, and refine without changing the core agent logic significantly.
*   **Optimization:** Allow for experimentation and optimization of prompts to achieve better performance and accuracy from the LLM for specific security domains.

---

## 2. Core Concepts

### Placeholders/Variables

Templates contain placeholders (variables) that are filled in dynamically before the prompt is sent to the LLM. Common variables include:

*   `{input}`: The user's query or the current task description.
*   `{agent_scratchpad}` or `{intermediate_steps}`: The history of the agent's thoughts, actions taken, and observations received (crucial for ReAct-style agents).
*   `{chat_history}`: Previous turns in the conversation.
*   `{tool_names}`: A list of available tool names.
*   `{tool_descriptions}`: Detailed descriptions of available tools and their usage.
*   `{format_instructions}`: Specific instructions on how the LLM should format its final output.

### Prompt Formatting

Templates combine static instructional text with these dynamic variables. They often include sections like:

*   **Role Definition:** Instructing the LLM to act as a specific persona (e.g., "You are a cybersecurity analyst assistant...").
*   **Tool Instructions:** Explaining how the LLM should decide to use tools and the format for invoking them.
*   **Task Instructions:** Detailing the specific goal or question to be addressed.
*   **Output Formatting:** Specifying the desired structure of the final answer (e.g., JSON, Markdown table, step-by-step plan).

### Framework Integration (LangChain)

CyberSage leverages frameworks like LangChain, which have built-in support for prompt templates (`PromptTemplate`, `ChatPromptTemplate`, `FewShotPromptTemplate`, etc.). These classes handle the formatting and variable injection automatically. The templates defined in `prompt_templates.py` are often instances of these LangChain classes or provide the necessary string formats for them.

---

## 3. Catalog of Common Templates

Below are examples of the *types* of prompt templates used within CyberSage. The actual implementations are in `core/prompt_templates.py` or related files.

*(Note: The exact wording and variables will vary based on the specific agent type and LLM used.)*

### Agent Scratchpad/Thought Process

*   **Purpose:** Used by ReAct (Reasoning and Acting) agents to structure their internal monologue.
*   **Key Variables:** `{input}`, `{tool_names}`, `{tool_descriptions}`, `{agent_scratchpad}`.
*   **Example Snippet:**
    ```text
    You are a helpful cybersecurity assistant. Answer the following questions as best you can. You have access to the following tools:
    {tool_descriptions}

    Use the following format:

    Question: the input question you must answer
    Thought: you should always think about what to do
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question

    Begin!

    Question: {input}
    Thought: {agent_scratchpad}
    ```

### Tool Usage Instruction

*   **Purpose:** Explicitly tells the agent how and when to use a specific tool or format tool requests.
*   **Key Variables:** `{tool_name}`, `{tool_description}`, `{input}`.
*   **Example Snippet (Part of a larger prompt):**
    ```text
    To use the Nmap scanner tool, format your action like this:
    Action: nmap_tool
    Action Input: target=<target_ip_or_hostname>, ports=<port_list>, scan_type=<basic|service|full>
    Only specify the parameters needed for the current task based on the user query: {input}
    ```

### Task Decomposition

*   **Purpose:** Instructs the LLM to break down a complex user request into smaller, manageable sub-tasks.
*   **Key Variables:** `{input}`.
*   **Example Snippet:**
    ```text
    Given the complex security investigation request below, break it down into a sequence of smaller, actionable steps. For each step, identify the primary goal and potential tools needed.

    Request: {input}

    Output the plan as a numbered list.
    ```

### Result Summarization/Analysis

*   **Purpose:** Takes raw output from a tool (e.g., Nmap XML, log lines) and asks the LLM to summarize key findings or perform analysis.
*   **Key Variables:** `{tool_output}`, `{original_task}`.
*   **Example Snippet:**
    ```text
    You are provided with the raw output from a security tool run for the task: "{original_task}".
    Analyze the following tool output and provide a concise summary of the key findings relevant to the task. Focus on actionable intelligence like open ports, identified services, potential vulnerabilities, or indicators of compromise.

    Tool Output:
    ```
    {tool_output}
    ```

    Summary:
    ```

### Security Report Generation

*   **Purpose:** Guides the LLM to compile findings from multiple steps or tools into a structured report format.
*   **Key Variables:** `{findings_summary}`, `{target_info}`, `{report_format_instructions}`.
*   **Example Snippet:**
    ```text
    Generate a security assessment section based on the following summary of findings for target {target_info}.
    Follow the specified report format.

    Findings Summary:
    {findings_summary}

    Report Format Instructions:
    {report_format_instructions}

    Report Section:
    ```

---

## 4. Template Variables

The specific variables available depend on the context in which the template is used (e.g., which agent, which chain). Common sources for variable values include:

*   User input.
*   Agent's internal state (`agent_scratchpad`).
*   Conversation history (`chat_history`).
*   Tool definitions (`tool_names`, `tool_descriptions`).
*   Output parsing instructions (`format_instructions`).
*   Data retrieved from memory or vector stores.

---

## 5. Usage Examples

### Formatting a Prompt

This shows how a `PromptTemplate` object (like one defined in `prompt_templates.py`) might be used.

```python
from langchain.prompts import PromptTemplate

# Assume a template string is defined (simplified example)
template_string = """
Analyze the following Nmap scan results for {target}:
Scan Data: {scan_data}
Identify critical open ports and potential vulnerabilities.
"""

# Create a PromptTemplate instance
scan_analysis_prompt = PromptTemplate(
    input_variables=["target", "scan_data"],
    template=template_string
)

# Format the prompt with actual data
formatted_prompt = scan_analysis_prompt.format(
    target="192.168.1.1",
    scan_data="<Nmap output string or relevant data>"
)

print(formatted_prompt)
# Output would be the template string with placeholders filled
```

---

## 6. Best Practices for Creating Templates

*   **Be Specific:** Clearly define the task, expected output format, and constraints. Avoid ambiguity.
*   **Provide Context:** Include relevant background information, tool descriptions, or few-shot examples to guide the LLM.
*   **Use Role Prompting:** Instruct the LLM to adopt a specific persona (e.g., "You are a helpful cybersecurity analyst specializing in network traffic analysis...").
*   **Iterate and Test:** Prompt engineering is an iterative process. Test templates with various inputs and refine them based on the LLM's performance and accuracy.
*   **Control Output Format:** Use techniques like explicitly requesting JSON, Markdown tables, numbered lists, or providing output schemas (e.g., via LangChain's output parsers) to guide the structure.
*   **Consider Token Limits:** Be mindful of the overall prompt length, especially when injecting large amounts of dynamic context like chat history or verbose tool output. Long prompts can be costly and may hit model limits.
*   **Separate Concerns:** Use distinct templates for different logical steps or tasks (e.g., planning vs. summarization vs. tool invocation formatting). This improves modularity and maintainability.

---

## 7. Integration with Other Components

*   **`AgentManager` (`/core/agent_manager.py`):** Provides the appropriate prompt templates (often based on `agent_type`) to the agents it initializes.
*   **`ChainBuilder` (`/core/chain_builder.py`):** Uses prompt templates as fundamental building blocks when constructing LangChain chains (e.g., within an `LLMChain`).
*   **LLM Services (`/services/openai_service.py`):** The final, formatted prompt strings generated from these templates are sent to the underlying LLM (e.g., OpenAI) via these service interfaces.
*   **Tool Definitions (`/tools/`):** Information such as tool names (`{tool_names}`) and descriptions (`{tool_descriptions}`) are dynamically injected as variables into prompt templates to inform the agent about its available capabilities.
```
