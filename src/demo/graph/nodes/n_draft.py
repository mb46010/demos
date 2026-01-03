"""Refactored draft creation node using PromptLoader for better testability."""

import json
import logging
from pathlib import Path
from typing import Any, Dict

from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from demo.config.config import Config
from demo.graph.consts import KEY_DRAFT, KEY_INPUT, KEY_STRUCTURE
from demo.graph.state import GraphState
from demo.prompts.prompt_loader import PromptLoader

logger = logging.getLogger(__name__)


class DraftResult(BaseModel):
    """Structured output for the draft node."""

    draft: str = Field(..., description="Draft of the performance review")


# ============================================================================
# Factory Pattern (Recommended)
# ============================================================================


def create_draft_node(llm, prompt_loader: PromptLoader):
    """Factory function that creates a draft node with injected dependencies.

    Args:
        llm: Language model instance
        prompt_loader: PromptLoader instance for loading prompts

    Returns:
        Configured draft creation node function

    Example:
        >>> from demo.prompt_loader import PromptLoader
        >>> from langchain_openai import ChatOpenAI
        >>>
        >>> llm = ChatOpenAI(model="gpt-4o")
        >>> loader = PromptLoader(prompts_dir=Path("src/prompts"))
        >>> draft_node = create_draft_node(llm, loader)
        >>>
        >>> # Use in graph
        >>> graph.add_node("create_draft", draft_node)
    """

    def create_draft(state: GraphState) -> Dict[str, Any]:
        """Create a draft of the performance review.

        Args:
            state: Current graph state

        Returns:
            Dictionary with updated draft
        """
        logger.info("Stage: create_draft started.")

        try:
            # Load and format prompt using PromptLoader
            filled_prompt = prompt_loader.get_formatted(
                "n_draft",
                manager_input=json.dumps(state[KEY_INPUT], indent=2),
                review_template_structure=json.dumps(state[KEY_STRUCTURE], indent=2),
            )

            # Generate draft using LLM
            response = llm.with_structured_output(DraftResult).invoke([HumanMessage(content=filled_prompt)])

            # Extract result
            draft_result = response.model_dump()

            logger.info("Stage: create_draft completed.")
            return {KEY_DRAFT: draft_result["draft"]}

        except Exception as e:
            logger.error(f"Stage: create_draft failed: {e}", exc_info=True)
            raise

    return create_draft


# ============================================================================
# Class Pattern (Alternative)
# ============================================================================


class DraftCreator:
    """Draft creation node as a callable class.

    Useful when you need to share state or have complex configuration.

    Example:
        >>> creator = DraftCreator(
        ...     llm=llm,
        ...     prompt_loader=loader,
        ...     max_retries=3
        ... )
        >>> graph.add_node("create_draft", creator)
    """

    def __init__(
        self,
        llm,
        prompt_loader: PromptLoader,
        max_retries: int = 3,
        timeout: float = 30.0,
    ):
        """Initialize draft creator.

        Args:
            llm: Language model instance
            prompt_loader: PromptLoader instance
            max_retries: Maximum number of retries on failure
            timeout: Timeout in seconds for LLM call
        """
        self.llm = llm
        self.prompt_loader = prompt_loader
        self.max_retries = max_retries
        self.timeout = timeout

    def __call__(self, state: GraphState) -> Dict[str, Any]:
        """Make the class callable as a LangGraph node."""
        logger.info("Stage: create_draft started.")

        for attempt in range(self.max_retries):
            try:
                return self._create_draft_with_retry(state, attempt)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Stage: create_draft failed after {self.max_retries} attempts")
                    raise
                logger.warning(f"Retry {attempt + 1}/{self.max_retries} after error: {e}")

    def _create_draft_with_retry(self, state: GraphState, attempt: int) -> Dict[str, Any]:
        """Internal method to create draft with retry logic."""
        # Build prompt
        filled_prompt = self._build_prompt(state)

        # Call LLM
        response = self._invoke_llm(filled_prompt)

        # Extract and validate result
        draft_result = response.model_dump()
        self._validate_draft(draft_result["draft"])

        logger.info("Stage: create_draft completed.")
        return {KEY_DRAFT: draft_result["draft"]}

    def _build_prompt(self, state: GraphState) -> str:
        """Build the prompt from state."""
        return self.prompt_loader.get_formatted(
            "n_draft",
            manager_input=json.dumps(state[KEY_INPUT], indent=2),
            review_template_structure=json.dumps(state[KEY_STRUCTURE], indent=2),
        )

    def _invoke_llm(self, prompt: str) -> DraftResult:
        """Invoke LLM with structured output."""
        return self.llm.with_structured_output(DraftResult).invoke([HumanMessage(content=prompt)])

    def _validate_draft(self, draft: str) -> None:
        """Validate the generated draft."""
        if not draft or not draft.strip():
            raise ValueError("Generated draft is empty")

        # Check for PII placeholders
        required_placeholders = [
            "{{employee_name}}",
            "{{employee_possessive_pronouns}}",
            "{{employee_accusative_pronouns}}",
        ]

        for placeholder in required_placeholders:
            if placeholder not in draft:
                logger.warning(f"Draft may contain PII - missing placeholder: {placeholder}")


# ============================================================================
# Backward Compatibility Wrapper
# ============================================================================


def create_draft_backward_compatible(state: GraphState) -> Dict[str, Any]:
    """Backward compatible version that creates dependencies internally.

    NOT RECOMMENDED for production - use factory pattern instead.
    Only use this during migration.
    """
    from demo.graph.model import llm

    # Create loader on demand
    loader = PromptLoader(prompts_dir=Path("src/prompts"))

    # Create and call node
    node = create_draft_node(llm, loader)
    return node(state)


# ============================================================================
# Usage Examples
# ============================================================================

if __name__ == "__main__":
    # Example 1: Using factory pattern
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    loader = PromptLoader(prompts_dir=Path("src/prompts"))

    draft_node = create_draft_node(llm, loader)

    # Example 2: Using class pattern
    creator = DraftCreator(llm=llm, prompt_loader=loader, max_retries=3, timeout=30.0)

    # Both can be used in graph
    print("Draft node created successfully!")
