# decorators.py
from rest_framework import generics

from core.utils.paginator import Pagination


def paginate_list_view(view_class):
    """
    Decorator to apply pagination to ListAPIView.
    """
    # Check if the view class is a subclass of ListAPIView
    if not issubclass(view_class, generics.ListAPIView):
        raise ValueError("The view class must inherit from ListAPIView.")

    # Set the pagination class
    view_class.pagination_class = Pagination

    return view_class
