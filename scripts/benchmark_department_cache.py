import argparse
import json
import math
import os
import statistics
import sys
import time
import uuid
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "employee_project.settings")

import django

django.setup()

from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.test.utils import CaptureQueriesContext

from employees.cache_service import (
    build_department_summary,
    get_cached_department_summary,
)


def measure(operation, iterations):
    durations_ms = []
    query_counts = []

    for _ in range(iterations):
        with CaptureQueriesContext(connection) as queries:
            started = time.perf_counter()
            result = operation()
            durations_ms.append((time.perf_counter() - started) * 1000)
        query_counts.append(len(queries))

    ordered_durations = sorted(durations_ms)

    return {
        "average_ms": round(statistics.mean(durations_ms), 3),
        "p50_ms": round(statistics.median(durations_ms), 3),
        "p95_ms": round(
            ordered_durations[math.ceil(0.95 * iterations) - 1],
            3,
        ),
        "average_database_queries": round(
            statistics.mean(query_counts),
            2,
        ),
        "total_database_queries": sum(query_counts),
        "result_departments": len(result),
    }


def benchmark(iterations):
    cache_key = f"department_summary:benchmark:v1:{uuid.uuid4().hex}"
    cache.set(cache_key, "cache health check", timeout=30)
    if cache.get(cache_key) != "cache health check":
        cache.delete(cache_key)
        raise RuntimeError("The configured cache failed its read/write check")

    try:
        build_department_summary()
        get_cached_department_summary(cache_key)

        uncached = measure(build_department_summary, iterations)

        def measure_cache_miss():
            cache.delete(cache_key)
            return get_cached_department_summary(cache_key)

        cache_miss = measure(measure_cache_miss, iterations)
        get_cached_department_summary(cache_key)
        cache_hit = measure(
            lambda: get_cached_department_summary(cache_key),
            iterations,
        )

        return {
            "endpoint": "/reports/department-summary/",
            "iterations": iterations,
            "database_vendor": connection.vendor,
            "cache_backend": settings.CACHES["default"]["BACKEND"],
            "comparability": (
                "All cases use the same aggregate and serialization logic; "
                "startup warm-up is excluded."
            ),
            "results": {
                "uncached": uncached,
                "cache_miss": cache_miss,
                "cache_hit": cache_hit,
            },
        }
    finally:
        cache.delete(cache_key)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Compare uncached, cache-miss, and cache-hit department "
            "summary latency and database query counts."
        )
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=30,
        help="Number of measured requests per case (default: 30)",
    )
    args = parser.parse_args()
    if args.iterations < 1:
        parser.error("--iterations must be at least 1")

    print(json.dumps(benchmark(args.iterations), indent=2))


if __name__ == "__main__":
    main()
