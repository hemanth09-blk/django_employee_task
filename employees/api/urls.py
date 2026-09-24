from django.urls import include, path

from .routers import router
from . import report_views
from employees.views import (
    employee_details_unoptimized,
    employee_details_optimized,
)    


urlpatterns = [
    # DB-004 Query Optimization
    path(
        "employees/details/",
        employee_details_unoptimized,
        name="employee-details",
    ),

    path(
        "employees/details-optimized/",
        employee_details_optimized,
        name="employee-details-optimized",
    ),

    path(  "",  include(router.urls)),

    path(
        "reports/salary-summary/",
        report_views.salary_summary,
        name="salary-summary",
    ),

    path(
        "reports/department-summary/",
        report_views.department_summary,
        name="department-summary",
    ),

    path(
        "reports/project-summary/",
        report_views.project_summary,
        name="project-summary",
    ),

    path(
        "reports/departments-more-than-5-employees/",
        report_views.departments_with_more_than_5_employees,
        name="departments-more-than-5-employees",
    ),

    path(
        "reports/employees-above-department-average/",
        report_views.employees_above_department_average,
        name="employees-above-department-average",
    ),

    path(
        "reports/projects-more-than-3-employees/",
        report_views.projects_with_more_than_3_employees,
        name="projects-more-than-3-employees",
    ),

    path(
        "reports/employees-with-multiple-projects/",
        report_views.employees_with_multiple_projects,
        name="employees-with-multiple-projects",
    ),

    path(
        "reports/employees-without-projects/",
        report_views.employees_without_projects,
        name="employees-without-projects",
    ),

]    