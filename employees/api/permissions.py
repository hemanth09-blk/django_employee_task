from rest_framework.permissions import BasePermission


# =====================================================
# SEC-003: Individual Role Permissions
# =====================================================

class IsAdmin(BasePermission):
    """
    Allows access only to users in the ADMIN role.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.groups.filter(
                name="ADMIN"
            ).exists()
        )


class IsHR(BasePermission):
    """
    Allows access only to users in the HR role.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.groups.filter(
                name="HR"
            ).exists()
        )


class IsManager(BasePermission):
    """
    Allows access only to users in the MANAGER role.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.groups.filter(
                name="MANAGER"
            ).exists()
        )


class IsEmployee(BasePermission):
    """
    Allows access only to users in the EMPLOYEE role.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.groups.filter(
                name="EMPLOYEE"
            ).exists()
        )


# =====================================================
# SEC-003: Combined Role Permissions
# =====================================================

class IsAdminOrHR(BasePermission):
    """
    Allows ADMIN or HR users.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.groups.filter(
                name__in=["ADMIN", "HR"]
            ).exists()
        )


class IsAdminOrHROrManager(BasePermission):
    """
    Allows ADMIN, HR, or MANAGER users.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.groups.filter(
                name__in=[
                    "ADMIN",
                    "HR",
                    "MANAGER",
                ]
            ).exists()
        )


class IsAdminOrHROrManagerOrEmployee(BasePermission):
    """
    Allows ADMIN, HR, MANAGER, or EMPLOYEE users.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.groups.filter(
                name__in=[
                    "ADMIN",
                    "HR",
                    "MANAGER",
                    "EMPLOYEE",
                ]
            ).exists()
        )