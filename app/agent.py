from typing import Annotated

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from tools import calculate_budget, search_flights, search_hotels

with open("system_prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


tools_list = [search_flights, search_hotels, calculate_budget]
llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools(tools_list)


def agent_node(state: AgentState):
    messages = state["messages"]
    if not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(tools_list))
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition, {"tools": "tools", END: END})
builder.add_edge("tools", "agent")

graph = builder.compile()


def run_agent(messages: list) -> tuple[str, dict]:
    """Invoke the agent with a list of LangChain messages, return (answer, usage_metadata)."""
    result = graph.invoke({"messages": messages})
    final = result["messages"][-1]
    usage = getattr(final, "usage_metadata", None) or {}
    return final.content, usage


# CLI entry point kept for local testing
if __name__ == "__main__":
    print("=" * 60)
    print("TravelBuddy - Trợ lý Du lịch Thông minh")
    print("   Gõ 'quit' để thoát")
    print("=" * 60)

    history: list = []
    while True:
        user_input = input("\nBạn: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break

        history.append(HumanMessage(content=user_input))
        print("\nTravelBuddy đang suy nghĩ...")
        answer, _ = run_agent(history)
        history.append(AIMessage(content=answer))
        print(f"\nTravelBuddy: {answer}")
