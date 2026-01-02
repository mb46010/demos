"""Module for input validation nodes in the performance review graph."""

import json
import logging
from pathlib import Path
from pprint import pprint
from typing import List, Optional

from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from demo.graph.consts import KEY_CHECK_RESULT, KEY_INPUT, KEY_QUALIFIERS
from demo.graph.model import llm
from demo.graph.state import GraphState
from demo.tools.validate_input import validate_input
from demo.utils.loader import load_prompt

logger = logging.getLogger(__name__)


class CheckResult(BaseModel):
    """Structured output for the input check node."""

    valid: bool = Field(..., description="Whether the input is valid")
    errors: List[str] = Field(default_factory=list, description="List of validation errors")
    message_to_manager: Optional[str] = Field(None, description="Message to be sent back to the manager")


# Node for InputCheck (N1)
def input_check(state: GraphState):
    """Validate the manager's input using both a basic tool and an LLM.

    This node:
    1. Runs a basic validation tool on the raw input.
    2. Feeds both the input and tool results to an LLM for semantic check.
    3. Merges results and ensures consistency (e.g., if errors exist, valid must be False).
    """
    logger.info("Stage: %s started.", KEY_CHECK_RESULT)

    # Load prompt and join if it's a list
    prompt_raw = load_prompt(Path("src/prompts/n_input.json"))
    if isinstance(prompt_raw, list):
        prompt_template = "\n".join(prompt_raw)
    else:
        prompt_template = prompt_raw

    # Validate input
    validation_result = validate_input(state[KEY_INPUT], state[KEY_QUALIFIERS])

    # Fill the prompt
    filled_prompt = prompt_template.format(
        manager_input=json.dumps(state[KEY_INPUT], indent=2),
        validation_tool_output=json.dumps(validation_result, indent=2),
    )

    # Invoke LLM with structured output
    response = llm.with_structured_output(CheckResult).invoke([HumanMessage(content=filled_prompt)])

    # Update state
    check_result = response.model_dump()

    print()
    print("LLM Check Result:")
    pprint(check_result)

    # Fixing LLM inconsistencies and ensuring tool output is respected
    errors = check_result.get("errors", [])
    message_to_manager = check_result.get("message_to_manager")
    valid = check_result.get("valid")

    # 1. Respect Tool Results: If tool found errors, force valid to False and merge errors
    if not validation_result.get("valid", True):
        if valid:
            logger.warning("Validation tool found errors but LLM suggested input is valid. Forcing valid=False.")
            valid = False

        tool_errors = validation_result.get("errors", [])
        for err in tool_errors:
            if err not in errors:
                errors.append(err)

    # 2. Consistency: If there are errors, valid MUST be False
    if errors and valid:
        logger.warning("Errors found but valid is True. Forcing valid=False.")
        valid = False

    # 3. Consistency: If valid is False, message_to_manager MUST be provided
    if not valid and not message_to_manager:
        logger.warning("Validation failed but no message_to_manager provided. Generating fallback message.")
        if errors:
            message_to_manager = "The submitted information requires corrections:\n- " + "\n- ".join(errors)
        else:
            message_to_manager = "The submitted information is invalid. Please review your entries."

    # 4. Consistency: If valid is True, message_to_manager SHOULD be None
    if valid and message_to_manager:
        logger.warning(
            "Validation passed but message_to_manager was provided. Clearing message: %s", message_to_manager
        )
        message_to_manager = None

    # Update state
    final_result = {
        "valid": valid,
        "errors": errors,
        "message_to_manager": message_to_manager,
    }

    print()
    print("Final Validation Result:")
    pprint(final_result)

    logger.info("Stage: %s passed.", KEY_CHECK_RESULT)
    return {KEY_CHECK_RESULT: final_result}


def check_valid(state: GraphState):
    """Gate function to check if valid == True."""
    # Safe access using .get() to handle cases where check_result or valid might be missing/None
    check_result = state.get(KEY_CHECK_RESULT)
    if check_result and check_result.get("valid"):
        logger.info("Edge: %s value is True.", KEY_CHECK_RESULT)
        return "True"
    logger.info("Edge: %s value is False.", KEY_CHECK_RESULT)
    return "False"
