Celery Deployment and Architecture Notes

1. Architecture

The Employee Management Backend uses Django, Celery, Redis, Celery Beat, and a SQL database.

- Django: Handles API requests and employee business logic.
- Redis broker: Stores queued Celery task messages.
- Celery worker: Executes background tasks asynchronously.
- Celery Beat: Publishes scheduled tasks at configured times.
- SQL database: Stores employee records and related application data.
- Redis cache: Stores cached application data separately from the Celery broker.

Redis Configuration

- Redis database 0: Celery broker and configured result backend.
- Redis database 1: Django application cache.

Both databases use the local Redis service during development.

2. Scheduled Tasks

The following tasks are configured in "CELERY_BEAT_SCHEDULE" in "employee_project/settings.py".

Task| Purpose| Configured time
"employees.tasks.daily_employee_report_task"| Generates the daily employee report| 8:00 AM
"employees.tasks.deactivate_old_employees_task"| Deactivates employees matching the configured inactivity criteria| 1:00 AM

Timezone: "Asia/Kolkata".

These times assume the corresponding "crontab" entries use hours 8 and 1, respectively, with minute 0.

3. Local Startup Order

Run each long-running service in a separate terminal.

1. Start Redis and confirm that it responds to a ping.
2. Activate the Python virtual environment.
3. Start the Celery worker.
4. Start Celery Beat.
5. Start Django when API access is required.

Start the Celery worker

celery -A employee_project worker --loglevel=info --pool=solo

Start Celery Beat

celery -A employee_project beat --loglevel=info

Start Django

python manage.py runserver

The "--pool=solo" option is suitable for local development on Windows.

4. Reliability Configuration

The following reliability settings are configured:

- Late task acknowledgements are enabled.
- Worker-loss rejection is enabled.
- Worker prefetch multiplier is set to 1.
- Soft and hard task execution limits are configured.
- Broker connection retries at startup are enabled.
- Selected tasks use bounded retry and backoff policies.

Tasks must be designed to tolerate retries and possible redelivery. Late acknowledgements do not guarantee exactly-once execution.

5. Health Checks and Monitoring

Worker health

celery -A employee_project inspect ping

Expected response: "pong".

Registered tasks

celery -A employee_project inspect registered

Active queues

celery -A employee_project inspect active_queues

Redis connectivity

python -c "import redis; r=redis.Redis(host='localhost', port=6379, db=0); print(r.ping())"

Expected response: "True".

Review worker logs for task execution, retry attempts, exceptions, and execution duration. Review Beat logs for scheduled task dispatch.

6. Operational Notes

- Run only one Beat scheduler for this schedule to avoid duplicate dispatches.
- Keep the worker and Beat running as separate processes.
- Ensure Redis is available before starting the worker and Beat.
- Use environment variables for configuration and sensitive values.
- Configure process supervision and restart policies for production.
- Use persistent storage and appropriate access controls for production services.
- Test worker restart and broker-outage recovery in a controlled development environment before marking recovery testing complete.

7. Verification Summary

Development checks performed include:

- Django system check passed.
- Celery worker responded to ping.
- Registered tasks were visible.
- Redis broker connectivity passed.
- Redis cache connectivity passed.
- Celery Beat dispatched scheduled tasks.
- Employee report generation succeeded.
- Retry test completed successfully.

Worker restart and broker recovery must be verified separately before being reported as completed.