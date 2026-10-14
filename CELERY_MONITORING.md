Celery Monitoring and Health Checks

1. Worker Health

Check that a Celery worker responds:

celery -A employee_project inspect ping

Expected response: "pong".

List registered tasks:

celery -A employee_project inspect registered

Check active tasks:

celery -A employee_project inspect active

Check reserved tasks:

celery -A employee_project inspect reserved

These commands help verify worker availability, registered tasks, running tasks, and tasks reserved for execution.

2. Scheduled Task Monitoring

Start Celery Beat:

celery -A employee_project beat --loglevel=info

Review the logs for:

- "beat: Starting..."
- "Scheduler: Sending due task"

These messages confirm scheduler activity and task dispatch, not successful task completion.

Check that the configured schedule uses the intended timezone and that the worker is running to process dispatched tasks.

3. Queue Depth

For the default Redis list queue, check:

redis-cli LLEN celery

Alternatively, using Python:

python -c "import redis; r=redis.Redis(host='localhost', port=6379, db=0); print('Queue depth:', r.llen('celery'))"

A growing queue can indicate that tasks are arriving faster than workers can process them. Confirm the configured queue name and Redis database before interpreting the result.

Queue depth does not include tasks currently executing or necessarily tasks stored in other queues.

4. Execution Logs

Task logs should record:

- Task name and task ID.
- Task start.
- Successful completion.
- Execution duration.
- Failure details and exceptions.
- Retry attempts, where applicable.

Monitor worker output and configured application log files for failures.

Example log format:

Task started: name=employees.tasks.generate_employee_report id=<task-id>
Task execution: name=employees.tasks.generate_employee_report id=<task-id> status=success duration=0.217s

5. Recovery Checks

- Confirm Redis is available.
- Restart the Celery worker and verify that it reconnects.
- Confirm Celery Beat remains running.
- Submit a test task and verify that the worker processes it.
- Check that failures and retries are visible in the logs.
- Verify that queued tasks are eventually processed.
- Test worker-loss redelivery in a controlled development environment.

A successful ping confirms worker responsiveness but does not prove that every task is healthy.

6. Operational Cautions

- Beat dispatch does not guarantee task completion.
- An empty queue does not prove that no tasks are executing.
- Late acknowledgements and worker-loss rejection do not guarantee exactly-once execution.
- Tasks that may be retried or redelivered should be designed to be idempotent.
- Avoid terminating workers during production tasks unless performing a controlled recovery test.

7. Deployment Topology

The backend uses the following components:

- Django: Provides APIs and business logic.
- Redis database 0: Celery message broker and configured result backend.
- Redis database 1: Django cache.
- Celery worker: Executes background tasks.
- Celery Beat: Dispatches scheduled tasks.
- SQL database: Stores employee and application data.

For deployment, run Django, Redis, the Celery worker, and Celery Beat as separate managed services or containers. Configure persistent storage, environment variables, logging, and restart policies appropriately.

8. Verification Summary

The following checks have been observed during development:

- Worker ping returned "pong".
- Registered tasks were visible.
- Django system checks passed.
- Redis broker and cache connectivity checks returned "True".
- Queue-depth check returned "0".
- The employee report task completed successfully.
- The retry test completed successfully after three retry attempts.

Worker restart and broker-outage recovery should be marked complete only after their behavior has been tested and observed.