from rest_framework import filters, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError as DjangoValidationError
from django_filters.rest_framework import DjangoFilterBackend

from ..models import Employee, EmployeeTransfer
from ..services.employee_transfer_service import EmployeeTransferService
from .serializers import EmployeeSerializer, EmployeeTransferSerializer
from .pagination import EmployeePagination


class EmployeeViewSet(viewsets.ModelViewSet):

    queryset = Employee.objects.all().order_by("id")
    serializer_class = EmployeeSerializer
    pagination_class = EmployeePagination

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "department",
        "is_active",
    ]

    search_fields = [
        "employee_code",
        "first_name",
        "last_name",
        "email",
        "phone",
        "designation",
    ]

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
        response = super().handle_exception(exc)

        if response is not None and response.status_code == 404:
            response.data = {
                "detail": "Employee not found."
            }

        return response

    @action(detail=False, methods=["get"])
    def active(self, request):

        queryset = self.filter_queryset(
            Employee.objects
            .filter(is_active=True)
            .order_by("id")
        )

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(
                page,
                many=True
            )
            return self.get_paginated_response(
                serializer.data
            )

        serializer = self.get_serializer(
            queryset,
            many=True
        )

        return Response(serializer.data)

    # DB-005
    @action(
        detail=True,
        methods=["post"],
        url_path="transfer"
    )
    def transfer(self, request, pk=None):

        employee_id = pk

        to_department = request.data.get(
            "to_department"
        )

        reason = request.data.get(
            "reason",
            ""
        )

        if not to_department:
            return Response(
                {
                    "error": "to_department is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not reason or not reason.strip():
            return Response(
                {
                    "error": "reason is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            transferred_by = (
                str(request.user)
                if request.user.is_authenticated
                else ""
            )

            transfer = (
                EmployeeTransferService
                .transfer_employee(
                    employee_id=employee_id,
                    to_department_id=to_department,
                    reason=reason,
                    transferred_by=transferred_by,
                )
            )

            serializer = EmployeeTransferSerializer(
                transfer
            )

            return Response(
                {
                    "message":
                        "Employee transferred successfully.",
                    "transfer": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except DjangoValidationError as error:
            return Response(
                {
                    "error": error.messages
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    # DB-005
    @action(
        detail=True,
        methods=["get"],
        url_path="transfer-history"
    )
    def transfer_history(
        self,
        request,
        pk=None
    ):

        try:
            employee = Employee.objects.get(pk=pk)

        except Employee.DoesNotExist:
            return Response(
                {
                    "error": "Employee not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        transfers = (
            EmployeeTransfer.objects
            .filter(employee=employee)
            .select_related(
                "from_department",
                "to_department",
            )
            .order_by("-transferred_at")
        )

        serializer = EmployeeTransferSerializer(
            transfers,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )