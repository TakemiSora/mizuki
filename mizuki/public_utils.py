import uuid


def generate_custom_id() -> str:
    """Generates a custom ID for use in a component."""
    return uuid.uuid4().hex
