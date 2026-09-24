# DB-004 — Database Indexes

## Objective

Evaluate commonly used fields for database indexing and add indexes where they can improve filtering, searching, or ordering performance.

## Index Selection

Indexes were not added blindly. The fields were evaluated based on their usage in employee queries.

### 1. employee_code

employee_code is unique and commonly used for employee lookup and ordering.

Django already creates an index for a unique field, so an additional manual index is not required.

### 2. email

email is unique and can be used to locate an employee.

Django already creates an index for a unique field, so an additional manual index is not required.

### 3. department

Department is commonly used for filtering employees.

A composite index was added together with is_active because employee queries commonly filter using both fields.

### 4. is_active

is_active is commonly used to filter active employees.

It was included in the composite index with department.

### 5. joining_date

joining_date is useful for date-based filtering and reporting.

A separate index was added for this field.

## Implemented Indexes

The following indexes were added:

```python
class Meta:
    indexes = [
        models.Index(fields=["joining_date"]),
        models.Index(fields=["department", "is_active"]),
    ]