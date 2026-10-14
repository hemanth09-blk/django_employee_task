import csv
import logging
import time
from datetime import timedelta

from celery import shared_task
from django.db import OperationalError
from django.utils import timezone

logger = logging.getLogger(__name__)


# --------------------------------------------------
# Common logging helper
# --------------------------------------------------

def log_task_execution(task_name, task_id, started_at, status):
    """Log task status and execution duration."""
    duration = time.perf_counter() - started_at

    logger.info(
        "Task execution: name=%s id=%s status=%s duration=%.3fs",
        task_name,
        task_id,
        status,
        duration,
    )


def get_task_context(task):
    """Return common execution details for a Celery task."""
    return task.name, task.request.id, time.perf_counter()


def retry_task(task, exc, task_name, task_id, started_at):
    """Log a failed attempt and retry with exponential backoff."""
    log_task_execution(
        task_name, task_id, started_at, "failure"
    )

    logger.exception(
        "Task failed: name=%s id=%s retry=%s",
        task_name,
        task_id,
        task.request.retries,
        exc_info=(type(exc), exc, exc._traceback_),
    )

    raise task.retry(
        exc=exc,
        countdown=60 * (2 ** task.request.retries),
    )


# --------------------------------------------------
# Shared employee report logic
# --------------------------------------------------

def build_employee_report():
    """Build a report without launching another Celery task."""
    from employees.orm_reports import (
        get_salary_summary,
        get_department_summary,
    )

    salary_summary = get_salary_summary()

    department_summary = []

    for department in get_department_summary():
        department_summary.append({
            "department_id": department.id,
            "department_name": department.name,
            "employee_count": department.employee_count,
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

    report = {
        "salary_summary": {
            "total_employees": salary_summary["total_employees"],
            "average_salary": (
                str(salary_summary["average_salary"])
                if salary_summary["average_salary"] is not None
                else None
            ),
            "maximum_salary": (
                str(salary_summary["maximum_salary"])
                if salary_summary["maximum_salary"] is not None
                else None
            ),
            "minimum_salary": (
                str(salary_summary["minimum_salary"])
                if salary_summary["minimum_salary"] is not None
                else None
            ),
            "total_salary_expenditure": (
                str(salary_summary["total_salary_expenditure"])
                if salary_summary["total_salary_expenditure"] is not None
                else None
            ),
        },
        "department_summary": department_summary,
    }

    return {
        "status": "success",
        "message": "Employee report generated successfully",
        "report": report,
    }


# --------------------------------------------------
# Basic Celery health-check task
# --------------------------------------------------

@shared_task
def test_celery_task():
    return "Celery task executed successfully!"


# --------------------------------------------------
# Welcome email task
# --------------------------------------------------

@shared_task(bind=True, max_retries=3)
def send_welcome_email(self, employee_id):
    task_name, task_id, started_at = get_task_context(self)

    logger.info(
        "Welcome email task started: employee_id=%s task_id=%s",
        employee_id,
        task_id,
    )

    try:
        from employees.models import Employee
        from employees.services.notification_service import (
            NotificationService,
        )

        try:
            employee = Employee.objects.get(pk=employee_id)
        except Employee.DoesNotExist:
            logger.error(
                "Employee not found: employee_id=%s",
                employee_id,
            )
            log_task_execution(
                task_name, task_id, started_at, "failure"
            )
            return {
                "status": "failed",
                "message": "Employee not found",
                "employee_id": employee_id,
            }

        if not employee.email:
            logger.error(
                "Employee email is missing: employee_id=%s",
                employee_id,
            )
            log_task_execution(
                task_name, task_id, started_at, "failure"
            )
            return {
                "status": "failed",
                "message": "Employee email is missing",
                "employee_id": employee_id,
            }

        notification = NotificationService.send_welcome_notification(
            employee=employee
        )

        if notification.status != "SENT":
            raise RuntimeError(
                f"Welcome email failed for employee {employee_id}"
            )

        logger.info(
            "Welcome email sent: employee_id=%s notification_id=%s",
            employee_id,
            notification.id,
        )

        log_task_execution(
            task_name, task_id, started_at, "success"
        )

        return {
            "status": "success",
            "message": "Welcome email sent successfully",
            "employee_id": employee_id,
            "notification_id": notification.id,
        }

    except Exception as exc:
        return retry_task(
            self, exc, task_name, task_id, started_at
        )


# --------------------------------------------------
# Retry demonstration task
# --------------------------------------------------

@shared_task(bind=True, max_retries=3)
def test_retry_task(self):
    task_name, task_id, started_at = get_task_context(self)

    logger.info(
        "Retry test attempt=%s task_id=%s",
        self.request.retries,
        task_id,
    )

    if self.request.retries < 3:
        raise self.retry(countdown=5)

    log_task_execution(
        task_name, task_id, started_at, "success"
    )

    return "Retry test completed successfully"


# --------------------------------------------------
# Employee report task
# --------------------------------------------------

@shared_task(bind=True, max_retries=3)
def generate_employee_report(self):
    task_name, task_id, started_at = get_task_context(self)

    logger.info("Employee report started: task_id=%s", task_id)

    try:
        report = build_employee_report()

        logger.info(
            "Employee report generated: task_id=%s",
            task_id,
        )

        log_task_execution(
            task_name, task_id, started_at, "success"
        )

        return report

    except Exception as exc:
        return retry_task(
            self, exc, task_name, task_id, started_at
        )


# --------------------------------------------------
# CSV processing task
# --------------------------------------------------

@shared_task(bind=True, max_retries=3)
def process_employee_csv(self, csv_file_path):
    task_name, task_id, started_at = get_task_context(self)

    logger.info(
        "CSV processing started: path=%s task_id=%s",
        csv_file_path,
        task_id,
    )

    try:
        with open(
            csv_file_path,
            "r",
            newline="",
            encoding="utf-8-sig",
        ) as file:
            reader = csv.DictReader(file)

            if not reader.fieldnames:
                raise ValueError("CSV file has no header row")

            processed_count = sum(1 for _ in reader)

        log_task_execution(
            task_name, task_id, started_at, "success"
        )

        logger.info(
            "CSV processing completed: rows=%s task_id=%s",
            processed_count,
            task_id,
        )

        return {
            "status": "success",
            "message": "CSV processed successfully",
            "rows_processed": processed_count,
        }

    except (OSError, OperationalError) as exc:
        return retry_task(
            self, exc, task_name, task_id, started_at
        )

    except Exception:
        log_task_execution(
            task_name, task_id, started_at, "failure"
        )
        logger.exception(
            "CSV processing failed permanently: task_id=%s",
            task_id,
        )
        raise


# --------------------------------------------------
# Scheduled daily employee report
# --------------------------------------------------

@shared_task(bind=True, max_retries=3)
def daily_employee_report_task(self):
    """Generate the daily report without a nested Celery task."""
    task_name, task_id, started_at = get_task_context(self)

    logger.info(
        "Daily employee report started: task_id=%s",
        task_id,
    )

    try:
        # Call ordinary Python logic directly.
        # Do not use generate_employee_report.apply().get().
        report = build_employee_report()

        logger.info(
            "Daily employee report completed: task_id=%s",
            task_id,
        )

        log_task_execution(
            task_name, task_id, started_at, "success"
        )

        return report

    except Exception as exc:
        return retry_task(
            self, exc, task_name, task_id, started_at
        )


# --------------------------------------------------
# Scheduled inactive employee maintenance
# --------------------------------------------------

@shared_task(
    bind=True,
    max_retries=3,
    autoretry_for=(OperationalError,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
)
def deactivate_old_employees_task(self):
    """Deactivate active employees whose joining date is over 365 days old."""
    task_name, task_id, started_at = get_task_context(self)

    logger.info(
        "Inactive employee maintenance started: task_id=%s",
        task_id,
    )

    try:
        from employees.models import Employee

        cutoff_date = (
            timezone.now().date() - timedelta(days=365)
        )

        updated_count = Employee.objects.filter(
            is_active=True,
            joining_date__lt=cutoff_date,
        ).update(is_active=False)

        logger.info(
            "Inactive employee maintenance completed: "
            "deactivated=%s task_id=%s",
            updated_count,
            task_id,
        )

        log_task_execution(
            task_name, task_id, started_at, "success"
        )

        return {
            "status": "success",
            "employees_deactivated": updated_count,
        }

    except Exception:
        log_task_execution(
            task_name, task_id, started_at, "failure"
        )
        logger.exception(
            "Inactive employee maintenance failed: task_id=%s",
            task_id,
        )
        raise


# --------------------------------------------------
# Worker-loss recovery test task
# --------------------------------------------------

@shared_task(
    bind=True,
    acks_late=True,
    reject_on_worker_lost=True,
)
def test_worker_recovery_task(self, marker):
    """Test redelivery behavior after unexpected worker loss."""
    task_name, task_id, started_at = get_task_context(self)

    logger.info(
        "Worker recovery task executed: marker=%s task_id=%s",
        marker,
        task_id,
    )

    log_task_execution(
        task_name, task_id, started_at, "success"
    )

    return {
        "status": "success",
        "marker": marker,
        "task_id": task_id,
    }