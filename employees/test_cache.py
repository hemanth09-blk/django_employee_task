from decimal import Decimal
from unittest.mock import patch

from django.core.cache import cache
from django.db import transaction
from django.test import TestCase

from .cache_service import CACHE_KEY, get_cached_department_summary
from .models import Department, Employee


class DepartmentSummaryCacheTests(TestCase):
    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def create_employee(self, department, **overrides):
        values = {
            "employee_code": "CACHE001",
            "first_name": "Cache",
            "last_name": "Test",
            "email": "cache@example.com",
            "designation": "Engineer",
            "salary": "50000.00",
            "joining_date": "2025-01-01",
            "department": department,
        }
        values.update(overrides)
        return Employee.objects.create(**values)

    def test_cache_miss_queries_database_and_hit_does_not(self):
        department = Department.objects.create(name="Engineering", code="ENG")
        self.create_employee(department)

        with self.assertNumQueries(1):
            first_result = get_cached_department_summary()

        with self.assertNumQueries(0):
            second_result = get_cached_department_summary()

        self.assertEqual(first_result, second_result)
        self.assertEqual(first_result[0]["employee_count"], 1)
        self.assertEqual(first_result[0]["active_count"], 1)
        self.assertEqual(
            Decimal(first_result[0]["average_salary"]),
            Decimal("50000.00"),
        )

    def test_empty_department_table_returns_cached_empty_list(self):
        with self.assertNumQueries(1):
            result = get_cached_department_summary()

        self.assertEqual(result, [])
        self.assertEqual(cache.get(CACHE_KEY), [])

        with self.assertNumQueries(0):
            self.assertEqual(get_cached_department_summary(), [])

    def test_both_department_summary_routes_share_the_cached_data(self):
        department = Department.objects.create(name="Engineering", code="ENG")
        self.create_employee(department)

        with self.assertNumQueries(1):
            root_response = self.client.get("/reports/department-summary/")

        with self.assertNumQueries(0):
            api_response = self.client.get(
                "/api/v1/reports/department-summary/"
            )

        self.assertEqual(root_response.status_code, 200)
        self.assertEqual(api_response.status_code, 200)
        result = api_response.json()[0]
        self.assertEqual(result["name"], "Engineering")
        self.assertEqual(result["employee_count"], 1)
        self.assertEqual(
            Decimal(result["average_salary"]),
            Decimal("50000.00"),
        )
        self.assertEqual(
            Decimal(result["maximum_salary"]),
            Decimal("50000.00"),
        )

    def test_department_changes_invalidate_after_commit(self):
        self.assertEqual(get_cached_department_summary(), [])

        with self.captureOnCommitCallbacks(execute=True):
            department = Department.objects.create(
                name="Engineering",
                code="ENG",
            )
        self.assertEqual(
            [row["department_name"] for row in get_cached_department_summary()],
            ["Engineering"],
        )

        with self.captureOnCommitCallbacks(execute=True):
            department.name = "Platform"
            department.save()
        self.assertEqual(
            [row["department_name"] for row in get_cached_department_summary()],
            ["Platform"],
        )

        with self.captureOnCommitCallbacks(execute=True):
            department.delete()
        self.assertEqual(get_cached_department_summary(), [])

    def test_employee_update_invalidates_cached_counts(self):
        department = Department.objects.create(name="Engineering", code="ENG")
        employee = self.create_employee(department)
        self.assertEqual(
            get_cached_department_summary()[0]["active_count"],
            1,
        )

        with self.captureOnCommitCallbacks(execute=True):
            employee.is_active = False
            employee.save(update_fields=["is_active"])

        summary = get_cached_department_summary()[0]
        self.assertEqual(summary["active_count"], 0)
        self.assertEqual(summary["inactive_count"], 1)

    def test_employee_create_and_delete_invalidate_cached_counts(self):
        department = Department.objects.create(name="Engineering", code="ENG")
        self.assertEqual(
            get_cached_department_summary()[0]["employee_count"],
            0,
        )

        with self.captureOnCommitCallbacks(execute=True):
            employee = self.create_employee(department)
        self.assertEqual(
            get_cached_department_summary()[0]["employee_count"],
            1,
        )

        with self.captureOnCommitCallbacks(execute=True):
            employee.delete()
        self.assertEqual(
            get_cached_department_summary()[0]["employee_count"],
            0,
        )

    def test_rolled_back_department_creation_keeps_existing_cache(self):
        original = get_cached_department_summary()

        with self.assertRaises(RuntimeError):
            with transaction.atomic():
                Department.objects.create(name="Temporary", code="TMP")
                raise RuntimeError("rollback")

        with self.assertNumQueries(0):
            self.assertEqual(get_cached_department_summary(), original)

    def test_cache_outage_falls_back_to_fresh_database_data(self):
        department = Department.objects.create(name="Engineering", code="ENG")
        self.create_employee(department)

        with self.assertLogs("employees.cache_service", level="ERROR"):
            with (
                patch(
                    "employees.cache_service.cache.get",
                    side_effect=ConnectionError("cache unavailable"),
                ),
                patch(
                    "employees.cache_service.cache.set",
                    side_effect=ConnectionError("cache unavailable"),
                ),
            ):
                result = get_cached_department_summary()

        self.assertEqual(result[0]["employee_count"], 1)
