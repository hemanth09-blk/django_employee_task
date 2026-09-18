from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from ..models import Employee
from .serializers import EmployeeSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    Employee CRUD API using DRF ModelViewSet.

    GET     /api/v1/employees/       -> List employees
    POST    /api/v1/employees/       -> Create employee
    GET     /api/v1/employees/{id}/  -> Retrieve employee
    PUT     /api/v1/employees/{id}/  -> Full update
    PATCH   /api/v1/employees/{id}/  -> Partial update
    DELETE  /api/v1/employees/{id}/  -> Delete employee
    """

    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    # Filtering
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = {
        "department": ["exact"],
        "is_active": ["exact"],
        "salary": ["exact", "gte", "lte"],
    }

    # Searching
    search_fields = [
        "first_name",
        "last_name",
        "email",
        "employee_code",
        "department",
    ]

    # Ordering
    ordering_fields = [
        "salary",
        "joining_date",
    ]

    ordering = ["id"]

    # Custom action
    @action(detail=False, methods=["get"], url_path="active")
    def active(self, request):
        """
        Return only active employees.
        """

        employees = self.get_queryset().filter(is_active=True)

        serializer = self.get_serializer(employees, many=True)

        return Response(serializer.data)