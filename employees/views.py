import json
import logging

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Employee


logger = logging.getLogger(__name__)


def employee_to_dict(employee):
    """Convert Employee object to dictionary."""
    return {
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
    }


@csrf_exempt
def employee_list(request):
    """
    GET  - List employees
    POST - Create employee
    """

    # GET - List employees
    if request.method == "GET":
        employees = Employee.objects.all().order_by("employee_code")

        # Search
        search = request.GET.get("search")
        if search:
            employees = employees.filter(
                first_name__icontains=search
            ) | employees.filter(
                last_name__icontains=search
            ) | employees.filter(
                employee_code__icontains=search
            ) | employees.filter(
                email__icontains=search
            )

        # Filter by department
        department = request.GET.get("department")
        if department:
            employees = employees.filter(department__iexact=department)

        # Filter by active status
        is_active = request.GET.get("is_active")
        if is_active is not None:
            if is_active.lower() == "true":
                employees = employees.filter(is_active=True)
            elif is_active.lower() == "false":
                employees = employees.filter(is_active=False)

        data = [employee_to_dict(employee) for employee in employees]

        logger.info("Employee list retrieved successfully")

        return JsonResponse(data, safe=False, status=200)

    # POST - Create employee
    elif request.method == "POST":
        try:
            data = json.loads(request.body)

            employee = Employee.objects.create(
                employee_code=data["employee_code"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                email=data["email"],
                phone=data.get("phone", ""),
                department=data["department"],
                designation=data["designation"],
                salary=data["salary"],
                joining_date=data["joining_date"],
                is_active=data.get("is_active", True),
            )

            logger.info(
                "Employee created successfully: %s",
                employee.employee_code,
            )

            return JsonResponse(
                {
                    "message": "Employee created successfully",
                    "id": employee.id,
                },
                status=201,
            )

        except json.JSONDecodeError:
            logger.warning("Invalid JSON received while creating employee")

            return JsonResponse(
                {"error": "Invalid JSON data"},
                status=400,
            )

        except KeyError as error:
            logger.warning(
                "Missing employee field: %s",
                error,
            )

            return JsonResponse(
                {
                    "error": f"Missing required field: {error.args[0]}"
                },
                status=400,
            )

        except (IntegrityError, ValidationError):
            logger.warning(
                "Employee creation failed due to invalid data"
            )

            return JsonResponse(
                {"error": "Invalid employee data or duplicate employee"},
                status=400,
            )

    return JsonResponse(
        {"error": "Method not allowed"},
        status=405,
    )


@csrf_exempt
def employee_detail(request, id):
    """
    GET    - View employee
    PUT    - Update employee
    DELETE - Delete employee
    """

    # Find employee
    try:
        employee = Employee.objects.get(id=id)

    except Employee.DoesNotExist:
        logger.warning("Employee not found: %s", id)

        return JsonResponse(
            {"error": "Employee not found"},
            status=404,
        )

    # GET - View employee
    if request.method == "GET":
        logger.info("Employee retrieved successfully: %s", id)

        return JsonResponse(
            employee_to_dict(employee),
            status=200,
        )

    # PUT - Update employee
    elif request.method == "PUT":
        try:
            data = json.loads(request.body)

            employee.employee_code = data.get(
                "employee_code",
                employee.employee_code,
            )

            employee.first_name = data.get(
                "first_name",
                employee.first_name,
            )

            employee.last_name = data.get(
                "last_name",
                employee.last_name,
            )

            employee.email = data.get(
                "email",
                employee.email,
            )

            employee.phone = data.get(
                "phone",
                employee.phone,
            )

            employee.department = data.get(
                "department",
                employee.department,
            )

            employee.designation = data.get(
                "designation",
                employee.designation,
            )

            employee.salary = data.get(
                "salary",
                employee.salary,
            )

            employee.joining_date = data.get(
                "joining_date",
                employee.joining_date,
            )

            employee.is_active = data.get(
                "is_active",
                employee.is_active,
            )

            employee.full_clean()
            employee.save()

            logger.info("Employee updated successfully: %s", id)

            return JsonResponse(
                {
                    "message": "Employee updated successfully",
                    "id": employee.id,
                },
                status=200,
            )

        except json.JSONDecodeError:
            logger.warning(
                "Invalid JSON received while updating employee: %s",
                id,
            )

            return JsonResponse(
                {"error": "Invalid JSON data"},
                status=400,
            )

        except (ValidationError, IntegrityError) as error:
            logger.warning(
                "Employee update failed: %s",
                error,
            )

            return JsonResponse(
                {"error": "Invalid employee data"},
                status=400,
            )

    # DELETE - Delete employee
    elif request.method == "DELETE":
        employee.delete()

        logger.info("Employee deleted successfully: %s", id)

        return JsonResponse(
            {"message": "Employee deleted successfully"},
            status=200,
        )

    return JsonResponse(
        {"error": "Method not allowed"},
        status=405,
    )