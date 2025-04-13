from functools import wraps

from rest_framework import status

from auth_app.services.user import UserService
from core.common.erro_message_type import APPErrorTypes
from core.exceptions.base import ApiError


def get_user_from_request(func):
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        # Assuming the user has been attached to the request by jwt_required
        user_payload = getattr(request, 'user_payload', None)
        if user_payload is None:
            raise ApiError(
                errors="User is not authenticated.",
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="login required",
                error_type=APPErrorTypes.UNAUTHORIZED_ACCESS.value
            )

        # Retrieve the user from UserEntity using the user's id or any relevant identifier
        user_entity = UserService.find_one_by_id(user_payload.get("user_id"))
        if user_entity is None:
            raise ApiError(
                errors="User is not authenticated.",
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="login required",
                error_type=APPErrorTypes.UNAUTHORIZED_ACCESS.value
            )
        if user_entity.is_blocked:
            raise ApiError(
                errors="sorry your account has been blocked, please contact admin!",
                status_code=status.HTTP_403_FORBIDDEN,
                message="account blocked",
                error_type=APPErrorTypes.USER_BLOCKED.value
            )
        if user_entity.is_de_activated:
            raise ApiError(
                errors="sorry your account has been deactivated, please contact admin!",
                status_code=status.HTTP_403_FORBIDDEN,
                message="account deactivated",
                error_type=APPErrorTypes.USER_DEACTIVATED.value
            )
        # Attach the user entity to the request for access in the view
        request.user = user_entity
        # Proceed with the original view logic
        return func(self, request, *args, **kwargs)

    return wrapper
