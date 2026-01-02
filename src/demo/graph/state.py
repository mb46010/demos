from typing import Any, Dict
from langchain.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage, ToolMessage

from typing_extensions import TypedDict, Annotated
import operator

# from langgraph.graph import MessagesState

class GraphState(TypedDict):
    """State of the graph."""
    input: Dict[str, Any]
    structure: Dict[str, Any]
    qualifiers: Dict[str, Any]
    draft: Dict[str, Any]
    manager_id: str


class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int

def llm_call(state: dict):
    """LLM decides whether to call a tool or not"""

    return {
        "messages": [
            model_with_tools.invoke(
                [
                    SystemMessage(
                        content="You are a helpful assistant tasked with performing arithmetic on a set of inputs."
                    )
                ]
                + state["messages"]
            )
        ],
        "llm_calls": state.get('llm_calls', 0) + 1
    }

def tool_node(state: dict):
    """Performs the tool call"""

    result = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return {"messages": result}

# from typing import Literal
# from langgraph.graph import StateGraph, START, END


# def should_continue(state: MessagesState) -> Literal["tool_node", END]:
#     """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

#     messages = state["messages"]
#     last_message = messages[-1]

#     # If the LLM makes a tool call, then perform an action
#     if last_message.tool_calls:
#         return "tool_node"

#     # Otherwise, we stop (reply to the user)
#     return END