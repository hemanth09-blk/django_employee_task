from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand

from employees.models import Employee, Department


class Command(BaseCommand):
    help = "Seed sample employee records"

    def handle(self, *args, **options):

        department, _ = Department.objects.get_or_create(
            code="IT",
            defaults={
                "name": "Information Technology",
                "description": "IT Department",
                "is_active": True,
            },
        )

        employees = [
            {
                "employee_code": "EMP001",
                "first_name": "John",
                "last_name": "Smith",
                "email": "john.smith@example.com",
                "phone": "9876543210",
                "designation": "Software Engineer",
                "salary": Decimal("60000.00"),
                "joining_date": date(2024, 1, 15),
            },
            {
                "employee_code": "EMP002",
                "first_name": "Sarah",
                "last_name": "Johnson",
                "email": "sarah.johnson@example.com",
                "phone": "9876543211",
                "designation": "Senior Developer",
                "salary": Decimal("80000.00"),
                "joining_date": date(2023, 6, 10),
            },
            {
                "employee_code": "EMP003",
                "first_name": "David",
                "last_name": "Williams",
                "email": "david.williams@example.com",
                "phone": "9876543212",
                "designation": "Project Manager",
                "salary": Decimal("90000.00"),
                "joining_date": date(2022, 3, 20),
            },
        ]

        created_count = 0
        skipped_count = 0

        for employee_data in employees:

            employee, created = Employee.objects.get_or_create(
                employee_code=employee_data["employee_code"],
                defaults={
                    **employee_data,
                    "department": department,
                },
            )

            if created:
                created_count += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created: {employee.employee_code}"
                    )
                )

            else:
                skipped_count += 1

                self.stdout.write(
                    self.style.WARNING(
                        f"Skipped existing: {employee.employee_code}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeding completed. "
                f"Created: {created_count}, "
                f"Skipped: {skipped_count}"
            )
        )