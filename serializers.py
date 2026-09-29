from decimal import Decimal
from django.utils import timezone
from rest_framework import serializers

from employees.models import Employee


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