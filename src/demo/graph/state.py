"""Module defining the state structure for the performance review graph."""

import operator
from typing import Any, Dict, Optional

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage, ToolMessage
from typing_extensions import Annotated, TypedDict


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
    claims_extracted: Optional[Dict[str, Any]]
    revision_number: int
