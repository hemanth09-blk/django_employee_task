# DB-004 — Query Optimization

## Objective

Identify and optimize inefficient database queries caused by N+1 query problems.

## N+1 Problem

The unoptimized endpoint:

GET /api/v1/employees/details/

loads employees using:

```python
Employee.objects.all()


## N+1 Query Identification

The unoptimized endpoint loads employees using `Employee.objects.all()`.

For each employee, the code then accesses:

- `employee.department`
- `employee.profile`
- `employee.projects`

Because these related objects are loaded separately for each employee, additional database queries are generated.

This creates an N+1 query problem.

### Measured Unoptimized Performance

The endpoint was tested using Postman:

text
GET /api/v1/employees/details/
The unoptimized endpoint returned:

- Query count: 88
- Response time: 270 ms
- HTTP status: 200 OK

The high query count is caused by the N+1 query problem, where
department, profile, and projects are loaded separately for each employee.
## Query Optimization

The query was optimized using Django ORM relationship-loading techniques.

### select_related()

select_related() was used for the ForeignKey and OneToOne relationships:
### prefetch_related()
`prefetch_related()` was used for the ManyToMany relationship between
Employee and Project.

```python
employees = (
    Employee.objects
    .select_related("department", "profile")
    .prefetch_related("projects")
    .all()
    .order_by("employee_code")
)
## Optimized Performance

The optimized endpoint was tested using Postman:

GET /api/v1/employees/details-optimized/

The optimized endpoint returned:

- Query count: 2
- Response time: 125 ms
- HTTP status: 200 OK

## Performance Comparison

| Version | Query Count | Response Time |
|---|---:|---:|
| Unoptimized | 88 | 270 ms |
| Optimized | 2 | 125 ms |

The optimized implementation reduced the number of database queries
from 88 to 2.

The API response remains functionally identical after optimization.

## Optimization Summary

| Relationship | Type | Optimization |
|---|---|---|
| Employee → Department | ForeignKey | select_related() |
| Employee → Profile | OneToOne | select_related() |
| Employee → Projects | ManyToMany | prefetch_related() |

The N+1 query problem was resolved by using appropriate Django ORM
relationship-loading techniques.