from django.test import TestCase
from django.urls import reverse


class EmployeeAPITest(TestCase):

    def test_employee_list(self):
        response = self.client.get(reverse("employee-list"))
        self.assertEqual(response.status_code, 200)

    def test_valid_employee_detail(self):
        response = self.client.get(reverse("employee-detail", args=[1]))
        self.assertEqual(response.status_code, 200)

    def test_invalid_employee_detail(self):
        response = self.client.get(reverse("employee-detail", args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_invalid_url(self):
        response = self.client.get("/api/anything/")
        self.assertEqual(response.status_code, 404)