import logging
import time

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

from core.common.erro_message_type import APPErrorTypes
from core.exceptions.base import ApiError

logger = logging.getLogger(__name__)


class ExceptionMiddleware(MiddlewareMixin):
    """
    Exception middleware to handle api exceptions
    """

    def process_request(self, request):
        # Record the start time before processing the request
        request.start_time = time.time()

    def process_exception(self, request, exception):
        time_taken = (time.time() - request.start_time) * 1000
        if isinstance(exception, ApiError):
            logger.error(f"API error: {str(exception)}")
            return JsonResponse({
                "api": request.path,
                "response_time": f"{time_taken:.2f} ms",
                "status_code": exception.status_code,
                "error_type": {"code": exception.error_type[0], "type": exception.error_type[1]},
                "errors": exception.errors,
                "data": None
            }, status=400)

        logger.error(f"Unhandled exception: {exception}", exc_info=True)
        return JsonResponse({
            "api": request.path,
            "status_code": 500,
            "error_type": {
                "code": APPErrorTypes.INTERNAL_SERVER_ERROR.value[0],
                "type": APPErrorTypes.INTERNAL_SERVER_ERROR.value[1]
            },
            "errors": "An unexpected error occurred.",
            "data": None,
        }, status=500)
