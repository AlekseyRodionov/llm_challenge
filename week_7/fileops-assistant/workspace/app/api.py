"""API handlers module."""
from service import get_user, create_user


def handle_get_user(request):
    """Handle get user request."""
    user_id = request.get('user_id')
    return get_user(user_id)


def handle_create_user(request):
    """Handle create user request."""
    name = request.get('name')
    email = request.get('email')
    return create_user(name, email)


def process_request(request_type, data):
    """Main request processor."""
    if request_type == 'get':
        return handle_get_user(data)
    elif request_type == 'create':
        return handle_create_user(data)
    else:
        return {"error": "Unknown request type"}


def handler():
    """Example handler."""
    return get_user(1)
