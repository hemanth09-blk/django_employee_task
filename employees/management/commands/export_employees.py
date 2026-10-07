import csv

from django.core.management.base import BaseCommand

from employees.models import Employee


class Command(BaseCommand):
    help = "Export employees to a CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            required=True,
            help="Path of the CSV output file",
        )

    def handle(self, *args, **options):
        output_file = options["output"]

        employees = Employee.objects.select_related(
            "department"
        ).all()

        fieldnames = [
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
        ]

        with open(
            output_file,
            "w",
            newline="",
            encoding="utf-8",
        ) as csvfile:

            writer = csv.DictWriter(
                csvfile,
                fieldnames=fieldnames,
            )

            writer.writeheader()

            for employee in employees:
                writer.writerow(
                    {
                        "employee_code": employee.employee_code,
                        "first_name": employee.first_name,
                        "last_name": employee.last_name,
                        "email": employee.email,
                        "phone": employee.phone,
                        "department": (
                            employee.department.code
                            if employee.department
                            else ""
                        ),
                        "designation": employee.designation,
                        "salary": employee.salary,
                        "joining_date": employee.joining_date,
                        "is_active": employee.is_active,
                    }
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully exported employees to {output_file}"
            )
        )