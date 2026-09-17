from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView
)

from ..models import Employee
from .serializers import EmployeeSerializer


class EmployeeListCreateView(ListCreateAPIView):
    """
    GET  /api/v1/employees/  -> List all employees
    POST /api/v1/employees/  -> Create a new employee
    """

    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class EmployeeDetailView(RetrieveUpdateDestroyAPIView):
    """
    GET    /api/v1/employees/<id>/ -> Get employee
    PUT    /api/v1/employees/<id>/ -> Full update
    PATCH  /api/v1/employees/<id>/ -> Partial update
    DELETE /api/v1/employees/<id>/ -> Delete employee
    """

    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    lookup_field = "id"