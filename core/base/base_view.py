from rest_framework import status
from rest_framework.request import Request
from rest_framework.serializers import Serializer
from rest_framework.views import APIView

from core.common.erro_message_type import APPErrorTypes
from core.exceptions.base import ApiError


class BaseView(APIView):
    """
    Base view to handle common tasks like serializer validation and error handling.
    You can extend this class to add more advanced validation logic.
    """

    serializer_class = None
    additional_serializer_classes = {}

    def get_serializer_class(self) -> Serializer:
        """
        Get the serializer class. Can be overridden for custom logic.
        """
        if self.serializer_class is None:
            raise AssertionError(
                f"'{self.__class__.__name__}' should include a `serializer_class` attribute."
            )
        return self.serializer_class

    def get_additional_serializer_class(self, name):
        """
        Retrieve additional serializers by name.
        """
        return self.additional_serializer_classes.get(name)

    def validate_serializer(self, request: Request, serializer_class=None):
        """
        Validate the serializer and handle errors.
        """
        if serializer_class is None:
            serializer_class = self.get_serializer_class()

        serializer = serializer_class(data=request.data)
        if not serializer.is_valid():
            raise ApiError(
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
                message="validation error",
                error_type=APPErrorTypes.VALIDATION_ERROR.value,
            )
        return serializer.validated_data

    def handle_serializer_validation(self, request: Request, additional_serializers=None):
        """
        Handle the primary serializer and any additional serializers.
        """
        primary_serializer = self.validate_serializer(request.data)

        if additional_serializers:
            for _, serializer_class in additional_serializers.items():
                self.validate_serializer(request.data, serializer_class)

        return primary_serializer.validated_data
