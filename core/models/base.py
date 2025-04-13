from django.db import models


class BaseModel(models.Model):
    """
    An abstract base model class that provides a method to convert
    model field values into a dictionary representation.

    Attributes:
        No additional attributes are added; this class serves as a base class.

    Methods:
        to_dict() -> dict:
            Returns a dictionary with model field names as keys and
            their corresponding values as values.
    """

    class Meta:
        abstract = True

    objects = models.Manager()

    def to_dict(self):
        """
        Converts the model instance's fields into a dictionary.

        Returns:
            dict: A dictionary where keys are the model's field names
                  and values are the corresponding field values.
        """
        return {field.name: getattr(self, field.name) for field in self._meta.get_fields()}
