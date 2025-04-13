from typing import TypeVar, Generic, Type, List, Optional
from django.db.models import Model

# Define a TypeVar for the entity
T = TypeVar('T', bound=Model)

class BaseRepository(Generic[T]):
    """
    A base repository class that provides common CRUD operations for Django models.

    This class is intended to be subclassed by specific repositories
    that define a particular model type.
    """

    model: Type[T] = None  # The model type

    @classmethod
    def find(cls, **kwargs) -> List[T]:
        """
        Retrieves all instances of the model.

        :return: A list of all instances of the model.
        """
        if kwargs:  # If there are any keyword arguments
            return cls.model.objects.filter(**kwargs)  # Apply the filters
        return cls.model.objects.all()

    @classmethod
    def find_one_by_id(cls, entity_id: int) -> Optional[T]:
        """
        Retrieves a single instance of the model by its ID.

        :param entity_id: The primary key (ID) of the model instance.
        :return: An instance of the model, or None if not found.
        """
        return cls.find_one_by_q(id=entity_id)

    @classmethod
    def find_one_by_q(cls, **kwargs) -> Optional[T]:
        """
        Retrieves a single instance of the model by querying with specified conditions.

        :param kwargs: Query parameters to filter the model instances.
        :return: A single instance of the model that matches the query, or None if not found.
        """
        return cls.model.objects.filter(**kwargs).first()  # Returns Optional[T]

    @classmethod
    def create(cls, **kwargs) -> T:
        """
        Creates and saves a new instance of the model with the provided data.

        :param kwargs: Fields and their values for creating the new instance.
        :return: The newly created instance of the model.
        """
        entity = cls.model.objects.create(**kwargs)
        return entity

    @classmethod
    def update(cls, entity_id: int, **kwargs) -> Optional[T]:
        """
        Updates an existing instance of the model by its ID with the provided data.

        :param entity_id: The primary key (ID) of the model instance to update.
        :param kwargs: Fields and their new values to update in the instance.
        :return: The updated instance, or None if the instance was not found.
        """
        entity = cls.find_one_by_id(entity_id)
        if entity:
            for attr, value in kwargs.items():
                setattr(entity, attr, value)
            entity.save()
        return entity

    @classmethod
    def delete(cls, entity_id: int) -> bool:
        """
        Deletes an instance of the model by its ID.

        :param entity_id: The primary key (ID) of the model instance to delete.
        :return: True if the instance was found and deleted, False otherwise.
        """
        entity = cls.find_one_by_id(entity_id)
        if entity:
            entity.delete()
            return True
        return False
