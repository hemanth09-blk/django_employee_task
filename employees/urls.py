from django.urls import path
from . import views


urlpatterns = [
    # Employee APIs
    path(
        "employees/",
        views.employee_list,
        name="employee-list",
    ),
    path(
        "employees/<int:id>/",
        views.employee_detail,
        name="employee-detail",
    ),

    # DB-003 Reporting APIs
    path(
        "reports/department-summary/",
        views.department_summary,
        name="department-summary",
    ),
    path(
        "reports/project-summary/",
        views.project_summary,
        name="project-summary",
    ),
    path(
        "reports/salary-summary/",
        views.salary_summary,
        name="salary-summary",
    ),

]    