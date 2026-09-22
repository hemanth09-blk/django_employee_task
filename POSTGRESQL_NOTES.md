# PostgreSQL Notes

## Database Concepts

- Database: employee_management
- Schema: public
- Table: employees_employee
- Row: One employee record
- Column: Employee attributes such as name, email, salary
- Primary Key: id
- Constraints: Unique employee_code and email
- Index: Used to improve query performance

## Django ORM Examples

### Get all employees
Employee.objects.all()

### Get active employees
Employee.objects.filter(is_active=True)

### Filter by department
Employee.objects.filter(department="Backend")

### Order by highest salary
Employee.objects.order_by("-salary")

### Count employees
Employee.objects.count()

## PostgreSQL Integration

Django is configured to use PostgreSQL through environment variables:

- DB_NAME
- DB_USER
- DB_PASSWORD
- DB_HOST
- DB_PORT

The actual .env file is excluded from Git using .gitignore.