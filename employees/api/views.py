from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from ..models import Employee
from .serializers import EmployeeSerializer


# GET all employees
# POST create a new employee
@api_view(["GET", "POST"])
def employee_list(request):

    # GET: Return all employees
    if request.method == "GET":
        employees = Employee.objects.all()
        serializer = EmployeeSerializer(employees, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    # POST: Create a new employee
    if request.method == "POST":
        serializer = EmployeeSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


# GET one employee
# PUT update employee
# PATCH partially update employee
# DELETE employee
@api_view(["GET", "PUT", "PATCH", "DELETE"])
def employee_detail(request, employee_id):

    # Find employee
    try:
        employee = Employee.objects.get(id=employee_id)

    except Employee.DoesNotExist:
        return Response(
            {"detail": "Employee not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    # GET: Return employee details
    if request.method == "GET":
        serializer = EmployeeSerializer(employee)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    # PUT: Update entire employee
    if request.method == "PUT":
        serializer = EmployeeSerializer(
            employee,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    # PATCH: Partially update employee
    if request.method == "PATCH":
        serializer = EmployeeSerializer(
            employee,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    # DELETE: Delete employee
    if request.method == "DELETE":
        employee.delete()

        return Response(
            {"detail": "Employee deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )