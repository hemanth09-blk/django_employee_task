from datetime import date

from django.urls import reverse
from rest_framework.test import APITestCase

from .models import Employee, Department


class EmployeeAPITest(APITestCase):

    def setUp(self):
        # Create Department first because Employee.department
        # is a ForeignKey to Department
        self.department = Department.objects.create(
            name="IT",
            code="IT"
        )

        # Create test employee
        self.employee = Employee.objects.create(
            employee_code="TEST001",
            first_name="Test",
            last_name="Employee",
            email="test@example.com",
            phone="9876543210",
            department=self.department,
            designation="Software Engineer",
            salary=50000,
            joining_date=date.today(),
            is_active=True
        )

    def test_employee_list(self):
        response = self.client.get(
            reverse("employee-list")
        )

        self.assertEqual(response.status_code, 200)

    def test_employee_detail(self):
        response = self.client.get(
            reverse(
                "employee-detail",
                args=[self.employee.id]
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_create_employee(self):
        data = {
            "employee_code": "EMP002",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone": "9876543211",
            "department": self.department.id,
            "designation": "Developer",
            "salary": 60000,
            "joining_date": str(date.today()),
            "is_active": True
        }

        response = self.client.post(
            reverse("employee-list"),
            data=data,
            format="json"
        )

        print("CREATE RESPONSE:", response.status_code, response.data)

        self.assertEqual(response.status_code, 201)

    def test_update_employee(self):
        data = {
            "first_name": "Updated",
            "salary": 65000
        }

        response = self.client.patch(
            reverse(
                "employee-detail",
                args=[self.employee.id]
            ),
            data=data,
            format="json"
        )

        print("UPDATE RESPONSE:", response.status_code, response.data)

        self.assertEqual(response.status_code, 200)

    def test_delete_employee(self):
        response = self.client.delete(
            reverse(
                "employee-detail",
                args=[self.employee.id]
            )
        )

        self.assertEqual(response.status_code, 204)

        self.assertFalse(
            Employee.objects.filter(
                id=self.employee.id
            ).exists()
        )

    def test_duplicate_employee_code(self):
        data = {
            "employee_code": "TEST001",
            "first_name": "Duplicate",
            "last_name": "Employee",
            "email": "duplicate@example.com",
            "phone": "9876543212",
            "department": self.department.id,
            "designation": "Developer",
            "salary": 50000,
            "joining_date": str(date.today()),
            "is_active": True
        }

        response = self.client.post(
            reverse("employee-list"),
            data=data,
            format="json"
        )

        self.assertEqual(response.status_code, 400)

    def test_employee_not_found(self):
        response = self.client.get(
            reverse(
                "employee-detail",
                args=[99999]
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_update_nonexistent_employee(self):
        data = {
            "first_name": "Updated",
            "salary": 65000
        }

        response = self.client.patch(
            reverse(
                "employee-detail",
                args=[99999]
            ),
            data=data,
            format="json"
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_nonexistent_employee(self):
        response = self.client.delete(
            reverse(
                "employee-detail",
                args=[99999]
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_create_employee_with_invalid_data(self):
        data = {
            "employee_code": "",
            "first_name": "Invalid",
            "last_name": "Employee",
            "email": "invalid-email",
            "phone": "123",
            "department": self.department.id,
            "designation": "Developer",
            "salary": -1000,
            "joining_date": str(date.today()),
            "is_active": True
        }

        response = self.client.post(
            reverse("employee-list"),
            data=data,
            format="json"
        )

        self.assertEqual(response.status_code, 400)