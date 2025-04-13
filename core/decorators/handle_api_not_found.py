from django.http import JsonResponse
from rest_framework import status

from core.common.erro_message_type import APPErrorTypes


def handle_404_error(request, exception=None):
    """
    Custom handler for 404 Not Found errors.
    """
    # Create an instance of ApiError instead of raising it
    return JsonResponse(
        {
            "api": request.path,
            "error": [
                {"message": "API not found, please double-check the slash (/) at the end."}
            ],
            "error_type": {
                "code": APPErrorTypes.API_NOT_FOUND.value[0],
                "error": APPErrorTypes.API_NOT_FOUND.value[1],
            },
        },
        status=status.HTTP_404_NOT_FOUND
    )
