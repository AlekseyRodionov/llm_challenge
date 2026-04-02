"""Utility functions module."""


def format_response(data, status='success'):
    """Format API response."""
    return {
        "status": status,
        "data": data
    }


def validate_email(email: str) -> bool:
    """Validate email format."""
    return "@" in email and "." in email


def sanitize_input(text: str) -> str:
    """Sanitize user input."""
    return text.strip()


def helper():
    """Helper function."""
    return "Helper executed"


def process_data(data):
    """Process data."""
    return [item for item in data if item]


def format_date(date):
    """Format date."""
    return str(date)
