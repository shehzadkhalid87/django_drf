from rest_framework import status

from core.common.erro_message_type import APPErrorTypes


class ApiError(Exception):
    """
    Custom exception class for API errors, providing a structured
    way to handle errors in the API response.

    Attributes:
        message (str): The main error message to describe what went wrong.
        status_code (int): HTTP status code representing the error type
        (default is 500).
        errors (list): A list of error dictionaries, each containing a
        'message' key with additional error details.
        type (str): A string indicating the type of error (default is 'unhandled').
    """

    def __init__(self, message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, errors=None,
                 error_type: APPErrorTypes = (5000, "internal server error")):
        """
        Initializes the ApiError instance with the provided message, status code, errors, and type.

        :param:
            message (str): A brief message describing the error.
            status_code (int, optional): HTTP status code (default is 500).
            errors (list or str or None, optional):
            Either a list of error messages or a single error string.
            error_type (tuple, optional): Type of the error (default is 'unhandled').
        """
        if isinstance(errors, dict):
            self.errors = errors
        elif isinstance(errors, str):
            self.errors = {"message": errors}
        else:
            self.errors = {"message": "unknown error"}

        self.message = message
        self.status_code = status_code
        self.error_type = error_type

        super().__init__(self.message)
