# Cache Strategy and Baseline

## Scope and current behavior

The department summary is the implemented cache target. Both
`/reports/department-summary/` and `/api/v1/reports/department-summary/` use
the same aggregate and cache entry; the API v1 route preserves its existing
response field names. Employee list/detail routes and the other salary/project
reports remain uncached.

The summary contains department names, employee counts, active/inactive counts,
and average/maximum salaries. It is global rather than user-specific, as is the
existing report behavior. Do not put user-specific or permission-filtered data
in this shared entry.

## Cacheability and TTL matrix

| Read | Decision | TTL / freshness | Reason |
|---|---|---|---|
| Department summary (both routes) | Cache | 300 seconds; employee and department saves/deletes invalidate after commit | Aggregate query is shared by both routes; freshness is maintained for normal model writes |
| Employee list | Do not cache | Read current database state | Search, department/status filters, and changing employee data require query-specific keys and broad invalidation |
| Employee detail | Do not cache | Read current database state | Employee data changes frequently and detail can contain user-related data |
| Salary/project and other reports | Do not cache yet | Read current database state | Measure each query first; choose an endpoint-specific key and invalidation rule before caching |

The configured Django cache uses Redis database 1 and the `employee_management`
key prefix. The logical application key is `department_summary:v1`; the
effective key includes the configured prefix. Increment the version when the
cached data shape or meaning changes.

## Invalidation matrix

| Mutation | Invalidation | Boundary/limitation |
|---|---|---|
| Employee create/update/deactivate/delete | Delete `department_summary:v1` after the database transaction commits | Covers model `save()` and `delete()` paths |
| Department create/update/delete | Delete `department_summary:v1` after commit | Affects even departments with zero employees |
| Employee department transfer | Employee save invalidates the shared summary after commit | Both departments are represented by the recomputed aggregate |
| Rolled-back employee/department write | Do not invalidate | Commit hook is discarded on rollback; any pre-existing cached value remains correct |
| `QuerySet.update()`, `bulk_create()`, `bulk_update()`, raw SQL | Not covered by Django model signals | Call `invalidate_department_summary_cache()` after a successful transaction or use model saves |

The 300-second expiry is a safety net if an invalidation path is missed; it is
not the primary freshness mechanism. Redis failures on cache reads/writes are
logged and the summary is computed from the database rather than failing the
request.

## Cache stampede and operational risks

Concurrent requests after expiry or invalidation can all run the aggregate
query. The current summary is one aggregate query, but this can increase
database load during a burst. Measure under representative concurrency before
adding distributed locking; if needed, add a short per-key Redis lock with a
bounded wait and continue to serve database results if lock acquisition fails.
Do not let lock failures turn a cache outage into a failed report.

Invalidation and expiry can cause a miss burst. Redis is a shared dependency
for Celery as well as caching, so cache health and cache latency should be
monitored separately from broker health. Do not flush Redis globally to clear
this entry.

## Reproducible benchmark

Run from the repository root with the project virtual environment and the
configured application database and Redis available:

```powershell
.\.venv\Scripts\python.exe scripts\benchmark_department_cache.py --iterations 30
```

The benchmark warms Django/database startup outside the timed samples, then
measures the same aggregate and serialization logic for uncached queries,
cache misses, and cache hits. Misses and hits use a unique temporary key, so
the production summary entry is not overwritten or cleared. Output is JSON
with average, p50, p95 latency, and average/total database query counts. Save
the output when recording a new environment's baseline.

The checked-in benchmark is a repeatable measurement tool, not a universal
latency guarantee: results depend on database size, machine load, network,
cache backend, and warm/cold database state. Compare runs on the same data and
environment; do not compare the old one-off timings to these measurements.

### Baseline captured 2026-10-23

The benchmark ran 30 iterations per case against PostgreSQL and the configured
`django_redis` cache, with six departments in the summary. These are service
operation measurements (including query-capture instrumentation), not full
HTTP/network latency:

| Case | Average | p50 | p95 | Average DB queries/request |
|---|---:|---:|---:|---:|
| Uncached | 8.003 ms | 7.877 ms | 10.394 ms | 1 |
| Cache miss | 79.684 ms | 12.406 ms | 420.224 ms | 1 |
| Cache hit | 1.689 ms | 1.612 ms | 2.161 ms | 0 |

The cache-miss p95 and average are unusually high compared with its median and
the uncached query, indicating substantial runtime variability during the run.
Do not interpret the mean miss latency as normal cache behavior; investigate
Redis/network and machine load if it repeats. Cache hits removed the aggregate
database query and had lower latency in this sample. This small, single-machine
sample supports the expected query reduction but is not a concurrency or
production capacity test.

## Validation

Run cache behavior tests with the isolated in-memory SQLite and local-memory
cache settings with:

```powershell
.\.venv\Scripts\python.exe manage.py test employees.test_cache --settings=employee_project.settings_test
```

The tests verify a database-backed miss and zero-query hit, both report routes,
empty-result caching, employee/department invalidation, rollback behavior, and
database fallback when cache reads/writes fail.
