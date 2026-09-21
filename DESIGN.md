# Design

## Architecture

The agent is implemented as a small LangGraph workflow using Google Gemini for reasoning and tool selection.

```text
User
  │
  ▼
LLM Node
  │
  ├── No tool needed ──────► Final response
  │
  └── Tool call
        │
        ▼
     Tool Node
        │
        ▼
      LLM Node
        │
        ├── Another tool needed ──► Tool Node
        │
        └── No more tools ────────► Final response
```

The application keeps the conversation message history during the interactive session, allowing the agent to resolve short follow-up questions that depend on previous turns.

## Tool Design

### `search_arxiv`

This tool addresses the user's need to discover relevant research papers without manually searching arXiv. It returns structured information such as the title, update date, abstract, and PDF URL, which can also be used by the agent for subsequent actions.

### `download_pdf`

This tool complements `search_arxiv` by allowing the agent to retrieve the actual paper once a relevant result has been identified. Keeping search and download as separate tools allows the agent to download a paper only when the user requests it.

## Key Trade-offs

### Simple graph vs. more complex agent architecture

A small two-node LangGraph workflow was chosen instead of introducing multiple specialized agents. This keeps the execution flow easy to understand and debug while being sufficient for the current task.

### LLM-based tool selection vs. rule-based routing

Tool selection is delegated to the LLM rather than implementing custom keyword-based routing. This allows the agent to handle natural language requests and multi-step requests such as finding a paper and then downloading it. The trade-off is that tool selection is probabilistic and therefore requires clear tool descriptions, prompting, and testing.

### Session context vs. persistent memory

Conversation history is maintained in application state for the current interactive session. This is sufficient for the required multi-turn context while avoiding the complexity of a persistent memory backend.

### Optional observability

LangSmith tracing is optional rather than a core dependency. This provides useful visibility into tool calls and execution flow without making the application dependent on an external observability service.

## Error Handling

Tool failures are explicitly propagated and handled by the LangGraph `ToolNode` using:

```python
ToolNode(
    chat_tools,
    handle_tool_errors=True,
)
```

The system prompt instructs the agent to report tool failures clearly and never fabricate results when a tool fails.

## What I Would Change with More Time

With more time, I would extend the project in several directions.

### User Interface and Streaming

I would add a **Streamlit-based graphical interface** to make the research agent easier to use than the current command-line interface. The interface could include conversation history, tool activity, downloaded papers, and clearer presentation of research results.

I would also add **streaming responses** so that the agent's answer is displayed incrementally as it is generated. This would provide a more responsive and interactive user experience, especially for longer research tasks.

### Model Flexibility

I would decouple the agent from a single provider and support both **closed and open models**. For example, the application could allow users to select between hosted APIs and local/open-source models through a common LLM interface.

### Richer Research Assistant

I would add more research-oriented tools to make the agent a more complete research assistant. Possible extensions include PDF text extraction and retrieval, paper summarization, citation lookup, related-paper discovery, and other tools that support the workflow from finding a paper to understanding and comparing its contents.

## What I Would Change at Production Scale

At production scale, I would add persistent conversation storage so context can survive application restarts and multiple sessions. A database-backed checkpointer would replace the current in-memory application state.

I would also improve the download pipeline with retries, stronger URL validation, file-size limits, safe file naming, and asynchronous/background downloads. Large downloads should not block the agent request.