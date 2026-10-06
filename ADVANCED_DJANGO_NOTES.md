# Advanced Django Notes

## Employee Audit Logging

Implemented an EmployeeAudit model to maintain an audit trail for employee CREATE and UPDATE operations.

### EmployeeAudit Fields

- employee: ForeignKey to Employee
- action: CREATE or UPDATE
- created_at: Timestamp of the audit event

The employee relationship uses SET_NULL so audit records are retained even if the employee is deleted.

### Signals

A Django post_save signal was implemented for the Employee model.

The signal:
- Creates an audit record when an employee is created.
- Creates an audit record when an employee is updated.
- Logs the employee ID and action.

### Request ID Middleware

Implemented custom middleware to provide request correlation IDs.

The middleware:
- Uses an existing X-Request-ID when supplied by the client.
- Generates a UUID when no request ID is provided.
- Logs request method, path, user, status code and execution time.
- Returns the X-Request-ID in the response.

### Health Check

Added a health-check endpoint:

GET /api/v1/health/

The endpoint returns the service health status.

### Testing

Automated tests were executed successfully.

Result:

10 tests passed successfully.