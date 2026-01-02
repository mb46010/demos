"""Module for fact verification nodes in the performance review graph."""

import logging

from demo.graph.consts import KEY_FACT_CHECKER_CLAIMS_EXTRACTED, KEY_FACT_CHECKER_REWRITTER
from demo.graph.state import GraphState
from demo.utils.parse_facts import parse_fact_extractor_output

logger = logging.getLogger(__name__)


def fc_rewriter(state: GraphState):
    """Verify extracted claims (placeholder)."""
    logger.info("Stage: %s started.", KEY_FACT_CHECKER_REWRITTER)

    claims_extracted = state.get(KEY_FACT_CHECKER_CLAIMS_EXTRACTED)
    feedback = parse_fact_extractor_output(claims_extracted)

    # Verify claims with LLM?

    new_draft = ""

    logger.info("Stage: %s passed.", KEY_FACT_CHECKER_REWRITTER)
    return {KEY_FACT_CHECKER_REWRITTER: new_draft}
