from langchain_core.messages import SystemMessage

class Agent:
    def __init__(self, llm_with_tools, system_prompt):
        self.llm_with_tools = llm_with_tools
        self.system_prompt = system_prompt

    def run(self, chat_state):
        messages = [
            SystemMessage(content=self.system_prompt),
            *chat_state["messages"]
        ]
        response = self.llm_with_tools.invoke(messages)
        return {"messages": [response]}