from typing import Any, Dict, List, Union


def validate_input(
    input_data: Dict[str, Any],
    qualifiers_data: Dict[str, Any],
    min_bullets: int = 3,
    min_ratings: int = 2,
    min_text_length: int = 10,
) -> Dict[str, Union[bool, List[str]]]:
    """Validate the input data against the requirements.
    - the fields `manager_id`, employee, manager_bullets are not empty.
    - manager_bullets must have at list len>=3
    - the elements of manager_bullets must have the fields `text (mandatory) and `rating` (optional)
    - rating must be in the Enum field of docs/templates/qualifiers.json.

    Args:
        input_data: The input JSON data containing manager_id, employee, rating, manager_bullets.
        qualifiers_data: The qualifiers JSON data containing allowed ratings.

    Returns:
        A dictionary with 'valid' (bool) and 'errors' (list of strings).
    """
    errors = []

    # Check top-level fields are not empty
    required_fields = ["manager_id", "employee", "manager_bullets"]
    for field in required_fields:
        if not input_data.get(field):
            errors.append(f"Field '{field}' is missing or empty.")

    # Check manager_bullets list
    bullets = input_data.get("manager_bullets", [])
    if not isinstance(bullets, list):
        errors.append("Field 'manager_bullets' must be a list.")
    elif len(bullets) < min_bullets:
        errors.append(f"Field 'manager_bullets' must have at least {min_bullets} items. Found {len(bullets)}.")

    # Get allowed ratings from qualifiers schema
    # Structure of qualifiers.json: {"schema": {"properties": {"performance_rating": {"enum": [...]}}}}
    try:
        allowed_ratings = (
            qualifiers_data.get("schema", {}).get("properties", {}).get("performance_rating", {}).get("enum", [])
        )
        if not allowed_ratings:
            # Fallback if structure is different or empty, though instruction says it's there
            # Based on previous file view, it is under schema.properties.performance_rating.enum
            pass
    except AttributeError:
        allowed_ratings = []
        errors.append("Invalid qualifiers schema structure.")

    # Check bullet items
    rated_bullets_count = 0
    if isinstance(bullets, list):
        for i, item in enumerate(bullets):
            if not isinstance(item, dict):
                errors.append(f"Bullet item {i} is not a dictionary.")
                continue

            if not item.get("text"):
                errors.append(f"Bullet item {i} missing 'text'.")
            text = item.get("text")
            if len(text) < min_text_length:
                errors.append(f"Bullet item {i} 'text' is too short.")

            rating = item.get("rating")
            if rating:
                rated_bullets_count += 1
                if rating not in allowed_ratings:
                    errors.append(f"Bullet item {i} has invalid rating '{rating}'. Allowed: {allowed_ratings}")

    if rated_bullets_count < min_ratings:
        errors.append(f"At least {min_ratings} bullets must have a rating. Found {rated_bullets_count}.")

    return {"valid": len(errors) == 0, "errors": errors}
