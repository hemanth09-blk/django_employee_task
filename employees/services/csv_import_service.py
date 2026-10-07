import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.db import transaction

from employees.models import Employee, Department


REQUIRED_COLUMNS = {
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
}


class EmployeeCSVImportService:

    def __init__(self):
        self.successful = []
        self.skipped = []
        self.failed = []

    def import_file(self, file_path):
        self.successful = []
        self.skipped = []
        self.failed = []
        
        with open(
            file_path,
            "r",
            newline="",
            encoding="utf-8-sig",
        ) as csvfile:

            reader = csv.DictReader(csvfile)

            if not reader.fieldnames:
                raise ValueError(
                    "CSV file is empty or has no header."
                )

            headers = {
                header.strip()
                for header in reader.fieldnames
                if header
            }

            missing_columns = REQUIRED_COLUMNS - headers

            if missing_columns:
                raise ValueError(
                    "Missing required columns: "
                    + ", ".join(sorted(missing_columns))
                )

            for row_number, row in enumerate(reader, start=2):
                self._process_row(row_number, row)

        return {
            "successful": self.successful,
            "skipped": self.skipped,
            "failed": self.failed,
        }

    def _process_row(self, row_number, row):

        employee_code = (
            row.get("employee_code") or ""
        ).strip()

        email = (
            row.get("email") or ""
        ).strip().lower()

        if not employee_code:
            self.failed.append({
                "row": row_number,
                "reason": "Employee code is required.",
            })
            return

        if not email:
            self.failed.append({
                "row": row_number,
                "employee_code": employee_code,
                "reason": "Email is required.",
            })
            return

        if Employee.objects.filter(
            employee_code=employee_code
        ).exists():

            self.skipped.append({
                "row": row_number,
                "employee_code": employee_code,
                "reason": "Employee code already exists.",
            })
            return

        if Employee.objects.filter(
            email=email
        ).exists():

            self.skipped.append({
                "row": row_number,
                "employee_code": employee_code,
                "reason": "Email already exists.",
            })
            return

        try:
            first_name = (
                row.get("first_name") or ""
            ).strip()

            last_name = (
                row.get("last_name") or ""
            ).strip()

            phone = (
                row.get("phone") or ""
            ).strip()

            designation = (
                row.get("designation") or ""
            ).strip()

            department_code = (
                row.get("department") or ""
            ).strip()

            if not first_name:
                raise ValueError(
                    "First name is required."
                )

            if not last_name:
                raise ValueError(
                    "Last name is required."
                )

            if not designation:
                raise ValueError(
                    "Designation is required."
                )

            salary = Decimal(
                (row.get("salary") or "").strip()
            )

            if salary < 0:
                raise ValueError(
                    "Salary cannot be negative."
                )

            joining_date = datetime.strptime(
                (row.get("joining_date") or "").strip(),
                "%Y-%m-%d",
            ).date()

            department = None

            if department_code:
                department = Department.objects.filter(
                    code=department_code
                ).first()

                if not department:
                    raise ValueError(
                        f"Department '{department_code}' "
                        "does not exist."
                    )

            active_value = (
                row.get("is_active") or "True"
            ).strip().lower()

            if active_value in {"true", "1", "yes"}:
                is_active = True
            elif active_value in {"false", "0", "no"}:
                is_active = False
            else:
                raise ValueError(
                    "is_active must be True or False."
                )

            with transaction.atomic():
                employee = Employee.objects.create(
                    employee_code=employee_code,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone=phone,
                    department=department,
                    designation=designation,
                    salary=salary,
                    joining_date=joining_date,
                    is_active=is_active,
                )

            self.successful.append({
                "row": row_number,
                "employee_code": employee.employee_code,
            })

        except (InvalidOperation, ValueError) as exc:

            self.failed.append({
                "row": row_number,
                "employee_code": employee_code,
                "reason": str(exc),
            })

        except Exception as exc:

            self.failed.append({
                "row": row_number,
                "employee_code": employee_code,
                "reason": f"Unexpected error: {str(exc)}",
            })