"""Module for fact verification nodes in the performance review graph."""

import logging

from demo.graph.consts import KEY_FACT_CHECKER_CLAIMS_VERIFIED
from demo.graph.state import GraphState

logger = logging.getLogger(__name__)


def fc_verifier(state: GraphState):
    """Verify extracted claims (placeholder)."""
    logger.info("Stage: %s started.", KEY_FACT_CHECKER_CLAIMS_VERIFIED)

    # Placeholder: just pass along the extracted claims as verified for now
    # In a real implementation, this would call an LLM to verify facts against evidence
    claims_extracted = state.get("claims_extracted")

    logger.info("Stage: %s passed.", KEY_FACT_CHECKER_CLAIMS_VERIFIED)
    return {KEY_FACT_CHECKER_CLAIMS_VERIFIED: claims_extracted}
