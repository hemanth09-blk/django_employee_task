from django.http import JsonResponse


employees = [
    {
        "id": 1,
        "name": "Divya",
        "department": "Backend",
        "designation": "Python Developer",
    },
    {
        "id": 2,
        "name": "Rahul",
        "department": "Frontend",
        "designation": "React Developer",
    },
    {
        "id": 3,
        "name": "Priya",
        "department": "Testing",
        "designation": "QA Engineer",
    },
]


def employee_list(request):
    return JsonResponse(employees, safe=False)


def employee_detail(request, id):
    for employee in employees:
        if employee["id"] == id:
            return JsonResponse(employee)

    return JsonResponse(
        {"error": "Employee not found"},
        status=404,
    )

# Create your views here.
