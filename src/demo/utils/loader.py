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

def load_data(
    input_path: Path = Path("data/input.json"),
    structure_path: Path = Path("docs/templates/review_format.json"),
    qualifiers_path: Path = Path("docs/templates/qualifiers.json")
) -> Dict[str, Any]:
    """Load all required data files."""
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
