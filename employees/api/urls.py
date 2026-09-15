from django.urls import path

from .views import employee_list, employee_detail

urlpatterns = [
    path("employees/", employee_list, name="employee-list"),
    path(
        "employees/<int:employee_id>/",
        employee_detail,
        name="employee-detail",
    ),
]