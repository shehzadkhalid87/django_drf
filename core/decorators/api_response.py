from functools import wraps
from rest_framework.response import Response
import  time

def api_response(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        start_time = time.time()
        response = func(self, *args, **kwargs)
        response_time_ms = int((time.time() - start_time) * 1000)
        if isinstance(response, Response):
            return Response({
                "api": self.request.path,
                "response_time": f"{response_time_ms}ms",
                "status_code": response.status_code,
                "error_type": None,
                "errors": None,
                "data": response.data if response.data else None
            }, status=response.status_code)
        return response
    return wrapper