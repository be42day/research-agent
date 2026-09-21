import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from chat_model.tools import chat_tools
from chat_model.state import ChatState
from chat_model.graph import ChatGraph


def extract_text(content) -> str:
    """Extract text from string or content blocks."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict)
            and block.get("type") == "text"
        )
    return str(content)



load_dotenv()
os.getenv("GOOGLE_API_KEY")


# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

# Bind tools to LLM
llm_with_tools = llm.bind_tools(chat_tools)

# Define graph state
state_schema = ChatState

# Define System Prompt
system_prompt = """
You are a helpful AI assistant.

Your job is to answer the user's questions accurately.
If you need additional information, use the available tools.
If a tool fails, times out, or returns an error, clearly tell the user that the requested operation 
could not be completed. Do not pretend that the tool succeeded and do not fabricate or guess 
the missing information.

Do not make up information.
When a tool error prevents you from answering the user's question, explain the failure briefly and clearly.
"""

# Define Graph
chat_graph = ChatGraph(state_schema, system_prompt, llm_with_tools, chat_tools).make()


def main():

    print("Research Agent")
    print("Type 'exit' to quit.\n")

    messages = []

    while True:

        user_input = input("You: ")

        if user_input.lower() in {"exit", "quit"}:
            break

        messages.append(
            HumanMessage(content=user_input)
        )

        result = chat_graph.invoke({
            "messages": messages
        })

        message = result["messages"][-1]

        text = extract_text(message.content)

        print(f"\nAgent: {text}\n")


if __name__ == "__main__":
    main()