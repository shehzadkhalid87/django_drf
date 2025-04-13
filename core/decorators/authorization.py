from functools import wraps
from typing import List

from rest_framework import status

from auth_app.models import UserEntity
from core.common.erro_message_type import APPErrorTypes
from core.common.permisions import Permissions
from core.decorators.authentication import login_required
from core.decorators.get_user_from_request import get_user_from_request
from core.exceptions.base import ApiError


def authorization(groups: List[str], permissions: List[str]):
    """
    Decorator to authorize users based on groups and permissions.

    Args:
        groups (List[str]): A list of group names to check.
        permissions (List[str]): A list of permission names to check.

    Returns:
        Callable: A decorator that wraps the original function.
    """

    def decorator_func(func):
        @wraps(func)
        @login_required
        @get_user_from_request
        def wrapper(self, request, *args, **kwargs):
            user: UserEntity = request.user
            # check if user has the role passed to route
            if user.role.lower() not in ",".join(groups).lower().split(","):
                raise ApiError(
                    errors="Forbidden resource",
                    status_code=status.HTTP_403_FORBIDDEN,
                    message="forbidden resource",
                    error_type=APPErrorTypes.FORBIDDEN_RESOURCE_ACCESS.value
                )
            # check if user has the permissions passed to route
            if not any(perm in Permissions[user.role] for perm in permissions):
                raise ApiError(
                    errors="Forbidden resource",
                    status_code=status.HTTP_403_FORBIDDEN,
                    message="forbidden resource",
                    error_type=APPErrorTypes.FORBIDDEN_RESOURCE_ACCESS.value
                )
            # If all checks pass, call the original function
            return func(self, request, *args, **kwargs)

        return wrapper

    return decorator_func
