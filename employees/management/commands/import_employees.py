from django.core.management.base import BaseCommand, CommandError

from employees.services.csv_import_service import (
    EmployeeCSVImportService,
)


class Command(BaseCommand):
    help = "Import employees from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            required=True,
            help="Path to the CSV input file",
        )

    def handle(self, *args, **options):
        file_path = options["file"]

        service = EmployeeCSVImportService()

        try:
            result = service.import_file(file_path)

        except FileNotFoundError:
            raise CommandError(
                f"CSV file not found: {file_path}"
            )

        except ValueError as exc:
            raise CommandError(str(exc))

        self.stdout.write(
            self.style.SUCCESS(
                f"Successful: {len(result['successful'])}"
            )
        )

        self.stdout.write(
            self.style.WARNING(
                f"Skipped: {len(result['skipped'])}"
            )
        )

        self.stdout.write(
            self.style.ERROR(
                f"Failed: {len(result['failed'])}"
            )
        )

        if result["skipped"]:
            self.stdout.write("\nSkipped rows:")

            for item in result["skipped"]:
                self.stdout.write(
                    f"  Row {item['row']}: "
                    f"{item.get('employee_code', '')} - "
                    f"{item['reason']}"
                )

        if result["failed"]:
            self.stdout.write("\nFailed rows:")

            for item in result["failed"]:
                self.stdout.write(
                    f"  Row {item['row']}: "
                    f"{item.get('employee_code', '')} - "
                    f"{item['reason']}"
                )