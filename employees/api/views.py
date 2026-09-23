from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from ..models import Employee
from .serializers import EmployeeSerializer
from .pagination import EmployeePagination


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    Employee CRUD API using DRF ModelViewSet.
    """

    queryset = Employee.objects.all().order_by("id")
    serializer_class = EmployeeSerializer
    pagination_class = EmployeePagination

    # Filtering, searching and ordering
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    # Exact filtering
    filterset_fields = [
        "department",
        "is_active",
    ]

    # Text searching
    search_fields = [
        "employee_code",
        "first_name",
        "last_name",
        "email",
        "phone",
        "designation",
    ]

    # Sorting
    ordering_fields = [
        "id",
        "employee_code",
        "first_name",
        "last_name",
        "salary",
        "joining_date",
        "department",
    ]

    ordering = ["id"]

    def handle_exception(self, exc):
        """
        Return standardized 404 response.
        """
        response = super().handle_exception(exc)

        if response is not None and response.status_code == 404:
            response.data = {
                "detail": "Employee not found."
            }

        return response

    @action(detail=False, methods=["get"])
    def active(self, request):
        """
        Return only active employees.
        """
        queryset = self.filter_queryset(
            Employee.objects.filter(is_active=True).order_by("id")
        )

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)