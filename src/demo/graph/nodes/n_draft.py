"""Module for input validation nodes in the performance review graph."""

import json
import logging
from pathlib import Path
from pprint import pprint
from typing import List, Optional

from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from demo.graph.model import llm
from demo.graph.state import GraphState
from demo.tools.validate_input import validate_input
from demo.utils.loader import load_prompt

logger = logging.getLogger(__name__)


def create_draft(state: GraphState):
    """Create a draft of the performance review."""
    # TBD
    draft = "placeholder"
    state["draft"] = draft
    state["last_node"] = "draft"

    return state
