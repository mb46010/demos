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
    NODE_FACT_CHECKER_CLAIM_EXTRACTOR,
)
from demo.graph.model import llm
from demo.graph.nodes.fact_models import FactPairs
from demo.graph.state import GraphState
from demo.utils.loader import load_json, load_prompt

logger = logging.getLogger(__name__)


def fc_extractor(state: GraphState):
    """Extract claim-fact pairs."""
    logger.info("Stage: %s started.", NODE_FACT_CHECKER_CLAIM_EXTRACTOR)

    # Load prompt and join if it's a list

    prompt_template = load_prompt(Path("src/prompts/n_fact_extractor.json"))
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
    if response is None:
        raise ValueError("LLM failed to return a valid structured output.")
    try:
        fact_pairs = response.model_dump()
    except Exception as e:
        logger.exception("Failed to parse LLM response: %s", str(e))
        raise

    # print()
    # print("LLM Fact Pairs:")
    # pprint(fact_pairs)

    logger.info("Stage: %s passed.", NODE_FACT_CHECKER_CLAIM_EXTRACTOR)
    return {KEY_FACT_CHECKER_CLAIMS_EXTRACTED: fact_pairs["claim_fact_pairs"]}


def needs_rewrite(state: GraphState) -> str:
    """Check if claims were extracted successfully.

    If discrepancies (unsupported or partially supported claims) are found,
    we return "True" to trigger a rewrite.
    If all claims are supported, we return "False" to skip/stop the rewrite.
    """
    current_revision = state.get("revision_number", 0) or 0
    if current_revision >= 3:
        logger.warning("Stage: %s max revisions reached (3). Stopping loop.", NODE_FACT_CHECKER_CLAIM_EXTRACTOR)
        return "False"

    claims_data = state.get(KEY_FACT_CHECKER_CLAIMS_EXTRACTED)
    if not claims_data:
        logger.info("Stage: %s found no issues: no modifications needed.", NODE_FACT_CHECKER_CLAIM_EXTRACTOR)
        return "False"

    # Check for discrepancies in links
    links = claims_data.get("links", [])
    issues = [link for link in links if link.get("verdict") != "supported"]

    if issues:
        # We found issues (unsupported or partially supported)
        logger.info(
            "Stage: %s found %s discrepancies: modifications needed.", NODE_FACT_CHECKER_CLAIM_EXTRACTOR, len(issues)
        )
        return "True"

    # All links are "supported"
    logger.info("Stage: %s found no issues: all claims supported.", NODE_FACT_CHECKER_CLAIM_EXTRACTOR)
    return "False"
