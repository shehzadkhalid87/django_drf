from django.utils.deprecation import MiddlewareMixin
from rest_framework.response import Response


class APIResponseHandler(MiddlewareMixin):
    def process_response(self, request, response):
        # Process only DRF Response instances
        if isinstance(response, Response):
            try:
                # Ensure the response is rendered
                response.render()
            except Exception as e:
                # If any rendering issue occurs, return the response as is
                return response

            # Handle only successful responses
            if response.status_code < 400:
                # Format the successful response
                formatted_response = Response({
                    "api": request.path,
                    "status": response.status_code,
                    "message": {"message": "success"},
                    "data": response.data if response.data else None
                }, status=response.status_code)

                return formatted_response

        # For non-DRF responses, return the original response
        return response
