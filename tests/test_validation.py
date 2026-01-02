import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Add src to python path
# sys.path.append(str(Path(__file__).parent.parent / "src"))
# run with: uv run python tests/test_validation.py

from demo.tools.validate_input import validate_input
from demo.utils.loader import load_data


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

    # Test min_bullets parameter
    print("\nTesting min_bullets parameter...")
    # 2 bullets, min_bullets=3 (default) -> should fail
    input_less_bullets = data["input"].copy()
    input_less_bullets["manager_bullets"] = [
        {"text": "t1", "rating": "Exceeds expectations"},
        {"text": "t2", "rating": "Meets expectations"},
    ]
    res_min_bullets_fail = validate_input(input_less_bullets, data["qualifiers"])
    print(f"Min bullets fail result: {res_min_bullets_fail}")
    assert not res_min_bullets_fail["valid"]

    # 2 bullets, min_bullets=2 -> should pass
    res_min_bullets_pass = validate_input(input_less_bullets, data["qualifiers"], min_bullets=2)
    print(f"Min bullets pass result: {res_min_bullets_pass}")
    assert res_min_bullets_pass["valid"]

    # Test min_ratings parameter
    print("\nTesting min_ratings parameter...")
    # 3 bullets, 1 rated, min_ratings=2 (default) -> should fail
    input_less_ratings = data["input"].copy()
    input_less_ratings["manager_bullets"] = [
        {"text": "t1", "rating": "Exceeds expectations"},
        {"text": "t2"},
        {"text": "t3"},
    ]
    res_min_ratings_fail = validate_input(input_less_ratings, data["qualifiers"])
    print(f"Min ratings fail result: {res_min_ratings_fail}")
    assert not res_min_ratings_fail["valid"]
    assert "At least 2 bullets must have a rating" in str(res_min_ratings_fail["errors"])

    # 3 bullets, 1 rated, min_ratings=1 -> should pass
    res_min_ratings_pass = validate_input(input_less_ratings, data["qualifiers"], min_ratings=1)
    print(f"Min ratings pass result: {res_min_ratings_pass}")
    assert res_min_ratings_pass["valid"]


if __name__ == "__main__":
    test_validation()
