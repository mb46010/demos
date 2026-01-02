import sys
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Add src to python path
# sys.path.append(str(Path(__file__).parent.parent / "src"))

from demo.utils.loader import load_data
from demo.tools.validation import validate_input

def test_validation():
    print("Loading data...")
    data = load_data()
    print(data["input"])
    print()
    
    print("Validating input...")
    result = validate_input(data["input"], data["qualifiers"])
    
    print(f"Validation result: {result}")
    
    if result["valid"]:
        print("Input is valid.")
    else:
        print("Input is invalid. Errors:")
        for error in result["errors"]:
            print(f"- {error}")
            
    # Test with invalid data (mock modification)
    print("\nTesting with invalid data (less than 3 bullets)...")
    invalid_input = data["input"].copy()
    invalid_input["manager_bullets"] = invalid_input["manager_bullets"][:2]
    result_invalid = validate_input(invalid_input, data["qualifiers"])
    print(f"Invalid validation result: {result_invalid}")
    assert not result_invalid["valid"]
    assert "length" in str(result_invalid["errors"]) or "3 items" in str(result_invalid["errors"])

    print("\nTesting with invalid rating...")
    invalid_input_rating = data["input"].copy()
    invalid_input_rating["manager_bullets"] = [
        {"text": "t1", "rating": "Exceeds expectations"},
        {"text": "t2", "rating": "Invalid Rating"},
        {"text": "t3", "rating": "Meets expectations"}
    ]
    result_rating = validate_input(invalid_input_rating, data["qualifiers"])
    print(f"Invalid rating result: {result_rating}")
    assert not result_rating["valid"]

if __name__ == "__main__":
    test_validation()
