import logging

from celery.result import AsyncResult
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from ..tasks import generate_employee_report
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

logger = logging.getLogger(__name__)


# ============================================================
# DB-003: ADVANCED ORM REPORTING
# ============================================================

@require_GET
def salary_summary(request):
    data = get_salary_summary()
    return JsonResponse(data, safe=False, status=200)


@require_GET
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


@require_GET
def project_summary(request):
    data = list(
        get_project_summary().values(
            "name",
            "project_code",
            "employee_count",
        )
    )
    return JsonResponse(data, safe=False, status=200)


@require_GET
def departments_with_more_than_5_employees(request):
    data = list(
        get_departments_with_more_than_5_employees().values(
            "name",
            "employee_count",
        )
    )
    return JsonResponse(data, safe=False, status=200)


@require_GET
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


@require_GET
def projects_with_more_than_3_employees(request):
    data = list(
        get_projects_with_more_than_3_employees().values(
            "name",
            "project_code",
            "employee_count",
        )
    )
    return JsonResponse(data, safe=False, status=200)


@require_GET
def employees_with_multiple_projects(request):
    data = list(
        get_employees_with_multiple_projects().values(
            "employee_code",
            "first_name",
            "project_count",
        )
    )
    return JsonResponse(data, safe=False, status=200)


@require_GET
def employees_without_projects(request):
    data = list(
        get_employees_without_projects().values(
            "employee_code",
            "first_name",
        )
    )
    return JsonResponse(data, safe=False, status=200)


# ============================================================
# ADV-004: CELERY BACKGROUND REPORT PROCESSING
# ============================================================

@csrf_exempt
@require_POST
def employee_report_async(request):
    """Queue report generation without waiting for completion."""
    try:
        task = generate_employee_report.delay()

        logger.info(
            "Employee report task submitted: %s",
            task.id,
        )

        return JsonResponse(
            {
                "status": "accepted",
                "message": "Employee report generation started",
                "task_id": task.id,
            },
            status=202,
        )

    except Exception:
        logger.exception(
            "Failed to submit employee report task"
        )
        return JsonResponse(
            {
                "status": "error",
                "message": "Could not start employee report generation",
            },
            status=503,
        )


@csrf_exempt
@require_GET
def employee_report_status(request, task_id):
    """Return the status of a submitted Celery task."""
    task = AsyncResult(task_id)

    response = {
        "task_id": task_id,
        "status": task.status,
    }

    if task.successful():
        response["result"] = task.result
    elif task.failed():
        response["error"] = str(task.result)

    return JsonResponse(response, status=200)