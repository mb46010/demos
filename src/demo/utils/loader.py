import json
from pathlib import Path
from typing import Any, Dict


def load_json(path: Path) -> Dict[str, Any]:
    """Load a JSON file."""
    with open(path, "r") as f:
        return json.load(f)


def load_prompts(prompts_dir: Path = Path("src/prompts"), field_name: str = "prompt") -> Dict[str, str]:
    """Load prompts from JSON files in the specified directory."""
    prompts = {}
    if not prompts_dir.exists():
        return prompts

    for file_path in prompts_dir.glob("*.json"):
        data = load_json(file_path)
        if field_name in data:
            prompts[file_path.stem] = data[field_name]
    return prompts


def load_prompt(prompt_path: Path, field_name: str = "prompt") -> str:
    """Load prompts from JSON files in the specified directory."""
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    data = load_json(prompt_path)
    if field_name in data:
        return data[field_name]
    raise ValueError(f"Prompt field not found: {field_name}")


def load_data(
    input_path: Path = Path("data/input.json"),
    structure_path: Path = Path("docs/templates/review_format.json"),
    qualifiers_path: Path = Path("docs/templates/qualifiers.json"),
) -> Dict[str, Any]:
    """Load all required data files."""
    input_path = Path(input_path)
    structure_path = Path(structure_path)
    qualifiers_path = Path(qualifiers_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if not structure_path.exists():
        raise FileNotFoundError(f"Structure file not found: {structure_path}")
    if not qualifiers_path.exists():
        raise FileNotFoundError(f"Qualifiers file not found: {qualifiers_path}")

    return {
        "input": load_json(input_path),
        "structure": load_json(structure_path),
        "qualifiers": load_json(qualifiers_path),
    }


def get_manager_id(input_data: Dict[str, Any]) -> str:
    """Extract manager_id from input data."""
    # Assuming the structure based on typical input.json, but making it robust
    # Adjust this based on actual input.json structure if needed
    return input_data.get("manager_id", (input_data.get("manager") or {}).get("id", ""))


def load_fact_checker(fact_checker_path: Path = Path("data/input_fact_checker.json")) -> Dict[str, Any]:
    """Load fact checker from JSON file."""
    if not fact_checker_path.exists():
        raise FileNotFoundError(f"Fact checker file not found: {fact_checker_path}")
    full_data = load_json(fact_checker_path)

    return full_data
    # input_data = full_data.get("input")
    # draft_data = full_data.get("draft")

    # if input_data is None:
    #     raise ValueError(f"Missing required 'input' field in {fact_checker_path}")
    # if draft_data is None:
    #     raise ValueError(f"Missing required 'draft' field in {fact_checker_path}")

    # return {
    #     "input": input_data,
    #     "draft": draft_data,
    # }


def load_fact_checker_output(fact_checker_path: Path = Path("data/input_fact_checker.json")) -> Dict[str, Any]:
    """Load fact checker from JSON file."""
    if not fact_checker_path.exists():
        raise FileNotFoundError(f"Fact checker file not found: {fact_checker_path}")
    full_data = load_json(fact_checker_path)
    return full_data
