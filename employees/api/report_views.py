from django.http import JsonResponse

from ..orm_reports import (
    get_salary_summary,
    get_department_summary,
    get_project_summary,
    get_departments_with_more_than_5_employees,
    get_employees_above_department_average,
    get_projects_with_more_than_3_employees,
    get_employees_with_multiple_projects,
    get_employees_without_projects,
)


def salary_summary(request):
    data = get_salary_summary()
    return JsonResponse(data, safe=False, status=200)


def department_summary(request):
    data = list(
        get_department_summary().values(
            "name",
            "employee_count",
            "average_salary",
            "maximum_salary",
        )
    )

    return JsonResponse(data, safe=False, status=200)
def project_summary(request):
    """
    DB-003:
    Project-wise employee statistics.

    GET /api/v1/reports/project-summary/
    """

    data = list(
        get_project_summary().values(
            "name",
            "project_code",
            "employee_count",
        )
    )

    return JsonResponse(
        data,
        safe=False,
        status=200,
    )


def departments_with_more_than_5_employees(request):
    data = list(
        get_departments_with_more_than_5_employees().values(
            "name",
            "employee_count",
        )
    )

    return JsonResponse(data, safe=False, status=200)


def employees_above_department_average(request):
    data = list(
        get_employees_above_department_average().values(
            "employee_code",
            "first_name",
            "salary",
            "department__name",
        )
    )

    return JsonResponse(data, safe=False, status=200)


def projects_with_more_than_3_employees(request):
    data = list(
        get_projects_with_more_than_3_employees().values(
            "name",
            "project_code",
            "employee_count",
        )
    )

    return JsonResponse(data, safe=False, status=200)


def employees_with_multiple_projects(request):
    data = list(
        get_employees_with_multiple_projects().values(
            "employee_code",
            "first_name",
            "project_count",
        )
    )

    return JsonResponse(data, safe=False, status=200)


def employees_without_projects(request):
    data = list(
        get_employees_without_projects().values(
            "employee_code",
            "first_name",
        )
    )

    return JsonResponse(data, safe=False, status=200)