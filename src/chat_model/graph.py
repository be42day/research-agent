from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition, ToolNode

from chat_model.agent import Agent


class ChatGraph:
    def __init__(self, state_schema, system_prompt, llm_with_tools, chat_tools):
        self.state_schema = state_schema
        self.system_prompt = system_prompt
        self.llm_with_tools = llm_with_tools
        self.chat_tools = chat_tools

    def make(self):
        graph = StateGraph(self.state_schema)

        chat_agent = Agent(
            llm_with_tools=self.llm_with_tools,
            system_prompt=self.system_prompt,
        )

        tool_node = ToolNode(
            self.chat_tools,
            handle_tool_errors=True,
        )

        # Nodes
        graph.add_node("llm", chat_agent.run)
        graph.add_node("tools", tool_node)

        # Edges
        graph.add_edge(START, "llm")
        graph.add_conditional_edges(
            "llm",
            tools_condition,
            {"tools": "tools", "__end__": END},
        )
        graph.add_edge("tools", "llm")

        return graph.compile()