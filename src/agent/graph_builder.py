from langgraph.prebuilt import tools_condition
from langgraph.graph import END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph

from src.agent.ai_agent import AIAgent, State
from typing import Literal


class BotPipeline:
    def __init__(self):
        self.ai_agent = AIAgent()
        self.memory = MemorySaver()
        self.context = []
        # self.retain_graph = True


    def relevance_condition(self, state: State) -> Literal["human_node", None]:
        """Check if query is relevant to the role or not."""
        return state.get("next_step", "react_agent")

    def final_condition(self, state: State) -> Literal["human_node", None]:
        """Check if more clarification is required or not"""
        return state.get("next_step", END)
    
    def build_graph(self):
        self.graph_builder = StateGraph(State)
        self.graph_builder.add_node(self.ai_agent.initial_analysis)
        self.graph_builder.add_node(self.ai_agent.react_agent)
        self.graph_builder.add_node(self.ai_agent.tools)
        self.graph_builder.add_node(self.ai_agent.final_analysis)
        self.graph_builder.add_node(self.ai_agent.summarize_conversation)

        self.graph_builder.set_entry_point("initial_analysis")
        self.graph_builder.add_conditional_edges(
            "initial_analysis",
            self.relevance_condition,
            {END : END, "react_agent": "react_agent"},
        )
        self.graph_builder.add_conditional_edges(
            "react_agent",
            tools_condition,
            {"tools": "tools", END : "final_analysis"},
        )
        self.graph_builder.add_edge("tools", "react_agent")
        self.graph_builder.add_conditional_edges(
            "final_analysis",
            self.final_condition,
            {END : "summarize_conversation", "react_agent": "react_agent"},
        )
        self.graph_builder.add_edge("summarize_conversation", END)

        self.graph = self.graph_builder.compile(checkpointer=self.memory)

    def execute_graph(self, query: str, thread_id: str):
            responses = []
            for step in self.graph.stream(
                {"messages": [{"role": "user", "content": query}]},
                stream_mode="values",
                config={"configurable": {"thread_id": thread_id}},
            ):

                response = step["messages"][-1]
                responses.append(response)

            return responses[-1].content