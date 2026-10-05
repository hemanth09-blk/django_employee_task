from django.contrib.auth.models import Group


ADMIN = "ADMIN"
HR = "HR"
MANAGER = "MANAGER"
EMPLOYEE = "EMPLOYEE"

ROLES = [
    ADMIN,
    HR,
    MANAGER,
    EMPLOYEE,
]


def create_roles():
    """
    Create the RBAC groups if they do not already exist.
    """
    for role in ROLES:
        Group.objects.get_or_create(name=role)