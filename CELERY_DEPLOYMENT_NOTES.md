Celery Deployment and Architecture Notes

1. Architecture

The Employee Management Backend uses Django, Celery, Redis, Celery Beat, and a SQL database.

- Django: Handles API requests and application business logic.
- Redis broker: Stores queued Celery task messages.
- Celery worker: Executes background tasks asynchronously.
- Celery Beat: Publishes scheduled tasks according to their configured schedules.
- SQL database: Stores employee records and related application data.
- Redis cache: Stores cached application data separately from task messages.

Redis Configuration

The local Redis service uses separate logical databases:

- Database 0: Celery message broker.
- Database 1: Django application cache.
- Database 2: Celery task result backend.

These databases are logical partitions within the same Redis service, not separate Redis servers.

2. Celery Configuration

Celery is initialized in "employee_project/celery.py".

The application loads its configuration from Django settings using the "CELERY_" namespace and automatically discovers tasks in installed Django applications.

Important configuration values:

- Broker URL: "redis://127.0.0.1:6379/0"
- Result backend: "redis://127.0.0.1:6379/2"
- Timezone: "Asia/Kolkata"
- UTC support: Enabled
- Task started tracking: Enabled
- Late acknowledgements: Enabled
- Reject tasks on worker loss: Enabled
- Worker prefetch multiplier: "1"
- Soft task time limit: "240" seconds
- Hard task time limit: "300" seconds

Broker connection retry settings should also be checked in "employee_project/settings.py" before deployment.

3. Scheduled Tasks

The following tasks are configured in "CELERY_BEAT_SCHEDULE" in "employee_project/settings.py".

Task| Purpose| Schedule
"employees.tasks.daily_employee_report_task"| Generates the daily employee report| Every day at 8:00 AM
"employees.tasks.deactivate_old_employees_task"| Deactivates employees matching the configured inactivity criteria| Every day at 1:00 AM

Timezone: "Asia/Kolkata".

The schedules use "crontab(hour=8, minute=0)" and "crontab(hour=1, minute=0)", respectively.

Only one Celery Beat scheduler should run for this schedule to avoid duplicate dispatches.

4. Local Development Startup

Run Redis, the Celery worker, Celery Beat, and Django in separate terminals as needed.

Step 1: Start Redis

Ensure the local Redis service is running.

Check connectivity:

python -c "import redis; r=redis.Redis(host='127.0.0.1', port=6379, db=0); print(r.ping())"

Expected output:

True

Step 2: Activate the Python virtual environment

In PowerShell, from the project root:

.\.venv\Scripts\Activate.ps1

If execution policy prevents activation, use the project's approved PowerShell activation procedure.

Step 3: Start the Celery worker

celery -A employee_project worker -l info --pool=solo

Wait until the worker reports that it is connected to Redis and ready.

The "--pool=solo" option is appropriate for local development on Windows.

Step 4: Start Celery Beat

Open another terminal and activate the same virtual environment:

celery -A employee_project beat -l info

Keep the Beat process running to publish scheduled tasks.

Step 5: Start Django when API access is required

Open another terminal:

python manage.py runserver

5. Health Checks and Monitoring

Run these commands from an activated virtual environment.

Check worker availability

celery -A employee_project inspect ping

Expected response from a reachable worker: "pong".

List registered tasks

celery -A employee_project inspect registered

Confirm that the expected employee and recovery-test tasks appear.

Inspect active queues

celery -A employee_project inspect active_queues

Check Redis broker connectivity

python -c "import redis; r=redis.Redis(host='127.0.0.1', port=6379, db=0); print(r.ping())"

Check Redis cache connectivity

python -c "import redis; r=redis.Redis(host='127.0.0.1', port=6379, db=1); print(r.ping())"

Monitor logs

Review the worker logs for:

- Task received and completed messages.
- Task execution status and duration.
- Retry attempts and final failures.
- Exceptions and connection errors.
- Duplicate submissions and task IDs.

Review Beat logs for scheduler startup and scheduled-task dispatch.

6. Reliability and Recovery Design

Late acknowledgements

Late acknowledgements allow a task to be acknowledged after execution rather than immediately upon receipt. This can support redelivery after worker loss, depending on the broker and Celery configuration.

Worker-loss rejection

The worker-recovery test task uses:

acks_late=True
reject_on_worker_lost=True

These settings support testing redelivery after unexpected worker loss. They do not guarantee exactly-once execution.

Retry policy

Selected tasks use bounded retries and retry delays. Retry policies should be limited to transient failures and must avoid infinite retry loops.

Idempotency

Tasks that create records, send emails, or perform other side effects should be designed to tolerate duplicate delivery. Use appropriate unique identifiers, database constraints, transaction handling, or deduplication records where required.

Broker recovery

The worker and Beat depend on Redis for message delivery. Broker-outage recovery must be tested in a controlled environment, including reconnect behavior and the handling of queued or in-flight messages.

7. Recovery Demo Verification Results

Verified

- Celery worker connected to Redis and became ready.
- Expected Celery tasks appeared in the worker's registered task list.
- The worker-recovery test task completed successfully during normal operation.
- The retry demonstration task retried twice and reached its intentional final failure.
- The same marker was submitted twice with different task IDs, and both executions succeeded.
- Celery Beat started and published both configured scheduled tasks.
- The inactive employee maintenance task completed successfully; zero employees matched its deactivation criteria during the observed run.
- The daily employee report task completed successfully and generated a report for 34 employees.
- Task logs recorded execution status and duration.

Still requiring verification

- Actual worker-process loss followed by confirmed task redelivery.
- Redis broker interruption followed by confirmed recovery.
- Idempotency protection against duplicate side effects.
- Quantitative comparison with the original performance baseline.
- Final rollback procedure validation.

Do not mark these pending checks as passed until their results have been recorded.

8. Performance Baseline and Comparison

Record measurements with the same endpoint, test data, request volume, and environment.

Metric| Cache disabled / baseline| Cache enabled / after change
Average response time| Record measured value| Record measured value
P95 response time| Record measured value| Record measured value
Database query count| Record measured value| Record measured value
Cache hit/miss observations| Not applicable or record observed value| Record measured value

Do not invent or estimate benchmark results. Record actual measurements and note the test conditions.

For cached endpoints, verify that writes invalidate or refresh affected cache entries and that Redis unavailability follows the intended fallback behavior.

9. Rollback Procedure

Use the following controlled rollback process if a cache or Celery change causes problems.

1. Stop Celery Beat to prevent additional scheduled dispatches.
2. Stop the Celery worker gracefully after considering tasks currently in progress.
3. Revert the relevant application changes to the last known-good Git revision.
4. Restore the previous cache settings and invalidation behavior if the cache change caused the issue.
5. Restart Redis if it is the source of the failure, after checking service health and data-persistence requirements.
6. Restart the worker and Beat using the last known-good configuration.
7. Run Django system checks and the applicable automated tests.
8. Verify worker health, Redis connectivity, scheduled-task behavior, and affected API endpoints.
9. Record the reason for rollback and the verification results.

Do not flush Redis databases as a routine rollback step; doing so may remove queued tasks, cached data, or task results.

10. Production Considerations

- Keep secrets and environment-specific URLs in environment variables.
- Run one Beat scheduler per schedule unless a coordinated high-availability design is used.
- Configure process supervision and restart policies.
- Monitor worker health, queue depth, retry counts, task duration, and final failures.
- Apply Redis access controls and suitable network restrictions.
- Configure persistence and recovery according to operational requirements.
- Use task timeouts, bounded retries, and idempotent task design.
- Test worker and broker failure scenarios before production deployment.
- Document rollback steps and retain useful operational logs.

11. Final Status

The local development checks have confirmed worker startup, Redis connectivity, retry/final-failure behavior, duplicate submissions, and successful execution of the two scheduled tasks.

The recovery demo is partially verified. Actual worker-loss redelivery, broker-outage recovery, measured baseline comparison, idempotency safeguards, and rollback validation remain outstanding until supported by test evidence.