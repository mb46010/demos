import json
from pathlib import Path
from typing import List, Optional

from langchain_core.messages import HumanMessage
from demo.graph.state import GraphState
from demo.utils.loader import load_prompt
from demo.graph.model import llm
from demo.tools.validation import validate_input

from pydantic import BaseModel, Field
from pprint import pprint


class CheckResult(BaseModel):
    valid: bool = Field(..., description="Whether the input is valid")
    errors: List[str] = Field(default_factory=list, description="List of validation errors")
    message_to_manager: Optional[str] = Field(None, description="Message to be sent back to the manager")


# Node for InputCheck (N1)
def input_check(state: GraphState):
    # Load prompt and join if it's a list
    prompt_raw = load_prompt(Path("src/prompts/n_input.json"))
    if isinstance(prompt_raw, list):
        prompt_template = "\n".join(prompt_raw)
    else:
        prompt_template = prompt_raw

    # Validate input
    validation_result = validate_input(state["input"], state["qualifiers"])

    print()
    print("Validation Result:")
    pprint(validation_result)
    # Fill the prompt
    filled_prompt = prompt_template.format(
        manager_input=json.dumps(state["input"], indent=2),
        validation_tool_output=json.dumps(validation_result, indent=2),
    )

    # Invoke LLM with structured output
    response = llm.with_structured_output(CheckResult).invoke([HumanMessage(content=filled_prompt)])

    # Update state
    state["check_result"] = response.model_dump()

    return state
