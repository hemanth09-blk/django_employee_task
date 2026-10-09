import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def test_celery_task():
    return "Celery task executed successfully!"

@shared_task(
    bind=True,
    max_retries=3,
)
def send_welcome_email(self, employee_id):
    logger.info(
        "Starting welcome email task for employee_id=%s",
        employee_id,
    )

    try:
        from employees.models import Employee
        from employees.services.notification_service import NotificationService

        # Get employee using stable ID
        try:
            employee = Employee.objects.get(pk=employee_id)
        except Employee.DoesNotExist:
            logger.error(
                "Employee not found for employee_id=%s",
                employee_id,
            )
            return {
                "status": "failed",
                "message": "Employee not found",
                "employee_id": employee_id,
            }

        # Validate email before attempting to send
        if not employee.email:
            logger.error(
                "Employee %s does not have an email address",
                employee_id,
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
            "Welcome email sent successfully for employee_id=%s",
            employee_id,
        )

        return {
            "status": "success",
            "message": "Welcome email sent successfully",
            "employee_id": employee_id,
            "notification_id": notification.id,
        }

    except Exception as exc:
        logger.exception(
            "Welcome email task failed for employee_id=%s. "
            "Retry attempt=%s",
            employee_id,
            self.request.retries,
        )

        try:
            raise self.retry(
                exc=exc,
                countdown=60 * (2 ** self.request.retries),
            )
        except self.MaxRetriesExceededError:
            logger.exception(
                "Maximum retries exceeded for employee_id=%s",
                employee_id,
            )
            raise

@shared_task(bind=True, max_retries=3)
def test_retry_task(self):
    logger.info(
        "Retry test task attempt=%s",
        self.request.retries,
    )

    if self.request.retries < 3:
        raise self.retry(
            countdown=5,
        )

    logger.info("Retry test task completed successfully")

    return "Retry test completed successfully"

@shared_task(
    bind=True,
    max_retries=3,
)
def generate_employee_report(self):
    logger.info("Starting employee report generation")

    try:
        from employees.orm_reports import (
            get_salary_summary,
            get_department_summary,
        )

        salary_summary = get_salary_summary()

        department_summary = []

        for department in get_department_summary():
            department_summary.append(
                {
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
                }
            )

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

        logger.info("Employee report generated successfully")

        return {
            "status": "success",
            "message": "Employee report generated successfully",
            "report": report,
        }

    except Exception as exc:
        logger.exception(
            "Employee report generation failed. Retry attempt=%s",
            self.request.retries,
        )

        try:
            raise self.retry(
                exc=exc,
                countdown=60 * (2 ** self.request.retries),
            )
        except self.MaxRetriesExceededError:
            logger.exception(
                "Maximum retries exceeded for employee report"
            )
            raise
   
@shared_task(bind=True, max_retries=3)
def process_employee_csv(self, csv_file_path):
    logger.info("Starting CSV processing: %s", csv_file_path)

    try:
        import csv

        processed_count = 0

        with open(csv_file_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                processed_count += 1

        logger.info(
            "CSV processing completed successfully. Rows processed=%s",
            processed_count,
        )

        return {
            "status": "success",
            "message": "CSV processed successfully",
            "rows_processed": processed_count,
        }

    except Exception as exc:
        logger.exception(
            "CSV processing failed. Retry attempt=%s",
            self.request.retries,
        )

        raise self.retry(
            exc=exc,
            countdown=60 * (2 ** self.request.retries),
        )