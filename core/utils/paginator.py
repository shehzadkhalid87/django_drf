from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class Pagination(PageNumberPagination):
    """
    Custom pagination class that supports dynamic page size through a query parameter
    and handles invalid page requests by returning an empty result set.
    """

    # Default pagination settings
    page_size = 10  # Default number of items per page
    page_size_query_param = "page_limit"  # Parameter to specify the number of items per page
    page_query_param = "page"  # Parameter to specify the page number
    max_page_size = 100  # Maximum allowed number of items per page

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginates the queryset based on the request. If an invalid page is requested, it returns an empty list.

        Args:
            queryset: The set of data that needs to be paginated.
            request: The HTTP request object that may contain pagination parameters.
            view: The view instance that is using the paginator (optional).

        Returns:
            A paginated subset of the queryset, or an empty list if the page number is invalid.
        """
        try:
            return super().paginate_queryset(queryset, request, view)
        except NotFound:
            # If the page is not found (invalid page number), return an empty list
            self.page = None
            return []

    def get_paginated_response(self, data):
        """
        Returns a paginated response with metadata such as total count, current page, page size (limit),
        and links to the next and previous pages.

        Args:
            data: The paginated data that needs to be included in the response.

        Returns:
            A Response object containing pagination details and the paginated data.
        """
        # Determine current page and limit
        current_page = self.page.number if self.page else 0
        limit = self.page.paginator.per_page if self.page else self.page_size

        return Response({
            "total_count": self.page.paginator.count if self.page else 0,  # Total number of items
            "page": current_page,  # The current page number
            "limit": limit,  # The number of items per page
            "next": self.get_next_link() if self.page else None,  # URL for the next page
            "previous": self.get_previous_link() if self.page else None,  # URL for the previous page
            "result": data  # The actual paginated data (empty array if page is invalid)
        })
