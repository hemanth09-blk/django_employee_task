from decimal import Decimal

from django.db.models import (
    Q,
    F,
    Count,
    Sum,
    Avg,
    Min,
    Max,
    OuterRef,
    Subquery,
)

from .models import Employee, Department, Project


# ---------------------------------------------------------
# 1. Q OBJECTS
# ---------------------------------------------------------

def get_backend_or_data_employees():
    """
    Get employees who belong to Backend OR Data department.
    """
    employees = Employee.objects.filter(
        Q(department__name="Backend")
        | Q(department__name="Data")
    )

    return employees


# ---------------------------------------------------------
# 2. F EXPRESSIONS
# ---------------------------------------------------------

def increase_employee_salary_by_10_percent(employee_code):
    """
    Increase the salary of a specific employee by 10%.
    Uses F expression so the calculation happens in the database.
    """
    updated_count = Employee.objects.filter(
        employee_code=employee_code
    ).update(
        salary=F("salary") * Decimal("1.10")
    )

    return updated_count


# ---------------------------------------------------------
# 3. AGGREGATION
# ---------------------------------------------------------

def get_salary_summary():
    """
    Return overall employee salary statistics.
    """
    summary = Employee.objects.aggregate(
        total_employees=Count("id"),
        average_salary=Avg("salary"),
        maximum_salary=Max("salary"),
        minimum_salary=Min("salary"),
        total_salary_expenditure=Sum("salary"),
    )

    return summary


# ---------------------------------------------------------
# 4. ANNOTATION - DEPARTMENT SUMMARY
# ---------------------------------------------------------

def get_department_summary():
    """
    Return department-wise employee count and salary statistics.
    """
    departments = Department.objects.annotate(
        employee_count=Count("employees"),
        average_salary=Avg("employees__salary"),
        maximum_salary=Max("employees__salary"),
    )

    return departments


# ---------------------------------------------------------
# 5. QUERY A
# Departments having more than 5 employees
# ---------------------------------------------------------

def get_departments_with_more_than_5_employees():
    """
    Return departments with more than 5 employees.
    """
    departments = Department.objects.annotate(
        employee_count=Count("employees")
    ).filter(
        employee_count__gt=5
    )

    return departments


# ---------------------------------------------------------
# 6. QUERY B
# Employees earning above department average
# ---------------------------------------------------------

def get_employees_above_department_average():
    """
    Return employees whose salary is greater than
    the average salary of their department.
    """

    department_average = (
        Employee.objects
        .filter(department_id=OuterRef("department_id"))
        .values("department_id")
        .annotate(
            average_salary=Avg("salary")
        )
        .values("average_salary")
    )

    employees = Employee.objects.annotate(
        department_average_salary=Subquery(
            department_average
        )
    ).filter(
        salary__gt=F("department_average_salary")
    )

    return employees


# ---------------------------------------------------------
# 7. QUERY C
# Projects having more than 3 employees
# ---------------------------------------------------------

def get_projects_with_more_than_3_employees():
    """
    Return projects having more than 3 employees.
    """
    projects = Project.objects.annotate(
        employee_count=Count("employees")
    ).filter(
        employee_count__gt=3
    )

    return projects


# ---------------------------------------------------------
# 8. QUERY D
# Employees working on multiple projects
# ---------------------------------------------------------

def get_employees_with_multiple_projects():
    """
    Return employees assigned to more than one project.
    """
    employees = Employee.objects.annotate(
        project_count=Count("projects")
    ).filter(
        project_count__gt=1
    )

    return employees


# ---------------------------------------------------------
# 9. QUERY E
# Employees without projects
# ---------------------------------------------------------

def get_employees_without_projects():
    """
    Return employees who are not assigned to any project.
    """
    employees = Employee.objects.filter(
        projects__isnull=True
    )

    return employees


# ---------------------------------------------------------
# 10. PROJECT SUMMARY
# ---------------------------------------------------------

def get_project_summary():
    """
    Return project-wise employee count.
    """
    projects = Project.objects.annotate(
        employee_count=Count("employees")
    )

    return projects