from .settings import *

# Keep tests independent from a running PostgreSQL server.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Use Django's in-memory cache for isolated tests.
# The normal Redis configuration remains unchanged.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "employee-management-tests",
        "TIMEOUT": 300,
    }
}

# Run Celery tasks synchronously when supported.
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True