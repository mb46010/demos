"""Module for fact extraction nodes in the performance review graph."""

import json
import logging
from pathlib import Path
from pprint import pprint
from typing import Dict, List, Optional

from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from demo.graph.consts import (
    KEY_DRAFT,
    KEY_FACT_CHECKER_CLAIMS_EXTRACTED,
    KEY_INPUT,
)
from demo.graph.model import llm
from demo.graph.nodes.fact_models import FactPairs
from demo.graph.state import GraphState
from demo.utils.loader import load_json, load_prompt

logger = logging.getLogger(__name__)


def fc_extractor(state: GraphState):
    """Extract claim-fact pairs."""
    logger.info("Stage: %s started.", KEY_FACT_CHECKER_CLAIMS_EXTRACTED)

    # Load prompt and join if it's a list
    try:
        prompt_raw = load_prompt(Path("src/prompts/n_fact_extractor.json"))
    except FileNotFoundError:
        logger.warning("Prompt file src/prompts/n_fact_extractor.json not found. Using a default prompt.")
        prompt_raw = "Extract claim-fact pairs from the following manager input.\n\nManager Input:\n{manager_input}"

    if isinstance(prompt_raw, list):
        prompt_template = "\n".join(prompt_raw)
    else:
        prompt_template = prompt_raw

    example_data = load_json(Path("docs/templates/claim_fact_pairs.json"))

    # Fill the prompt
    filled_prompt = prompt_template.format(
        manager_input=json.dumps(state[KEY_INPUT], indent=2),
        review=state.get(KEY_DRAFT, ""),
        example=json.dumps(example_data, indent=2),
    )

    # Generate structured output
    response = llm.with_structured_output(FactPairs).invoke([HumanMessage(content=filled_prompt)])

    # Update state
    fact_pairs = response.model_dump()

    print()
    print("LLM Fact Pairs:")
    pprint(fact_pairs)

    logger.info("Stage: %s passed.", KEY_FACT_CHECKER_CLAIMS_EXTRACTED)
    return {KEY_FACT_CHECKER_CLAIMS_EXTRACTED: fact_pairs["claim_fact_pairs"]}


def check_fc_result(state: GraphState) -> str:
    """Check if claims were extracted successfully."""
    if state.get(KEY_FACT_CHECKER_CLAIMS_EXTRACTED):
        return "True"
    return "False"
