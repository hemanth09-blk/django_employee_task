from django.contrib import admin
from .models import Employee
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "employee_code",
        "first_name",
        "last_name",
        "email",
        "department",
        "designation",
        "salary",
        "joining_date",
        "is_active",
    )
    search_fields = (
        "employee_code",
        "first_name",
        "last_name",
        "email",
        "department",
    )
    list_filter = (
        "department",
        "designation",
        "is_active",
    )
    ordering = ("employee_code",)