import requests

url = "http://127.0.0.1:8000/employees/"

employee = {
    "employee_code": "EMP999",
    "first_name": "Test",
    "last_name": "Employee",
    "email": "test.employee@example.com",
    "phone": "9876543210",
    "department": "IT",
    "designation": "Developer",
    "salary": 50000,
    "joining_date": "2026-09-11",
    "is_active": True
}

response = requests.post(url, json=employee)

print("Status Code:", response.status_code)
print("Response:", response.text)