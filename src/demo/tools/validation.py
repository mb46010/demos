from typing import List, Dict, Any, Union

def validate_input(input_data: Dict[str, Any], qualifiers_data: Dict[str, Any]) -> Dict[str, Union[bool, List[str]]]:
    """
    Validate the input data against the requirements.
    
    Args:
        input_data: The input JSON data containing manager_id, employee, rating, manager_bullets.
        qualifiers_data: The qualifiers JSON data containing allowed ratings.
        
    Returns:
        A dictionary with 'valid' (bool) and 'errors' (list of strings).
    """
    errors = []
    
    # Check top-level fields are not empty
    required_fields = ["manager_id", "employee", "rating", "manager_bullets"]
    for field in required_fields:
        if not input_data.get(field):
            errors.append(f"Field '{field}' is missing or empty.")
            
    # Check manager_bullets list
    bullets = input_data.get("manager_bullets", [])
    if not isinstance(bullets, list):
        errors.append("Field 'manager_bullets' must be a list.")
    elif len(bullets) < 3:
        errors.append(f"Field 'manager_bullets' must have at least 3 items. Found {len(bullets)}.")
        
    # Get allowed ratings from qualifiers schema
    # Structure of qualifiers.json: {"schema": {"properties": {"performance_rating": {"enum": [...]}}}}
    try:
        allowed_ratings = qualifiers_data.get("schema", {}).get("properties", {}).get("performance_rating", {}).get("enum", [])
        if not allowed_ratings:
             # Fallback if structure is different or empty, though instruction says it's there
             # Based on previous file view, it is under schema.properties.performance_rating.enum
             pass
    except AttributeError:
        allowed_ratings = []
        errors.append("Invalid qualifiers schema structure.")

    # Check bullet items
    if isinstance(bullets, list):
        for i, item in enumerate(bullets):
            if not isinstance(item, dict):
                errors.append(f"Bullet item {i} is not a dictionary.")
                continue
                
            if not item.get("text"):
                errors.append(f"Bullet item {i} missing 'text'.")
            
            rating = item.get("rating")
            if not rating:
                errors.append(f"Bullet item {i} missing 'rating'.")
            elif rating not in allowed_ratings:
                errors.append(f"Bullet item {i} has invalid rating '{rating}'. Allowed: {allowed_ratings}")

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }
