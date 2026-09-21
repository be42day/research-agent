from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool

from chat_model.graph import ChatGraph
from chat_model.state import ChatState


class FakeLLM:

    def invoke(self, messages):
        return AIMessage(
            content="Hello! How can I help you?"
        )


def test_agent_without_tools():

    llm = FakeLLM()

    graph = ChatGraph(
        state_schema=ChatState,
        system_prompt="You are a helpful assistant.",
        llm_with_tools=llm,
        chat_tools=[],
    ).make()

    result = graph.invoke({
        "messages": [
            HumanMessage(content="Hello")
        ]
    })

    assert result["messages"][-1].content == (
        "Hello! How can I help you?"
    )


@tool
def get_weather(city: str) -> str:
    """Get the weather for a city."""
    return f"The weather in {city} is sunny."

@tool
def broken_tool(query: str) -> str:
    """A tool that always fails."""
    raise Exception("Service unavailable")


class FakeToolCallingLLM:

    def __init__(self):
        self.call_count = 0

    def invoke(self, messages):
        self.call_count += 1

        if self.call_count == 1:
            return AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "get_weather",
                        "args": {"city": "Tehran"},
                        "id": "call_1",
                        "type": "tool_call",
                    }
                ],
            )

        return AIMessage(
            content="The weather in Tehran is sunny."
        )


class FakeToolFailureLLM:

    def __init__(self):
        self.call_count = 0

    def invoke(self, messages):
        self.call_count += 1

        if self.call_count == 1:
            return AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "broken_tool",
                        "args": {"query": "test"},
                        "id": "call_1",
                        "type": "tool_call",
                    }
                ],
            )

        return AIMessage(
            content=(
                "I couldn't complete the request because "
                "the tool failed."
            )
        )


def test_agent_with_tool():

    llm = FakeToolCallingLLM()

    graph = ChatGraph(
        state_schema=ChatState,
        system_prompt="You are a helpful assistant.",
        llm_with_tools=llm,
        chat_tools=[get_weather],
    ).make()

    result = graph.invoke({
        "messages": [
            HumanMessage(
                content="What is the weather in Tehran?"
            )
        ]
    })

    assert result["messages"][-1].content == (
        "The weather in Tehran is sunny."
    )

    assert any(
        message.type == "tool"
        for message in result["messages"]
    )




def test_agent_handles_tool_failure():

    llm = FakeToolFailureLLM()

    graph = ChatGraph(
        state_schema=ChatState,
        system_prompt="You are a helpful assistant.",
        llm_with_tools=llm,
        chat_tools=[broken_tool],
    ).make()

    result = graph.invoke({
        "messages": [
            HumanMessage(content="Search for something.")
        ]
    })

    final_response = result["messages"][-1].content

    assert "couldn't complete" in final_response
    assert "tool failed" in final_response