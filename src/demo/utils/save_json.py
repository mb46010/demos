import json
from pathlib import Path
from typing import Any
from langchain_core.messages import BaseMessage

def default_serializer(obj: Any) -> Any:
    """JSON serializer for objects not serializable by default json code."""
    if isinstance(obj, BaseMessage):
        return obj.model_dump()
    if hasattr(obj, "dict"):
        return obj.dict()
    if hasattr(obj, "json"):
        return obj.json()
    return str(obj)

def save_json(data: Any, file_path: Path | str) -> None:
    """Save data to a JSON file."""
    if isinstance(file_path, str):
        file_path = Path(file_path)
    
    # Ensure directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4, default=default_serializer)
    
    print(f"Data saved to {file_path}")
