from typing import Union, Optional, Dict, Any
from auth_app.models import UserEntity
from core.base import BaseRepository


class UserRepository(BaseRepository[UserEntity]):
    """
    Usage:
    >> UserRepository.create("abc", "def", ...other)  # create user
    >> UserRepository.find()  # get all users
    ...
    """
    model = UserEntity

    @staticmethod
    def create_user(data: Dict[str, Any]) -> UserEntity:
        """
        :param data: Dict[str, Any]
        :return: UserEntity
        """
        return UserRepository.model.objects.create_user(**data)

    @staticmethod
    def find_one_by_email(email: str) -> Optional[UserEntity]:
        """
        Search for the first user by email.

        :param email: str - The email address of the user to search for.
        :return: Optional[UserEntity] - The first UserEntity
                instance with the given email, or None if not found.
        """
        return UserRepository.find_one_by_q(email=email)  # Returns Optional[UserEntity]

    @staticmethod
    def update_password(user: UserEntity, password: str) -> UserEntity:
        """
        Update the password of a user.

        :param user: UserEntity - The user entity whose password will be updated.
        :param password: str - The new password to set.
        :return: UserEntity - The updated user entity.
        """
        user.set_password(password)
        user.save()
        return user
