from functools import wraps

import jwt
from django.conf import settings
from rest_framework import status

from core.common.erro_message_type import APPErrorTypes
from core.exceptions.base import ApiError


def login_required(func):
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        # Get the Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            raise ApiError(
                errors="Authentication credentials were not provided.",
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="login required",
                error_type=APPErrorTypes.UNAUTHORIZED_ACCESS.value
            )

        try:
            # Extract the token and validate the format
            auth_type, token = auth_header.split()
            if auth_type.lower() != 'bearer':
                raise ApiError(
                    errors=[{"message": "Invalid token type."}],
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    message="login required",
                    type=APPErrorTypes.UNAUTHORIZED_ACCESS.value
                )
        except ValueError as error:
            raise ApiError(
                errors="Invalid Authorization header format.",
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="login required",
                error_type=APPErrorTypes.UNAUTHORIZED_ACCESS.value
            ) from error

        try:
            # Decode the JWT token without database lookup
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            # Attach the payload (user info) to the request
            request.user_payload = payload  # Instead of request.user

        except jwt.ExpiredSignatureError as error:
            raise ApiError(
                errors="Token has expired.",
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="login required",
                error_type=APPErrorTypes.UNAUTHORIZED_ACCESS.value
            ) from error
        except jwt.InvalidTokenError as error:
            raise ApiError(
                errors="Invalid token.",
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="login required",
                error_type=APPErrorTypes.UNAUTHORIZED_ACCESS.value
            ) from error
        # Proceed to the view with JWT payload attached to the request
        return func(self, request, *args, **kwargs)

    return wrapper
