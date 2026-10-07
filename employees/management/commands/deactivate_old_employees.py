from datetime import date
from django.core.management.base import BaseCommand

from employees.models import Employee


class Command(BaseCommand):
    help = (
        "Deactivate employees whose joining date is more than "
        "5 years old."
    )

    def handle(self, *args, **options):
        cutoff_date = date.today().replace(year=date.today().year - 5)

        employees = Employee.objects.filter(
            joining_date__lt=cutoff_date,
            is_active=True,
        )

        count = employees.update(is_active=False)

        self.stdout.write(
            self.style.SUCCESS(
                f"Deactivated {count} employee(s). "
                f"Rule: joining date before {cutoff_date}."
            )
        )