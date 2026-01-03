import json
import logging
from pathlib import Path
from pprint import pprint
from typing import Any, Dict

from langchain_core.messages import HumanMessage

from demo.graph.consts import (
    KEY_DRAFT,
    KEY_FACT_CHECKER_CLAIMS_EXTRACTED,
    KEY_INPUT,
    KEY_REWRITER,
    KEY_STRUCTURE,
    NODE_REWRITER,
)
from demo.graph.model import llm
from demo.graph.nodes.n_draft import DraftResult
from demo.graph.state import GraphState
from demo.utils.loader import load_prompt
from demo.utils.parse_facts import parse_fact_extractor_output

logger = logging.getLogger(__name__)


def fc_rewriter(state: GraphState):
    """Verify extracted claims (placeholder)."""
    logger.info("Stage: %s started.", NODE_REWRITER)

    # Overwrite draft and ncrement revision number
    current_revision = state.get("revision_number", 0) or 0
    new_revision = current_revision + 1

    try:
        claims_extracted = state.get(KEY_FACT_CHECKER_CLAIMS_EXTRACTED)
        feedback = parse_fact_extractor_output(claims_extracted)

        # Verify claims with LLM?
        # Load prompt and join if it's a list
        prompt_template = load_prompt(Path("src/prompts/n_rewriter.json"))

        # Fill the prompt
        filled_prompt = prompt_template.format(
            draft=state[KEY_DRAFT],
            feedback=json.dumps(feedback, indent=2),
            manager_input=json.dumps(state[KEY_INPUT], indent=2),
            # review_template_structure=json.dumps(state[KEY_STRUCTURE], indent=2),
        )

        # Generate draft
        # Invoke LLM with structured output
        response = llm.with_structured_output(DraftResult).invoke([HumanMessage(content=filled_prompt)])

        # Update state
        if response is None:
            raise ValueError("LLM failed to return a valid structured output.")
        try:
            new_draft = response.model_dump()
        except Exception as e:
            logger.exception("Failed to parse LLM response: %s", str(e))
            raise

        logger.info("Stage: %s completed. Revision: %d", NODE_REWRITER, new_revision)
        return {KEY_REWRITER: new_draft["draft"], "revision_number": new_revision}

    except Exception as e:
        logger.error("Stage: %s failed with error: %s. Incrementing revision and continuing.", NODE_REWRITER, str(e))
        # Increment revision even on failure, but don't update the draft (preserving previous state)
        return {"revision_number": new_revision}
