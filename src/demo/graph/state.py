import operator
from typing import Any, Dict, Optional

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage, ToolMessage
from typing_extensions import Annotated, TypedDict

# from langgraph.graph import MessagesState


class InputState(TypedDict):
    """Input state for the graph."""

    input: Dict[str, Any]
    structure: Dict[str, Any]
    qualifiers: Dict[str, Any]
    manager_id: str


class GraphState(InputState):
    """State of the graph."""

    draft: Optional[Dict[str, Any]]
    check_result: Optional[Dict[str, Any]]


# class MessagesState(TypedDict):
#     messages: Annotated[list[AnyMessage], operator.add]
#     llm_calls: int


# def llm_call(state: dict):
#     """LLM decides whether to call a tool or not"""
#     return {
#         "messages": [
#             model_with_tools.invoke(
#                 [
#                     SystemMessage(
#                         content="You are a helpful assistant tasked with performing arithmetic on a set of inputs."
#                     )
#                 ]
#                 + state["messages"]
#             )
#         ],
#         "llm_calls": state.get("llm_calls", 0) + 1,
#     }


# def tool_node(state: dict):
#     """Performs the tool call"""
#     result = []
#     for tool_call in state["messages"][-1].tool_calls:
#         tool = tools_by_name[tool_call["name"]]
#         observation = tool.invoke(tool_call["args"])
#         result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
#     return {"messages": result}
