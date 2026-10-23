import logging

from django.core.cache import cache
from django.db import transaction
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .cache_service import CACHE_KEY
from .models import Department, Employee, EmployeeAudit

logger = logging.getLogger(__name__)


def invalidate_department_summary_cache():
    def invalidate():
        try:
            cache.delete(CACHE_KEY)
            logger.info("Department summary cache invalidated")
        except Exception:
            logger.exception("Failed to invalidate department summary cache")

    transaction.on_commit(invalidate)


@receiver(post_save, sender=Employee)
def employee_audit_signal(sender, instance, created, **kwargs):
    try:
        action = "CREATE" if created else "UPDATE"

        EmployeeAudit.objects.create(
            employee=instance,
            action=action,
        )

        logger.info(
            "Employee audit created | employee_id=%s | action=%s",
            instance.id,
            action,
        )
    except Exception:
        logger.exception(
            "Failed to create employee audit | employee_id=%s",
            instance.id,
        )

    invalidate_department_summary_cache()


@receiver(post_delete, sender=Employee)
def employee_delete_cache_signal(sender, instance, **kwargs):
    invalidate_department_summary_cache()


@receiver(post_save, sender=Department)
@receiver(post_delete, sender=Department)
def department_cache_signal(sender, instance, **kwargs):
    invalidate_department_summary_cache()