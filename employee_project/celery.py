import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "employee_project.settings")

app = Celery("employee_project")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.timezone = "Asia/Kolkata"
app.conf.enable_utc = True

app.autodiscover_tasks()