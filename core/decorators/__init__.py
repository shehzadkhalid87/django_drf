import logging
from functools import wraps

from rest_framework.response import Response

from core.exceptions.base import ApiError

logger = logging.getLogger(__name__)


def handle_exceptions(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except ApiError as e:
            logger.exception(f"custom exception: {e.message}", exc_info=True)
            return Response({'error': e.message}, status=e.status_code)
        except Exception as e:
            logger.error(f"Unhandled exception: {e}", exc_info=True)
            return Response({'error': 'An unexpected error occurred.'}, status=500)

    return _wrapped_view
