"""Module for input validation nodes in the performance review graph."""

import json
import logging
from pathlib import Path
from pprint import pprint
from typing import List, Optional

from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from demo.graph.consts import KEY_DRAFT, KEY_INPUT, KEY_STRUCTURE, NODE_CREATE_DRAFT
from demo.graph.model import llm
from demo.graph.state import GraphState
from demo.tools.validate_input import validate_input
from demo.utils.loader import load_prompt

logger = logging.getLogger(__name__)


class DraftResult(BaseModel):
    """Structured output for the draft node."""

    draft: str = Field(..., description="Draft of the performance review")


def create_draft(state: GraphState):
    """Create a draft of the performance review."""
    logger.info("Stage: %s started.", NODE_CREATE_DRAFT)

    # Load prompt and join if it's a list
    prompt_raw = load_prompt(Path("src/prompts/n_draft.json"))
    if isinstance(prompt_raw, list):
        prompt_template = "\n".join(prompt_raw)
    else:
        prompt_template = prompt_raw

    # Fill the prompt
    filled_prompt = prompt_template.format(
        manager_input=json.dumps(state[KEY_INPUT], indent=2),
        review_template_structure=json.dumps(state[KEY_STRUCTURE], indent=2),
    )

    # Generate draft
    # Invoke LLM with structured output
    response = llm.with_structured_output(DraftResult).invoke([HumanMessage(content=filled_prompt)])

    # Update state
    draft_result = response.model_dump()

    # print()
    # print("LLM Draft Result:")
    # pprint(draft_result)

    logger.info("Stage: %s completed.", NODE_CREATE_DRAFT)
    return {KEY_DRAFT: draft_result["draft"]}
