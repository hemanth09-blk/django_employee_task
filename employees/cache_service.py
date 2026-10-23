import logging

from django.core.cache import cache
from django.db.models import Count, Avg, Max, Q

from .models import Department

logger = logging.getLogger(__name__)

CACHE_KEY = "department_summary:v1"
CACHE_TIMEOUT = 300


def build_department_summary():
    departments = Department.objects.annotate(
        employee_count=Count("employees"),
        active_count=Count(
            "employees",
            filter=Q(employees__is_active=True),
        ),
        inactive_count=Count(
            "employees",
            filter=Q(employees__is_active=False),
        ),
        average_salary=Avg("employees__salary"),
        maximum_salary=Max("employees__salary"),
    )

    return [
        {
            "department_id": department.id,
            "department_name": department.name,
            "employee_count": department.employee_count,
            "active_count": department.active_count,
            "inactive_count": department.inactive_count,
            "average_salary": (
                str(department.average_salary)
                if department.average_salary is not None
                else None
            ),
            "maximum_salary": (
                str(department.maximum_salary)
                if department.maximum_salary is not None
                else None
            ),
        }
        for department in departments
    ]


def get_cached_department_summary(cache_key=CACHE_KEY):
    try:
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            logger.info("Department summary cache HIT")
            return cached_data

        logger.info("Department summary cache MISS")

    except Exception:
        logger.exception("Department summary cache read failed")

    result = build_department_summary()

    try:
        cache.set(cache_key, result, CACHE_TIMEOUT)
        logger.info("Department summary stored in cache")
    except Exception:
        logger.exception("Department summary cache write failed")

    return result