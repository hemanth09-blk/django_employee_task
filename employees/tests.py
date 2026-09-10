from datetime import date
from django.test import TestCase
from django.urls import reverse
from .models import Employee
class EmployeeAPITest(TestCase):
    def setUp(self):
        self.employee = Employee.objects.create(
            employee_code="TEST001",
            first_name="Test",
            last_name="Employee",
            email="test@example.com",
            phone="9876543210",
            department="IT",
            designation="Software Engineer",
            salary=50000,
            joining_date=date.today(),
            is_active=True,
        )
    def test_employee_list(self):
        response = self.client.get(reverse("employee-list"))
        self.assertEqual(response.status_code, 200)
    def test_valid_employee_detail(self):
        response = self.client.get(
            reverse("employee-detail", args=[self.employee.id])
        )
        self.assertEqual(response.status_code, 200)
    def test_invalid_employee_detail(self):
        response = self.client.get(
            reverse("employee-detail", args=[9999])
        )
        self.assertEqual(response.status_code, 404)
    def test_invalid_url(self):
        response = self.client.get("/api/anything/")
        self.assertEqual(response.status_code, 404)
    def test_create_employee(self):
        data = {
            "employee_code": "EMP002",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone": "9876543211",
            "department": "IT",
            "designation": "Developer",
            "salary": 60000,
            "joining_date": str(date.today()),
            "is_active": True,
        }
        response = self.client.post(
            reverse("employee-list"),
            data=data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
    def test_update_employee(self):
        data = {
            "first_name": "Updated",
            "salary": 65000
        }
        response = self.client.put(
            reverse("employee-detail", args=[self.employee.id]),
            data=data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
    def test_delete_employee(self):
        response = self.client.delete(
            reverse("employee-detail", args=[self.employee.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Employee.objects.filter(id=self.employee.id).exists()
        )    
    def test_missing_email(self):
        response = self.client.post(
            reverse("employee-list"),
            data={
                "employee_code": "TEST002",
                "first_name": "Missing",
                "last_name": "Email",
                "designation": "Developer",
                "salary": 50000,
                "joining_date": str(date.today()),
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
    def test_duplicate_employee_code(self):
        response = self.client.post(
            reverse("employee-list"),
            data={
                "employee_code": "TEST001",
                "first_name": "Duplicate",
                "last_name": "Employee",
                "email": "duplicate@example.com",
                "designation": "Developer",
                "salary": 50000,
                "joining_date": str(date.today()),
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
    def test_invalid_salary(self):
        response = self.client.post(
            reverse("employee-list"),
            data={
                "employee_code": "TEST003",
                "first_name": "Invalid",
                "last_name": "Salary",
                "email": "invalidsalary@example.com",
                "designation": "Developer",
                "salary": -5000,
                "joining_date": str(date.today()),
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)    