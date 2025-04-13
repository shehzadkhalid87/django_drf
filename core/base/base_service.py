from typing import TypeVar, Generic, Type, List, Optional
from core.base.base_repository import BaseRepository
from django.db.models import Model

# Use the same TypeVar for the service
T = TypeVar('T', bound=Model)


class BaseService(Generic[T]):
    """
    A base service class that provides common operations for Django models.

    The service delegates calls to the repository layer for CRUD operations.
    This class is intended to be subclassed by specific services
    that define a particular repository and model type.
    """

    repository: Type[BaseRepository[T]] = None  # Reference to the repository

    @classmethod
    def find(cls, **kwargs) -> List[T]:
        """
        Retrieves all instances of the model from the repository.

        :return: A list of all instances of the model.
        """
        return cls.repository.find(**kwargs)

    @classmethod
    def find_one_by_id(cls, entity_id: int) -> Optional[T]:
        """
        Retrieves a single instance of the model by its ID from the repository.

        :param entity_id: The primary key (ID) of the model instance.
        :return: An instance of the model, or None if not found.
        """
        return cls.repository.find_one_by_id(entity_id)

    @classmethod
    def find_one_by_q(cls, **kwargs) -> Optional[T]:
        """
        Retrieves a single instance of the model by querying with
        specified conditions from the repository.

        :param kwargs: Query parameters to filter the model instances.
        :return: A single instance of the model that matches the query, or None if not found.
        """
        return cls.repository.find_one_by_q(**kwargs)

    @classmethod
    def create(cls, **kwargs) -> T:
        """
        Creates a new instance of the model via the repository.

        :param kwargs: Fields and their values for creating the new instance.
        :return: The newly created instance of the model.
        """
        return cls.repository.create(**kwargs)

    @classmethod
    def update(cls, entity_id: int, **kwargs) -> Optional[T]:
        """
        Updates an existing instance of the model by its ID via the repository.

        :param entity_id: The primary key (ID) of the model instance to update.
        :param kwargs: Fields and their new values to update in the instance.
        :return: The updated instance, or None if the instance was not found.
        """
        return cls.repository.update(entity_id, **kwargs)

    @classmethod
    def delete(cls, entity_id: int) -> bool:
        """
        Deletes an instance of the model by its ID via the repository.

        :param entity_id: The primary key (ID) of the model instance to delete.
        :return: True if the instance was found and deleted, False otherwise.
        """
        return cls.repository.delete(entity_id)
