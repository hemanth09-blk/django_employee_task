import json
from django.http import JsonResponse
from .models import Employee
def employee_list(request):
    if request.method == "GET":
        employees = Employee.objects.all()
        data = []
        for employee in employees:
            data.append({
                "id": employee.id,
                "employee_code": employee.employee_code,
                "first_name": employee.first_name,
                "last_name": employee.last_name,
                "email": employee.email,
                "phone": employee.phone,
                "department": employee.department,
                "designation": employee.designation,
                "salary": str(employee.salary),
                "joining_date": employee.joining_date,
                "is_active": employee.is_active,
            })
        return JsonResponse(data, safe=False)
    elif request.method == "POST":
     try:
        data = json.loads(request.body)
        required_fields = [
            "employee_code",
            "first_name",
            "last_name",
            "email",
            "designation",
            "salary",
            "joining_date",
        ]
        for field in required_fields:
            if not data.get(field):
                return JsonResponse(
                    {"error": f"{field} is required"},
                    status=400
                )
        if float(data["salary"]) < 0:
            return JsonResponse(
                {"error": "Salary cannot be negative"},
                status=400
            )
        if Employee.objects.filter(
            employee_code=data["employee_code"]
        ).exists():
            return JsonResponse(
                {"error": "Employee code already exists"},
                status=400
            )
        if Employee.objects.filter(
            email=data["email"]
        ).exists():
            return JsonResponse(
                {"error": "Email already exists"},
                status=400
            )
        employee = Employee.objects.create(
            employee_code=data["employee_code"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            phone=data.get("phone", ""),
            department=data.get("department", ""),
            designation=data["designation"],
            salary=data["salary"],
            joining_date=data["joining_date"],
            is_active=data.get("is_active", True),
        )
        return JsonResponse({
            "message": "Employee created successfully",
            "id": employee.id
        }, status=201)
     except ValueError:
        return JsonResponse(
            {"error": "Invalid salary"},
            status=400
        )
     except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON"},
            status=400
        )    
def employee_detail(request, id):
    try:
        employee = Employee.objects.get(id=id)
    except Employee.DoesNotExist:
        return JsonResponse(
            {"error": "Employee not found"},
            status=404
        )
    if request.method == "GET":
        return JsonResponse({
            "id": employee.id,
            "employee_code": employee.employee_code,
            "first_name": employee.first_name,
            "last_name": employee.last_name,
            "email": employee.email,
            "phone": employee.phone,
            "department": employee.department,
            "designation": employee.designation,
            "salary": str(employee.salary),
            "joining_date": employee.joining_date,
            "is_active": employee.is_active,
        })
    elif request.method == "PUT":
        data = json.loads(request.body)
        employee.employee_code = data.get(
            "employee_code", employee.employee_code
        )
        employee.first_name = data.get(
            "first_name", employee.first_name
        )
        employee.last_name = data.get(
            "last_name", employee.last_name
        )
        employee.email = data.get(
            "email", employee.email
        )
        employee.phone = data.get(
            "phone", employee.phone
        )
        employee.department = data.get(
            "department", employee.department
        )
        employee.designation = data.get(
            "designation", employee.designation
        )
        employee.salary = data.get(
            "salary", employee.salary
        )
        employee.joining_date = data.get(
            "joining_date", employee.joining_date
        )
        employee.is_active = data.get(
            "is_active", employee.is_active
        )
        employee.save()
        return JsonResponse({
            "message": "Employee updated successfully"
        })
    elif request.method == "DELETE":
        employee.delete()
        return JsonResponse({
            "message": "Employee deleted successfully"
        })