# Design

## Architecture

The agent is implemented as a small LangGraph workflow with an LLM node and a tool node.

```text
User
  ↓
LLM
  ↓
Tool call? ── No ──→ Final response
  │
 Yes
  ↓
ToolNode
  ↓
LLM
  ↓
Final response / another tool call
```

## Components

* **`app.py`** — CLI and conversation loop.
* **`agent.py`** — LLM invocation.
* **`graph.py`** — LangGraph workflow.
* **`state.py`** — Conversation message state.
* **`tools.py`** — arXiv search and PDF download tools.

## Tool Design

### `search_arxiv`

This tool addresses the user's need to discover relevant research papers without manually searching arXiv. It provides structured paper information, including the title, update date, abstract, and PDF URL, giving the agent the information needed for subsequent research steps.

### `download_pdf`

This tool complements `search_arxiv` by allowing the agent to retrieve the actual paper once a relevant result has been identified. Separating search and download gives the agent control over whether downloading is necessary instead of downloading papers for every search request.

## Tool Selection

The LLM decides which tool is relevant to the user's request.

* General questions → no tool
* Paper search → `search_arxiv`
* Search and download → `search_arxiv` followed by `download_pdf`

## Context

Conversation history is maintained during the current interactive session, allowing short follow-up questions to depend on previous turns.

## Error Handling

Tools raise explicit exceptions for failures such as API errors, invalid URLs, HTTP errors, timeouts, and file-system errors.

`ToolNode(handle_tool_errors=True)` passes tool failures back to the agent, and the system prompt instructs the agent to report failures clearly instead of fabricating results.

## Observability

Optional LangSmith tracing provides visibility into LLM calls, tool-call decisions, tool inputs/outputs, and failures.