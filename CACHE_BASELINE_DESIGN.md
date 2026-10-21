Cache Baseline Design and Performance Measurement

1. Objective

Identify read-heavy API endpoints, establish response-time baselines, and define cache TTL, key naming, invalidation, and data-freshness expectations for the Employee Management System.

The objective is to evaluate caching consistently without claiming performance improvements that have not been demonstrated through comparable measurements.

2. Read-Heavy Endpoints

The following endpoints are candidates for caching:

- Department summary report API
- Employee list API
- Employee detail API

Caching decisions must consider response cost, update frequency, data freshness, pagination, filtering, and user-specific information.

3. Response-Time Baseline

Measure response times using consistent requests and equivalent data under these conditions:

1. Cache disabled: Execute the underlying request without using cached responses.
2. Cache miss: Request the cached endpoint when the required key is absent.
3. Cache hit: Repeat the same request while its cached entry remains valid.

Record HTTP status, response time, database query count where available, and the test conditions.

Initial Benchmark Results

Endpoint| Cache condition| Response time| HTTP status
Department summary| Cache miss| 2.588 seconds| 200
Department summary| Cache hit| 3 ms| 200
Department summary| Uncached ORM endpoint| 114 ms| 200

Observations

- The observed cached endpoint returned in approximately 3 ms on a cache hit.
- The first cached request took approximately 2.588 seconds, including cache-miss processing and storing the result.
- The uncached ORM endpoint returned in approximately 114 ms.

Benchmark limitations

The cached and uncached measurements may use different view implementations or execution paths. The initial cache-miss result may also include database work, initialization, or other request overhead.

These measurements are preliminary observations, not a definitive performance comparison. Repeat the benchmark with equivalent business logic, data, request parameters, and environment. Run multiple iterations and compare average and percentile response times before reporting a performance improvement.

4. TTL Strategy

The existing cache timeout is 300 seconds (5 minutes).

This timeout is a starting point for suitable read-heavy endpoints. Review it according to:

- How frequently the underlying data changes.
- The cost of recomputing the response.
- The acceptable data-staleness window.
- Whether updates trigger reliable invalidation.

Use shorter TTLs for frequently changing data where appropriate. A TTL is a fallback expiry mechanism, not a replacement for invalidation when freshness is required.

5. Cache Key Convention

Use versioned, descriptive cache keys.

Proposed key names:

- "department_summary:v1"
- "employee_list:v1"
- "employee_detail:v1:<employee_id>"

If the response varies by query parameters, include relevant filters, ordering, pagination, and other response-defining inputs in the key. Use a consistent key-building strategy to avoid collisions.

Do not share sensitive or user-specific responses across users. Include an appropriate user or permission scope in the key when caching such responses is justified; otherwise, avoid caching them.

6. Cache Invalidation

Cached responses should be invalidated or refreshed after relevant employee or department changes.

Consider the following operations:

- Employee creation.
- Employee updates and deactivation.
- Employee deletion.
- Department creation or updates.
- Employee department transfers.

Department transfers must account for both the previous and new departments so that neither summary remains stale.

Perform invalidation only after the corresponding database transaction succeeds. Where necessary, use transaction commit hooks to prevent invalidating based on rolled-back changes.

7. Data Freshness and Failure Handling

With a 300-second TTL, cached data may remain stale for up to five minutes unless it is invalidated earlier.

Define acceptable freshness for each endpoint. Sensitive or user-specific responses must not be exposed through shared cache entries.

When Redis is unavailable, cached endpoints should follow the application's intended fallback behavior, such as retrieving fresh data from the database when safe and practical. Log cache failures without exposing sensitive information.

Validate invalidation and fallback behavior through tests before relying on them in production.

8. Validation and Benchmark Procedure

For each endpoint:

1. Use the same data, query parameters, and response logic.
2. Record the uncached response time.
3. Clear or expire the relevant key and measure a cache miss.
4. Repeat the request and measure a cache hit.
5. Run multiple iterations and compare average and percentile response times.
6. Record HTTP status, database query counts, and errors where available.
7. Update a cache entry through the application and verify invalidation.
8. Test the intended behavior when Redis is unavailable.
9. Document the test environment and any limitations.

Do not claim a performance improvement until comparable measurements support it.

9. Current Status

- Read-heavy endpoint candidates identified.
- Initial department-summary measurements recorded.
- A 300-second TTL identified for review.
- Versioned cache-key conventions proposed.
- Invalidation and data-freshness requirements documented.
- Equivalent repeated benchmarks, invalidation tests, and Redis-fallback tests still require verification.

The initial measurements are preliminary and should not be treated as a final performance conclusion.