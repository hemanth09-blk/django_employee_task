# SEC-003 — RBAC Permission Matrix

## Roles

### ADMIN
Can manage all employee information and perform all employee operations.

### HR
Can create, view, and update employee information.

### MANAGER
Can view employees within the permitted business scope.

### EMPLOYEE
Can access only their own permitted employee information.

---

## Employee API Permission Matrix

| Operation | ADMIN | HR | MANAGER | EMPLOYEE |
|----------|-------|----|---------|----------|
| View employee list | YES | YES | YES | NO |
| View employee details | YES | YES | YES | NO* |
| Create employee | YES | YES | NO | NO |
| Update employee | YES | YES | NO | NO |
| Delete employee | YES | NO | NO | NO |
| View own profile | YES | YES | YES | YES |
| View another employee | YES | YES | According to scope | NO |

\* Employee access is handled through /api/v1/profile/me/.

---

## Authentication

Unauthenticated users cannot access protected employee APIs.

Expected response:

HTTP 401 Unauthorized