import re
import secrets
import string
from datetime import timedelta
from typing import Any

from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import status, serializers

from core.common.erro_message_type import APPErrorTypes
from core.exceptions.base import ApiError
from .verification_email_token_generator import email_verification_token


def format_timedelta(td: timedelta) -> str:
    if td is None:
        return '00:00:00'
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


def generate_password(length=12):
    """Generate a strong random password.

    Args:
        length (int): Length of the password. Default is 12.

    Returns:
        str: A randomly generated password.
    """
    # Define the character sets to choose from
    characters = (
            string.ascii_uppercase +  # Uppercase letters
            string.ascii_lowercase +  # Lowercase letters
            string.digits +  # Digits
            string.punctuation  # Special characters
    )

    # Generate a password
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password


def validate_password(value: str) -> str:
    """
        Validate the password to ensure it meets specific requirements:
        - At least 8 characters
        - Contains at least one alphabetic character
        - Contains at least one numeric digit
        - Contains at least one special character
        - Does not contain invalid characters
    """
    if len(value) < 8:
        raise serializers.ValidationError("Password must be at least 8 characters long.")

    if not re.search(r'[A-Za-z]', value):
        raise serializers.ValidationError("Password must contain at least one alphabetic character.")

    if not re.search(r'[0-9]', value):
        raise serializers.ValidationError("Password must contain at least one numeric digit.")

    if not re.search(r'[@#$%^&+=]', value):
        raise serializers.ValidationError(
            "Password must contain at least one special character (@, #, $, %, ^, &, +, =).")

    if not re.match(r'^[A-Za-z0-9@#$%^&+=]*$', value):
        raise serializers.ValidationError("Password must contain only allowed characters.")

    return value


def generate_token(instance: Any) -> str:
    return email_verification_token.make_token(instance)


def generate_uid(value: str) -> str:
    return urlsafe_base64_encode(force_bytes(value))


def decode_uid(uid: str) -> bool:
    try:
        return urlsafe_base64_decode(uid).decode()
    except UnicodeDecodeError as error:
        raise ApiError(
            error_type=[{"message": "Invalid token provided"}],
            status_code=status.HTTP_400_BAD_REQUEST,
            message="invalid token",
            errors=APPErrorTypes.BAD_REQUEST.value,
        ) from error
