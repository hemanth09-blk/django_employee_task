import re
from datetime import date

from rest_framework import serializers

from ..models import Employee


class EmployeeSerializer(serializers.ModelSerializer):

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

        if not value:
            raise serializers.ValidationError(
                "Employee code is required."
            )

        if not re.fullmatch(r"EMP\d{3}", value):
            raise serializers.ValidationError(
                "Employee code must follow the format EMP001."
            )

        # Check uniqueness while allowing the current employee
        # during PUT/PATCH.
        queryset = Employee.objects.filter(
            employee_code=value
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Employee with this employee code already exists."
            )

        return value

    # ---------------------------------------------------------
    # Email Validation
    # ---------------------------------------------------------
    def validate_email(self, value):

        if not value:
            raise serializers.ValidationError(
                "Email is required."
            )

        # Django/DRF email validation
        email_field = serializers.EmailField()

        try:
            value = email_field.run_validation(value)
        except serializers.ValidationError:
            raise serializers.ValidationError(
                "A valid email address is required."
            )

        # Check uniqueness while allowing the current employee
        # during PUT/PATCH.
        queryset = Employee.objects.filter(
            email=value
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Employee with this email already exists."
            )

        return value

    # ---------------------------------------------------------
    # Salary Validation
    # ---------------------------------------------------------
    def validate_salary(self, value):

        if value < 0:
            raise serializers.ValidationError(
                "Salary cannot be negative."
            )

        if value < 10000 or value > 1000000:
            raise serializers.ValidationError(
                "Salary must be between 10000 and 1000000."
            )

        return value

    # ---------------------------------------------------------
    # Joining Date Validation
    # ---------------------------------------------------------
    def validate_joining_date(self, value):

        if value > date.today():
            raise serializers.ValidationError(
                "Joining date cannot be in the future."
            )

        return value

    # ---------------------------------------------------------
    # Phone Validation
    # ---------------------------------------------------------
    def validate_phone(self, value):

        if not value:
            raise serializers.ValidationError(
                "Phone number is required."
            )

        if not re.fullmatch(r"\d{10}", str(value)):
            raise serializers.ValidationError(
                "Phone number must contain exactly 10 digits."
            )

        return value