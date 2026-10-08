from decimal import Decimal
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers

from employees.models import Employee, EmployeeTransfer, EmployeeProfile, Notification


class EmployeeSerializer(serializers.ModelSerializer):
    """
    Serializer for Employee model.

    Includes field-level validation for:
    - Employee code
    - Email
    - Phone number
    - Salary
    - Joining date
    """

    class Meta:
        model = Employee
        fields = [
            "id",
            "employee_code",
            "first_name",
            "last_name",
            "email",
            "phone",
            "department",
            "designation",
            "salary",
            "joining_date",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    # ---------------------------------------------------------
    # Employee Code Validation
    # ---------------------------------------------------------
    def validate_employee_code(self, value):
        """
        Employee code must follow EMP001 format.
        """

        if not value.startswith("EMP") or not value[3:].isdigit():
            raise serializers.ValidationError(
                "Employee code must follow the format EMP001."
            )

        return value

    # ---------------------------------------------------------
    # Email Validation
    # ---------------------------------------------------------
    def validate_email(self, value):
        """
        Email must be unique.
        """

        queryset = Employee.objects.filter(email__iexact=value)

        # During PUT/PATCH, exclude current employee
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                "Employee with this email already exists."
            )

        return value

    # ---------------------------------------------------------
    # Phone Validation
    # ---------------------------------------------------------
    def validate_phone(self, value):
        """
        Phone number must contain exactly 10 digits and be unique.
        """

        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError(
                "Phone number must contain exactly 10 digits."
            )

        queryset = Employee.objects.filter(phone=value)

        # During PUT/PATCH, exclude current employee
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                "Employee with this phone number already exists."
            )

        return value

    # ---------------------------------------------------------
    # Salary Validation
    # ---------------------------------------------------------
    def validate_salary(self, value):
        """
        Salary must be between 10,000 and 1,000,000.
        """

        if value < Decimal("0"):
            raise serializers.ValidationError(
                "Salary cannot be negative."
            )

        if value < Decimal("10000") or value > Decimal("1000000"):
            raise serializers.ValidationError(
                "Salary must be between 10000 and 1000000."
            )

        return value

    # ---------------------------------------------------------
    # Joining Date Validation
    # ---------------------------------------------------------
    def validate_joining_date(self, value):
        """
        Joining date cannot be in the future.
        """

        if value > timezone.localdate():
            raise serializers.ValidationError(
                "Joining date cannot be in the future."
            )

        return value

    # ---------------------------------------------------------
    # Object-level Validation
    # ---------------------------------------------------------
    def validate(self, attrs):
        """
        Object-level validation.
        """

        return attrs
    from rest_framework import serializers

from employees.models import EmployeeTransfer


class EmployeeTransferSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmployeeTransfer
        fields = [
            "id",
            "employee",
            "from_department",
            "to_department",
            "reason",
            "transferred_by",
            "transferred_at",
            "status",
        ]

        read_only_fields = [
            "id",
            "employee",
            "from_department",
            "transferred_at",
            "status",
        ]
        # =========================================================
# User Registration Serializer
# =========================================================

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True
    )

    password_confirmation = serializers.CharField(
        write_only=True,
        required=True
    )
    email = serializers.EmailField(
        required=True
    )   

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password_confirmation",
            "first_name",
            "last_name",
        ]

    def validate_username(self, value):
        """
        Username must be unique.
        """

        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "Username already exists."
            )

        return value

    def validate_email(self, value):
        """
        Email must be valid and unique.
        """

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "Email already exists."
            )

        return value.lower()

    def validate_password(self, value):
        """
        Validate password strength using Django's
        built-in password validators.
        """

        validate_password(value)
        return value

    def validate(self, attrs):
        """
        Check password confirmation.
        """

        if attrs.get("password") != attrs.get("password_confirmation"):
            raise serializers.ValidationError({
                "password_confirmation": "Passwords do not match."
            })

        return attrs

    def create(self, validated_data):
        """
        Create the user using Django's create_user()
        so the password is securely hashed.
        """

        validated_data.pop("password_confirmation", None)

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )

        return user
        # =========================================================
# User Login Serializer
# =========================================================

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True
    )

    password = serializers.CharField(
        required=True,
        write_only=True
    )

    def validate(self, attrs):

        username = attrs.get("username")
        password = attrs.get("password")

        # Check whether the user exists
        try:
            user = User.objects.get(
                username__iexact=username
            )
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "Invalid username or password."
            )

        # Prevent inactive users from logging in
        if not user.is_active:
            raise serializers.ValidationError(
                "User account is inactive."
            )

        # Authenticate username + password
        authenticated_user = authenticate(
            username=user.username,
            password=password
        )

        if authenticated_user is None:
            raise serializers.ValidationError(
                "Invalid username or password."
            )

        attrs["user"] = authenticated_user

        return attrs
    # =========================================================
# Employee Profile Serializer - SEC-005
# =========================================================

class EmployeeProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeProfile
        fields = [
            "id",
            "employee",
            "date_of_birth",
            "address",
            "emergency_contact",
            "blood_group",
            "profile_image",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "employee",
            "created_at",
            "updated_at",
        ]
        # =========================================================
# Notification Serializer - ADV-003
# =========================================================

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "notification_type",
            "title",
            "message",
            "recipient_email",
            "status",
            "is_read",
            "read_at",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "notification_type",
            "title",
            "message",
            "recipient_email",
            "status",
            "is_read",
            "read_at",
            "created_at",
        ]