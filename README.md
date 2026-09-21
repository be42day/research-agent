# Research Agent

A simple research assistant built with **LangGraph** and **Google Gemini** that can search arXiv papers and download selected PDFs.

The agent supports multi-turn conversations and can decide when to use the available tools based on the user's request.

## Features

* Multi-turn conversational context
* Search research papers on arXiv
* Download paper PDFs
* Tool-calling with LangGraph
* Graceful tool failure handling
* No fabricated results when a tool fails
* Unit tests for tool success and failure paths
* Integration tests for the full agent loop
* Optional LangSmith tracing for observability

## Project Structure

```text
chat-model/
├── src/
│   └── chat_model/
│       ├── app.py
│       ├── agent.py
│       ├── graph.py
│       ├── state.py
│       └── tools.py
├── tests/
│   ├── test_tools.py
│   └── test_agent.py
├── papers/              # Downloaded PDFs
├── .env
├── pyproject.toml
└── README.md
```

## Requirements

* Python 3.13+
* [uv](https://docs.astral.sh/uv/)
* A Google Gemini API key

LangSmith is optional and only required if tracing is enabled.

## Setup

Clone the repository and move into the project directory:

```bash
git clone https://github.com/be42day/research-agent.git
cd chat-model
```

Install the project dependencies with `uv`:

```bash
uv sync
```

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_api_key
```

### Optional: LangSmith Tracing

The agent can use LangSmith for tracing and observability.

Add the following variables to the `.env` file:

```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_ENDPOINT=your_langsmith_endpoint
LANGSMITH_PROJECT=chat-model
```

When enabled, LangSmith traces the agent execution, including:

* LLM calls
* Tool-call decisions
* Tool inputs and outputs
* Tool failures
* The overall agent execution flow

LangSmith tracing is optional. The application can run without it by setting:

```env
LANGSMITH_TRACING=false
```

## Run

From the project root, run:

```bash
uv run python src/chat_model/app.py
```

The application starts an interactive chat loop.

Example:

```text
You: Find papers about 3D vision algorithms

Agent: ...

You: Download the most recent one

Agent: ...
```

Downloaded PDFs are stored in the project's `papers/` directory.

## Available Tools

### `search_arxiv`

Searches arXiv for research papers related to a topic.

Input:

```text
topic
max_results
```

Example request:

```text
Find papers about physics-informed neural networks.
```

### `download_pdf`

Downloads a PDF from a URL and returns the local file path.

Input:

```text
url
output_dir
```

Example request:

```text
Download the latest paper.
```

The agent can first use `search_arxiv` to identify the paper and then use `download_pdf` when the user requests the PDF.

## Agent Behavior

The agent uses the tools only when they are relevant to the user's request.

For example:

```text
General question
    → Answer directly
```

```text
Search for papers
    → search_arxiv
```

```text
Search for a paper and download it
    → search_arxiv
    → download_pdf
```

When a tool fails, the error is passed back to the agent and the agent is instructed to clearly report the failure instead of inventing a result.

## Graceful Failure Handling

Tool failures such as API errors, HTTP errors, timeouts, invalid URLs, or file-system errors are handled without silently producing a fabricated answer.

The tool errors are handled by the LangGraph `ToolNode`:

```python
ToolNode(
    chat_tools,
    handle_tool_errors=True,
)
```

The system prompt also explicitly instructs the agent not to pretend that a failed tool succeeded.

## Testing

The project includes:

### Unit tests

Unit tests cover both successful and failure cases for the tools:

* arXiv search success
* arXiv search failure
* PDF download success
* PDF download failure

### Integration tests

Integration tests exercise the agent loop, including:

* Agent response without tools
* Tool calling and tool execution
* Graceful handling of tool failures

Run all tests with a single command:

```bash
uv run pytest
```

Expected result:

```text
7 passed
```

## Observability

The project supports **LangSmith tracing** for inspecting agent execution.

When enabled, traces can be used to inspect:

* LLM calls
* Tool-call decisions
* Tool inputs and outputs
* Execution flow
* Tool failures

This is useful for understanding why the agent selected a particular tool and how the tool-calling loop was executed.

## Notes

The `papers/` directory contains runtime-generated PDF files and is separate from the source code under `src/`.

The application maintains conversation history during the current interactive session, allowing the agent to resolve follow-up questions that depend on previous turns.