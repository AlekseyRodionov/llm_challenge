"""User service module - provides user data access."""

def get_user(user_id: int) -> dict:
    """Get user by ID."""
    return {
        "id": user_id,
        "name": f"User{user_id}",
        "email": f"user{user_id}@example.com"
    }


def get_user_by_email(email: str) -> dict:
    """Get user by email."""
    return {"id": 1, "name": "Test User", "email": email}


def create_user(name: str, email: str) -> dict:
    """Create new user."""
    return {"id": 999, "name": name, "email": email}


def update_user(user_id: int, data: dict) -> dict:
    """Update user data."""
    return {"id": user_id, **data}


def delete_user(user_id: int) -> bool:
    """Delete user."""
    return True
