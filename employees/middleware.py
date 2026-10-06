import logging
import time
import uuid

logger = logging.getLogger(__name__)


class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Use existing request ID if the client provides one.
        # Otherwise generate a new unique ID.
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        request.request_id = request_id

        start_time = time.perf_counter()

        # AuthenticationMiddleware runs before this middleware,
        # so request.user is available.
        if request.user.is_authenticated:
            username = request.user.username
        else:
            username = "anonymous"

        logger.info(
            "Request started | request_id=%s | method=%s | path=%s | user=%s",
            request_id,
            request.method,
            request.path,
            username,
        )

        response = self.get_response(request)

        execution_time = time.perf_counter() - start_time

        logger.info(
            "Request completed | request_id=%s | method=%s | path=%s | "
            "status=%s | execution_time=%.4fs",
            request_id,
            request.method,
            request.path,
            response.status_code,
            execution_time,
        )

        # Send the correlation ID back to the client.
        response["X-Request-ID"] = request_id

        return response