import logging

from django.core.cache import cache
from django.db.models import Count, Avg, Max, Q

from .models import Department

logger = logging.getLogger(__name__)

CACHE_KEY = "department_summary:v1"
CACHE_TIMEOUT = 300


def get_cached_department_summary():
    try:
        cached_data = cache.get(CACHE_KEY)

        if cached_data is not None:
            logger.info("Department summary cache HIT")
            return cached_data

        logger.info("Department summary cache MISS")

    except Exception:
        logger.exception("Redis cache read failed")

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

    result = []

    for department in departments:
        result.append({
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
        })

    try:
        cache.set(CACHE_KEY, result, CACHE_TIMEOUT)
        logger.info("Department summary stored in Redis")
    except Exception:
        logger.exception("Redis cache write failed")

    return result