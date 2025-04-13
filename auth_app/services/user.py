from typing import Dict, Any

import pandas as pd
from django.contrib.auth import authenticate
from django.db import transaction
from django.utils.datetime_safe import datetime
from rest_framework import status
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from auth_app.models.user import UserEntity
from auth_app.repositories.user import UserRepository
from auth_app.serializers import SignupSerializer
from auth_app.serializers.auth import UserSerializer
from auth_app.utils import AuthUtils
from core.base import BaseService
from core.common.erro_message_type import APPErrorTypes
from core.enums.enums import ACCOUNT_STATUS, USER_UPDATE_ACTIONS, ROLES
from core.exceptions.base import ApiError
from core.types import LoginResult, RefreshTokenResult
from core.utils.helper import generate_password, decode_uid
from core.utils.import_user_preprocess import preprocess_csv
from core.utils.verification_email_token_generator import email_verification_token


class UserService(BaseService[UserEntity]):
    """
    Service class to handle user business logic.
    >> (signup_user, login_user, verify_email, ...)
    """
    repository = UserRepository

    @staticmethod
    def signup_user(data) -> UserEntity:
        """
           Registers a new user.

           This method checks if a user with the provided email already exists. If so,
           it raises an error; otherwise, it creates a new user.

           :param data: A dictionary containing the user's information, including:
               - "email": The user's email (str).

           :return: UserEntity: The newly created user entity.

           :raises ApiError: If the user already exists.

           Errors:
               - 400: User already exists if the email is already registered.
        """
        if UserService.repository.find_one_by_q(email=data['email']) is not None:
            raise ApiError(
                errors="User already exists",
                status_code=status.HTTP_400_BAD_REQUEST,
                message="User already exists",
                error_type=APPErrorTypes.DUPLICATION_ERROR.value,
            )
        return UserService.repository.create_user(data)

    @staticmethod
    def login_user(data) -> LoginResult:
        """
            Authenticates a user and logs them in.

            This method checks the provided email and password, verifies the account's
            status (verified, not blocked, and not deactivated), and updates the last
            login time. It returns a login result containing access and refresh tokens.

            :param data: A dictionary containing:
                - "email": The user's email (str).
                - "password": The user's password (str).

            :return: LoginResult: An object with refresh and access tokens, along with user data.

            :raises ApiError: If the credentials are invalid or the account status is problematic.

            Errors:
                - 400: Invalid credentials if authentication fails.
                - 404: Resource not found if the user account is not found.
        """
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            if user is None:
                raise ApiError(
                    errors="invalid credentials",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="credentials error",
                    error_type=APPErrorTypes.CREDENTIALS_ERROR.value
                )
        UserService.check_account_verified(user)
        UserService.check_account_blocked(user)
        UserService.check_account_deactivated(user)

        # update last login value
        UserService.repository.update(user.pk, **{"last_login": datetime.now()})

        refresh_token = RefreshToken.for_user(user)
        return LoginResult(
            str(refresh_token),
            str(refresh_token.access_token),
            UserSerializer(instance=user).data,
        )

    @staticmethod
    def update_user(user_id: int, data: Dict[str, Any]) -> UserEntity:
        """
           Updates the user's information.

           This method retrieves the user by ID and updates their details with the provided data.
           Raises an error if the user is not found.

           :param user_id: The ID of the user to update (int).
           :param data: A dictionary containing the user's updated information.

           :return: UserEntity: The updated user entity.

           :raises ApiError: If the user is not found.

           Errors:
               - 404: Resource not found if the user ID does not exist.
        """
        user = UserService.find_one_by_id(user_id)
        if user is None:
            raise ApiError(
                errors="Resource not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                message="resource not found",
                error_type=APPErrorTypes.RESOURCE_NOT_FOUND.value
            )

        return UserService.repository.update(user_id, **data)

    @staticmethod
    def change_password(user: UserEntity, data: Dict[str, Any]) -> UserEntity:
        """
        Changes the user's password after validating the old password.

        This method checks if the new password is different from the old password and
        verifies that the provided old password matches the user's current password.
        If both conditions are met, it updates the user's password.

        :param user: UserEntity: The user whose password is being changed.
        :param data: A dictionary containing:
            - "old_password": The user's current password (str).
            - "password": The new password to set (str).

        :return: UserEntity: The updated user entity after changing the password.

        :raises ApiError: If the new password is the same as the old password or
                          if the old password is incorrect.

        Errors:
            - 400: Bad Request if the new password is the same as the old password
                   or if the old password is incorrect.
        """
        old_password = data.get("old_password")
        new_password = data.get("password")
        # Check if the new password is different from the old password
        if old_password == new_password:
            raise ApiError(
                errors="New password cannot be the same as the old password.",
                status_code=status.HTTP_400_BAD_REQUEST,
                message="New password cannot be the same as the old password",
                error_type=APPErrorTypes.BAD_REQUEST.value
            )

        # Check if the old password matches the user's current password
        if not user.check_password(old_password):
            raise ApiError(
                errors="Old password is incorrect.",
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Old password is incorrect",
                error_type=APPErrorTypes.INVALID_CREDENTIALS.value
            )

        return UserService.repository.update_password(user, password=new_password)

    @staticmethod
    def check_account_blocked(user: UserEntity) -> bool:
        """
        Check if user account is block then throw error, else return False
        :param: user: UserEntity
        :return: bool
        """
        if user.is_blocked:
            raise ApiError(
                errors="sorry your account has been blocked, please contact admin!",
                status_code=status.HTTP_403_FORBIDDEN,
                message="account blocked",
                error_type=APPErrorTypes.USER_BLOCKED.value
            )
        return False

    @staticmethod
    def check_account_deactivated(user: UserEntity) -> bool:
        """
        Check if user is deactivated then throw error, else return False
        :param: user: UserEntity
        :return: bool
        """
        if user.is_de_activated:
            raise ApiError(
                errors="sorry your account has been deactivated, please contact admin!",
                status_code=status.HTTP_403_FORBIDDEN,
                message="account deactivated",
                error_type=APPErrorTypes.USER_DEACTIVATED.value
            )
        return False

    @staticmethod
    def check_account_verified(user: UserEntity) -> bool:
        """
        Check if user email is verified then return True, else throw error
        :param: user: UserEntity
        :return: bool
        :raises: ApiError Forbidden
        """
        if not user.google_email_verification:
            raise ApiError(
                errors="your account is not verified, please check your mail inbox to activate your account",
                status_code=status.HTTP_403_FORBIDDEN,
                message="account not verified",
                error_type=APPErrorTypes.ACCOUNT_NOT_VERIFIED.value
            )
        return True

    @staticmethod
    def verify_email(data: Dict[str, Any]) -> LoginResult:
        """
        Verifies the user's email by checking the provided token and UID.

        This method decodes the UID, retrieves the user from the repository,
        and checks if the email verification token is valid. If the verification
        is successful, the user's email is marked as verified, the token is marked
        as used, and a welcome email is sent.

        :param data: A dictionary containing:
            - "uid": The unique identifier of the user (str).
            - "token": The email verification token (str).

        :return: bool: Returns True if the email is successfully verified.

        :raises ApiError: If the user is not found, the token is invalid,
                          or the token has already been used.

        Error:
            - 400: Invalid link if the user does not exist or the token is invalid.
        """

        uid = decode_uid(data.get("uid", ""))
        user = UserService.find_one_by_id(entity_id=uid)

        if user is None or user.email_token_used \
                or not email_verification_token.check_token(user, data.get("token")):
            raise ApiError(
                errors="invalid link",
                status_code=status.HTTP_400_BAD_REQUEST,
                message="invalid link",
                error_type=APPErrorTypes.EMAIL_LINK_INVALID.value
            )

        UserService.update(user.pk, **{"google_email_verification": True, "email_token_used": True})

        refresh_token = RefreshToken.for_user(user)

        return LoginResult(
            str(refresh_token),
            str(refresh_token.access_token),
            UserSerializer(instance=user).data
        )

    @staticmethod
    def refresh_token(data: Dict[str, Any]) -> RefreshTokenResult:
        """
        Refreshes the user's access token using the provided refresh token.

        This method validates the refresh token, retrieves the associated user,
        and generates a new access token. If the refresh token is expired or invalid,
        it raises an error.

        :param data: A dictionary containing:
            - "refresh": The refresh token (str).

        :return: RefreshTokenResult: An object containing the new access
            token and the original refresh token.

        :raises ApiError: If the refresh token is expired or the user is not found.

        :Error:
            - 401: Refresh token expired if the token is invalid or expired.
        """

        try:
            refresh = RefreshToken(data.get("refresh"))
            user_id = refresh['user_id']
            user = UserRepository.find_one_by_id(user_id)
            if user is None:
                raise ApiError(
                    errors="Refresh token has expired. Please login again",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    message="refresh token expired",
                    error_type=APPErrorTypes.TOKEN_REFRESH_FAILED.value
                )
            access = AccessToken.for_user(user)
            # Return the standardized response if successful
            return RefreshTokenResult(
                str(refresh),
                str(access),
            )
        except TokenError as error:
            raise ApiError(
                errors="refresh token has expired. Please login again",
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="refresh token expired",
                error_type=APPErrorTypes.TOKEN_REFRESH_FAILED.value
            ) from error

    @staticmethod
    def complete_candidate_account(data: Dict[str, Any]) -> LoginResult:
        """
        Completes the candidate's account setup by verifying the
        email token and saving user data.

        This method checks the validity of the provided UID and email verification token.
        If valid, it updates the user’s account status, sets the password, and sends
        a welcome email. It raises an error if the link is
        invalid or the token has already been used.

        :param data: A dictionary containing:
            - "uid": The unique identifier of the user (str).
            - "token": The email verification token (str).
            - "password": The user's password (str).

        :return: LoginResult: An object containing the refresh
                token, access token, and user data.

        :raises ApiError: If the user is not found, the email token is used,
                or the token is invalid.

        Error:
            - 400: Invalid link if the user does not exist or the token is invalid.
        """
        uid = decode_uid(data.get("uid"), "")
        user = UserService.repository.find_one_by_id(entity_id=int(uid))

        if user is None or user.email_token_used \
                or not email_verification_token.check_token(user, data.get("token")):
            # If no user is found, raise an error indicating the invalid link
            raise ApiError(
                errors="invalid link",
                status_code=status.HTTP_400_BAD_REQUEST,
                message="invalid link",
                error_type=APPErrorTypes.EMAIL_LINK_INVALID.value
            )

        UserService.repository.update(user.pk, **{
            "google_email_verification": True,
            "status": ACCOUNT_STATUS.COMPLETE.value[0],
            "email_token_used": True,
            "last_login": datetime.now()
        })
        user.set_password(data.get("password"))
        user.save()

        AuthUtils.send_welcome_email(user.email)

        refresh_token = RefreshToken.for_user(user)

        return LoginResult(
            str(refresh_token),
            str(refresh_token.access_token),
            UserSerializer(instance=user).data
        )

    @staticmethod
    def update_user_action_fields(data: Dict[str, Any]) -> UserEntity:
        """
        Updates a user's status based on the specified action.

        This method looks up a user by `user_id` and performs actions like blocking,
        unblocking, activating, or deactivating. It raises an error if the user is
        not found or if an invalid action is provided.

        :param:
            data (Dict[str, Any]): Contains "user_id" (str) and "action" (str).

        :return:
            UserEntity: The updated user entity after the action.

        :raise:
            ApiError: If the user is not found or the action is invalid.

        Error
            - 404: Resource Not Found if the user does not exist.
            - 400: Bad Request for an invalid action.
        """
        user_id = data.get("user_id")
        action = data.get("action")

        user = UserService.find_one_by_id(entity_id=user_id)
        if user is None:
            raise ApiError(
                errors="Resource not found",
                status_code=status.HTTP_404_NOT_FOUND,
                message="resource not found",
                error_type=APPErrorTypes.RESOURCE_NOT_FOUND.value
            )
        print(action)
        if action.value == USER_UPDATE_ACTIONS.BLOCK.value:
            return UserService.__block_user__(user)

        if action.value == USER_UPDATE_ACTIONS.UNBLOCK.value:
            return UserService.__unblock_user__(user)
        if action.value == USER_UPDATE_ACTIONS.ACTIVATE.value:
            return UserService.__activate_user__(user)

        if action.value == USER_UPDATE_ACTIONS.DEACTIVATE.value:
            return UserService.__deactivate_user__(user)

        return ApiError(
            errors="Invalid action",
            status_code=status.HTTP_400_BAD_REQUEST,
            message="invalid action",
            error_type=APPErrorTypes.BAD_REQUEST
        )

    @staticmethod
    def __block_user__(user: UserEntity) -> bool:
        """
        Blocks a user by setting the 'is_blocked' field to True.
        :param user: The user instance to be is_blocked.
        :return: Response with success message.
        :raise: APIError Bad Request
        """
        print("blocked ", user.is_blocked)
        if user.is_blocked:
            raise ApiError(
                errors="User is already blocked",
                status_code=status.HTTP_400_BAD_REQUEST,
                message="user is already blocked",
                error_type=APPErrorTypes.USER_BLOCKED.value
            )

        UserService.update(user.pk, **{"is_blocked": True})
        return user

    @staticmethod
    def __unblock_user__(user: UserEntity) -> UserEntity:
        """
        Unblocks a user by setting the 'is_blocked' field to False.
        :param user: The user instance to be unblocked.
        :return: Response with success message.
        :raise: APIError Bad Request
        """
        if not user.is_blocked:
            raise ApiError(
                errors="User is already unblocked",
                status_code=status.HTTP_400_BAD_REQUEST,
                message="user is already un-blocked",
                error_type=APPErrorTypes.USER_UN_BLOCKED.value
            )

        UserService.update(user.pk, **{"is_blocked": False})
        return user

    @staticmethod
    def __deactivate_user__(user: UserEntity) -> UserEntity:
        """
        De activated a user by setting the 'is_de_activated' field to True.
        :param user: The user instance to be unblocked.
        :return: Response with success message.
        :raise: APIError Bad Request
        """
        if user.is_de_activated:
            raise ApiError(
                errors="User is already deactivated",
                status_code=status.HTTP_400_BAD_REQUEST,
                message="user is already deactivated",
                error_type=APPErrorTypes.USER_DEACTIVATED.value
            )

        UserService.update(user.pk, **{"is_de_activated": True})
        return user

    @staticmethod
    def __activate_user__(user: UserEntity) -> UserEntity:
        """
        Activate a user by setting the 'is_de_activated' field to False.
        :param user: The user instance to be unblocked.
        :return: Response with success message.
        :raise: APIError Bad Request
        """
        if not user.is_de_activated:
            raise ApiError(
                errors="User is already activated",
                status_code=status.HTTP_400_BAD_REQUEST,
                message="user is already deactivated",
                error_type=APPErrorTypes.USER_ACTIVATED.value
            )

        UserService.update(user.pk, **{"is_de_activated": False})
        return user

    @staticmethod
    def delete_user(entity_id: int) -> UserEntity:
        """
        Delete a user by their ID.

        :param entity_id: The ID of the user to be deleted.
        :return: The deleted UserEntity instance.
        :raises ApiError: If the user does not exist or if the deletion is forbidden.
        """
        user = UserService.find_one_by_id(entity_id=entity_id)
        if user is None:
            raise ApiError(
                errors="forbidden resource",
                status_code=status.HTTP_403_FORBIDDEN,
                message="forbidden resource",
                error_type=APPErrorTypes.FORBIDDEN_RESOURCE_ACCESS.value
            )
        user.delete()
        return user

    @staticmethod
    def import_user(data: Dict[str, Any], user: UserEntity) -> bool:
        """
        Import users from a CSV file.

        :param data: A dictionary containing the CSV file to import.
        :param user: The user performing the import operation.
        :return: True if the import is successful.
        :raises ApiError: If the file type is invalid or if user validation fails.
        """
        csv_file = data.get("file")

        if not csv_file.name.endswith(".csv"):
            raise ApiError(
                errors="invalid file type.",
                status_code=status.HTTP_400_BAD_REQUEST,
                message="invalid file type",
                error_type=APPErrorTypes.INVALID_FILE_TYPE.value
            )

        _df = pd.read_csv(csv_file)
        process_data = preprocess_csv(_df)
        try:
            with transaction.atomic():
                for user_data in process_data:
                    ser = SignupSerializer(data=user_data)
                    ser.initial_data['role'] = ROLES.CANDIDATE.value[0]  # Set additional fields
                    ser.initial_data['password'] = generate_password()  # Generate a random password
                    ser.initial_data['status'] = ACCOUNT_STATUS.PENDING.value[0]
                    ser.initial_data["is_agreement_accepted"] = True
                    ser.initial_data['company'] = user.pk
                    if not ser.is_valid():
                        raise ApiError(
                            errors=ser.errors,
                            status_code=status.HTTP_400_BAD_REQUEST,
                            message="User validation failed",
                            error_type=APPErrorTypes.VALIDATION_ERROR.value
                        )
                    UserService.repository.create_user(ser.validated_data)
        except ApiError as error:
            raise error from error

    @staticmethod
    def add_user_manual(data: Dict[str, Any]) -> UserEntity:
        """
        Manually add a new user to the system.

        :param data: A dictionary containing the user data to create.
        :return: The created UserEntity instance.
        """
        return UserService.repository.create_user(data)

    @staticmethod
    def get_user(request_user: UserEntity, user_id: int) -> UserEntity:
        """
        Retrieve a user by their ID, with access control checks.

        :param request_user: The user making the request.
        :param user_id: The ID of the user to retrieve.
        :return: The UserEntity instance of the requested user.
        :raises ApiError: If the user does not exist or if access is forbidden.
        """
        user = UserService.find_one_by_id(user_id)

        # Check if the user exists
        if user is None:
            raise ApiError(
                errors="Resource not found",
                status_code=status.HTTP_404_NOT_FOUND,
                message="resource not found",
                error_type=APPErrorTypes.RESOURCE_NOT_FOUND.value
            )

        # Super Admin can access any user
        if request_user.role == ROLES.SUPER_ADMIN.value[0]:
            return UserSerializer(instance=user).data

        # Organizer access checks
        if request_user.role == ROLES.COMPANY.value[0]:
            # Organizer can get their own details
            if request_user.id == user.id:
                return UserSerializer(instance=user).data

            # Organizer can get user details if the user belongs to the same company
            if user.company is not None and request_user.id == user.company.id:
                return UserSerializer(instance=user).data

        # If access conditions are not met, raise Forbidden error
        raise ApiError(
            errors="Forbidden resource",
            status_code=status.HTTP_403_FORBIDDEN,
            message="Forbidden resource",
            error_type=APPErrorTypes.FORBIDDEN_RESOURCE_ACCESS.value
        )

    @staticmethod
    def forgot_password_request(email: str) -> bool:

        user = UserService.find_one_by_q(email=email)
        if user is None:
            raise ApiError(
                errors="Invalid request",
                status_code=status.HTTP_400_BAD_REQUEST,
                message="invalid request",
                error_type=APPErrorTypes.BAD_REQUEST.value
            )
        UserService.check_account_verified(user)

        UserService.update(user.pk, **{"forgot_password_token_used": False})
        AuthUtils.send_forgot_password_email(user)

        return True

    @staticmethod
    def reset_password_request(data: Dict[str, Any]) -> bool:
        uid = decode_uid(data.get("uid", ""))
        user = UserService.find_one_by_id(entity_id=uid)
        print(user)

        if user is None or user.forgot_password_token_used \
                or not email_verification_token.check_token(user, data.get("token")):
            raise ApiError(
                errors="invalid link",
                status_code=status.HTTP_400_BAD_REQUEST,
                message="invalid link",
                error_type=APPErrorTypes.EMAIL_LINK_INVALID.value
            )

        UserService.repository.update_password(user, data.get("password"))
        UserService.update(user.pk, **{"forgot_password_token_used": True})

        return True
