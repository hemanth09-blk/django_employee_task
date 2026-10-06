from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import filters, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from django.core.exceptions import ValidationError as DjangoValidationError
from django_filters.rest_framework import DjangoFilterBackend

from .permissions import (
    IsAdmin,
    IsHR,
    IsManager,
    IsEmployee,
    IsAdminOrHR,
    IsAdminOrHROrManager,
    IsAdminOrHROrManagerOrEmployee,
    IsOwnerOrHROrAdmin,
)

from ..models import Employee, EmployeeTransfer,EmployeeProfile
from ..services.employee_transfer_service import EmployeeTransferService

from .serializers import (
    EmployeeSerializer,
    EmployeeTransferSerializer,
    RegistrationSerializer,
    LoginSerializer,
    EmployeeProfileSerializer,
)

from .pagination import EmployeePagination


# =====================================================
# Employee ViewSet
# =====================================================

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

    # =================================================
    # SEC-003: Role-Based Permissions
    # =================================================

    def get_permissions(self):

        # ADMIN + HR
        # Can create employees
        if self.action == "create":
            permission_classes = [
                IsAdminOrHR
            ]

        # ADMIN + HR
        # Can update employees
        elif self.action in [
            "update",
            "partial_update",
        ]:
            permission_classes = [
                IsAdminOrHR
            ]

        # ADMIN only
        # Can delete employees
        elif self.action == "destroy":
            permission_classes = [
                IsAdmin
            ]

        # ADMIN + HR + MANAGER
        # Can view employee list
        elif self.action in [
            "list",
            "active",
        ]:
            permission_classes = [
                IsAdminOrHROrManagerOrEmployee
            ]

        # ADMIN + HR + MANAGER + EMPLOYEE
        # Can retrieve an employee
        elif self.action == "retrieve":
            permission_classes = [
                IsAdminOrHROrManagerOrEmployee
            ]

        # ADMIN + HR
        # Employee department transfer
        elif self.action == "transfer":
            permission_classes = [
                IsAdminOrHR
            ]

        # ADMIN + HR + MANAGER
        # View transfer history
        elif self.action == "transfer_history":
            permission_classes = [
                IsAdminOrHROrManagerOrEmployee
            ]

        # Default
        else:
            permission_classes = [
                IsAuthenticated
            ]

        return [
            permission()
            for permission in permission_classes
        ]

    # =================================================
    # Error Handling
    # =================================================

    def handle_exception(self, exc):

        response = super().handle_exception(exc)

        if (
            response is not None
            and response.status_code == 404
        ):
            response.data = {
                "detail": "Employee not found."
            }

        return response

    # =================================================
    # GET ACTIVE EMPLOYEES
    # =================================================

    @action(
        detail=False,
        methods=["get"]
    )
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

        return Response(
            serializer.data
        )

    # =================================================
    # DB-005: EMPLOYEE TRANSFER
    # =================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="transfer"
    )
    def transfer(
        self,
        request,
        pk=None
    ):

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
                    "detail": "to_department is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            not reason
            or not reason.strip()
        ):

            return Response(
                {
                    "detail": "reason is required."
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
                    "transfer":
                        serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except DjangoValidationError as error:

            return Response(
                {
                    "detail": error.messages
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    # =================================================
    # DB-005: TRANSFER HISTORY
    # =================================================

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

            employee = Employee.objects.get(
                pk=pk
            )

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


# =====================================================
# SEC-001: User Registration API
# =====================================================

class RegisterView(APIView):

    permission_classes = [
        AllowAny
    ]

    authentication_classes = []

    def post(
        self,
        request
    ):

        serializer = RegistrationSerializer(
            data=request.data
        )

        if serializer.is_valid():

            user = serializer.save()

            return Response(
                {
                    "message":
                        "User registered successfully.",
                    "user": {
                        "id":
                            user.id,
                        "username":
                            user.username,
                        "email":
                            user.email,
                        "first_name":
                            user.first_name,
                        "last_name":
                            user.last_name,
                    }
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


# =====================================================
# SEC-001: User Login API
# =====================================================

class LoginView(APIView):

    permission_classes = [
        AllowAny
    ]

    authentication_classes = []

    def post(
        self,
        request
    ):

        serializer = LoginSerializer(
            data=request.data
        )

        if serializer.is_valid():

            user = (
                serializer
                .validated_data["user"]
            )

            return Response(
                {
                    "message":
                        "Login successful.",
                    "user": {
                        "id":
                            user.id,
                        "username":
                            user.username,
                        "email":
                            user.email,
                        "first_name":
                            user.first_name,
                        "last_name":
                            user.last_name,
                    }
                },
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    # =====================================================
# SEC-003: Employee Own Profile
# =====================================================

# =====================================================
# SEC-005: My Employee Profile
# =====================================================

class MyProfileView(APIView):
    permission_classes = [IsOwnerOrHROrAdmin]

    def get_profile(self, request):
        try:
            employee = Employee.objects.get(
                user=request.user
            )
        except Employee.DoesNotExist:
            return None

        profile, created = EmployeeProfile.objects.get_or_create(
            employee=employee
        )

        return profile

    def get(self, request):
        profile = self.get_profile(request)

        if profile is None:
            return Response(
                {"detail": "Employee profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        self.check_object_permissions(request, profile)

        serializer = EmployeeProfileSerializer(profile)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request):
        profile = self.get_profile(request)

        if profile is None:
            return Response(
                {"detail": "Employee profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        self.check_object_permissions(request, profile)

        serializer = EmployeeProfileSerializer(
            profile,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


# =====================================================
# SEC-005: Employee Profile by ID
# =====================================================

class EmployeeProfileView(APIView):
    permission_classes = [IsOwnerOrHROrAdmin]

    def get_profile(self, employee_id):
        try:
            return EmployeeProfile.objects.select_related(
                "employee__user"
            ).get(
                employee_id=employee_id
            )
        except EmployeeProfile.DoesNotExist:
            return None

    def get(self, request, employee_id):
        profile = self.get_profile(employee_id)

        if profile is None:
            return Response(
                {"detail": "Employee profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        self.check_object_permissions(request, profile)

        serializer = EmployeeProfileSerializer(profile)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, employee_id):
        profile = self.get_profile(employee_id)

        if profile is None:
            return Response(
                {"detail": "Employee profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        self.check_object_permissions(request, profile)

        serializer = EmployeeProfileSerializer(
            profile,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
    # =====================================================
# ADV-001: Health Check
# =====================================================

class HealthCheckView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return Response(
            {
                "status": "healthy",
                "service": "employee_management_api",
            },
            status=status.HTTP_200_OK,
        )   