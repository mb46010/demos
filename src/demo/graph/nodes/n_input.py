"""Module for input validation nodes in the performance review graph."""

import json
import logging
from pprint import pprint
from typing import Any, Dict, List, Optional

from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from demo.graph.consts import KEY_CHECK_RESULT, KEY_INPUT, KEY_QUALIFIERS, NODE_INPUT_CHECK
from demo.graph.state import GraphState
from demo.prompts.prompt_loader import PromptLoader
from demo.tools.validate_input import validate_input

logger = logging.getLogger(__name__)


class CheckResult(BaseModel):
    """Structured output for the input check node."""

    valid: bool = Field(..., description="Whether the input is valid")
    errors: List[str] = Field(default_factory=list, description="List of validation errors")
    message_to_manager: Optional[str] = Field(None, description="Message to be sent back to the manager")


# ============================================================================
# Factory Pattern (Recommended)
# ============================================================================


def create_input_node(llm, prompt_loader: PromptLoader):
    """Factory function that creates an input check node with injected dependencies.

    Args:
        llm: Language model instance
        prompt_loader: PromptLoader instance for loading prompts

    Returns:
        Configured input check node function
    """

    def input_check(state: GraphState) -> Dict[str, Any]:
        """Validate the manager's input using both a basic tool and an LLM."""
        logger.info("Stage: %s started.", NODE_INPUT_CHECK)

        try:
            # 1. Basic Validation Tool
            validation_result = validate_input(state[KEY_INPUT], state[KEY_QUALIFIERS])

            # 2. Semantic Check with LLM
            # Load and format prompt
            filled_prompt = prompt_loader.get_formatted(
                "n_input",
                manager_input=json.dumps(state[KEY_INPUT], indent=2),
                validation_tool_output=json.dumps(validation_result, indent=2),
            )

            # Invoke LLM
            response = llm.with_structured_output(CheckResult).invoke([HumanMessage(content=filled_prompt)])

            if response is None:
                raise ValueError("LLM failed to return a valid structured output.")

            check_result = response.model_dump()

            # 3. Merge and Consistency Check
            final_result = _ensure_consistency(check_result, validation_result)

            logger.info("Stage: %s completed.", NODE_INPUT_CHECK)
            print()
            print("Final Validation Result:")
            pprint(final_result)
            return {KEY_CHECK_RESULT: final_result}

        except Exception as e:
            logger.error(f"Stage: {NODE_INPUT_CHECK} failed: {e}", exc_info=True)
            raise

    return input_check


# ============================================================================
# Class Pattern (Alternative)
# ============================================================================


class InputChecker:
    """Input check node as a callable class."""

    def __init__(
        self,
        llm,
        prompt_loader: PromptLoader,
    ):
        """Initialize input checker.

        Args:
            llm: Language model instance
            prompt_loader: PromptLoader instance
        """
        self.llm = llm
        self.prompt_loader = prompt_loader

    def __call__(self, state: GraphState) -> Dict[str, Any]:
        """Make the class callable as a LangGraph node."""
        logger.info("Stage: %s started.", NODE_INPUT_CHECK)

        try:
            return self._validate(state)
        except Exception as e:
            logger.error(f"Stage: {NODE_INPUT_CHECK} failed: {e}", exc_info=True)
            raise

    def _validate(self, state: GraphState) -> Dict[str, Any]:
        # 1. Basic Validation Tool
        validation_result = validate_input(state[KEY_INPUT], state[KEY_QUALIFIERS])

        # 2. Semantic Check with LLM
        prompt = self._build_prompt(state, validation_result)
        response = self.llm.with_structured_output(CheckResult).invoke([HumanMessage(content=prompt)])

        if response is None:
            raise ValueError("LLM failed to return a valid structured output.")

        check_result = response.model_dump()

        # 3. Merge and Consistency Check
        final_result = _ensure_consistency(check_result, validation_result)

        logger.info("Stage: %s completed.", NODE_INPUT_CHECK)
        print()
        print("Final Validation Result:")
        pprint(final_result)
        return {KEY_CHECK_RESULT: final_result}

    def _build_prompt(self, state: GraphState, validation_result: Dict) -> str:
        return self.prompt_loader.get_formatted(
            "n_input",
            manager_input=json.dumps(state[KEY_INPUT], indent=2),
            validation_tool_output=json.dumps(validation_result, indent=2),
        )


def _ensure_consistency(check_result: Dict, validation_result: Dict) -> Dict:
    """Helper to ensure consistency between tool and LLM results."""
    errors = check_result.get("errors", [])
    message_to_manager = check_result.get("message_to_manager")
    valid = check_result.get("valid")

    # 1. Respect Tool Results
    if not validation_result.get("valid", True):
        if valid:
            logger.warning("Validation tool found errors but LLM suggested input is valid. Forcing valid=False.")
            valid = False

        tool_errors = validation_result.get("errors", [])
        for err in tool_errors:
            if err not in errors:
                errors.append(err)

    # 2. Consistency: If errors exist, valid must be False
    if errors and valid:
        logger.warning("Errors found but valid is True. Forcing valid=False.")
        valid = False

    # 3. Consistency: If valid is False, message_to_manager must be provided
    if not valid and not message_to_manager:
        logger.warning("Validation failed but no message_to_manager provided. Generating fallback message.")
        if errors:
            message_to_manager = "The submitted information requires corrections:\n- " + "\n- ".join(errors)
        else:
            message_to_manager = "The submitted information is invalid. Please review your entries."

    # 4. Consistency: If valid is True, message_to_manager should be None
    if valid and message_to_manager:
        logger.warning(
            "Validation passed but message_to_manager was provided. Clearing message: %s", message_to_manager
        )
        message_to_manager = None

    return {
        "valid": valid,
        "errors": errors,
        "message_to_manager": message_to_manager,
    }


def check_valid(state: GraphState):
    """Gate function to check if valid == True."""
    # Safe access using .get() to handle cases where check_result or valid might be missing/None
    check_result = state.get(KEY_CHECK_RESULT)
    if check_result and check_result.get("valid"):
        logger.info("Edge: %s value is True.", KEY_CHECK_RESULT)
        return "True"
    logger.info("Edge: %s value is False.", KEY_CHECK_RESULT)
    return "False"
