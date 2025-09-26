# polls/middleware.py

import time
from django.utils.deprecation import MiddlewareMixin
from django.utils.timezone import now
from django.http import JsonResponse
from polls.models import Poll
import logging

logger = logging.getLogger("polls.middleware")


class PollsMiddleware(MiddlewareMixin):
    """
    Custom middleware for:
    - Logging requests
    - Adding success/failure messages to responses
    - Restricting number of polls created by a user per day
    """

    def process_request(self, request):
        """Log every request and enforce poll creation limits."""
        request.start_time = time.time()

        user = getattr(request, "user", None)
        print(
            f"[Request] {request.method} {request.path} by {user if user and user.is_authenticated else 'Anonymous'}"
        )

        # ✅ Restrict polls per day (e.g., max 5 per user per day)
        if request.path.startswith("/api/polls/") and request.method == "POST":
            if user and user.is_authenticated:
                today = now().date()
                poll_count = Poll.objects.filter(
                    created_by=user, created_at__date=today
                ).count()
                if poll_count >= 5:  # limit
                    return JsonResponse(
                        {
                            "error": "You have reached the daily poll creation limit (5 polls per day)."
                        },
                        status=403,
                    )

    def process_response(self, request, response):
        """Add success/failure messages depending on API actions."""
        duration = time.time() - getattr(request, "start_time", time.time())
        print(
            f"[Response] {request.method} {request.path} took {duration:.2f}s -> {response.status_code}"
        )

        # Only attach custom messages for specific API endpoints
        if request.path.startswith("/api/polls/") and request.method == "POST":
            if response.status_code == 201:
                response.data = {
                    "message": "Poll created successfully",
                    **response.data,
                }
            else:
                response.data = {
                    "error": "Failed to create poll",
                    **getattr(response, "data", {}),
                }

        elif request.path.startswith("/api/votes/") and request.method == "POST":
            if response.status_code == 201:
                response.data = {"message": "Vote cast successfully", **response.data}
            else:
                response.data = {
                    "error": "Failed to cast vote",
                    **getattr(response, "data", {}),
                }

        elif request.path.startswith("/api/users/") and request.method == "POST":
            if response.status_code == 201:
                response.data = {
                    "message": "User created successfully",
                    **response.data,
                }
            else:
                response.data = {
                    "error": "Failed to create user",
                    **getattr(response, "data", {}),
                }

        return response


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Build curl command
        curl_parts = [f"curl -X '{request.method}' '{request.build_absolute_uri()}'"]

        # Headers
        for header, value in request.headers.items():
            if header.lower() == "cookie":
                continue  # skip cookies (often huge + sensitive)
            curl_parts.append(f"  -H '{header}: {value}'")

        # Body (only for POST/PUT/PATCH)
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = request.body.decode("utf-8")
                if body.strip():
                    curl_parts.append(f"  -d '{body}'")
            except Exception:
                pass

        curl_command = " \\\n  ".join(curl_parts)

        # Log it
        logger.info("[Incoming Request]\n%s", curl_command)

        response = self.get_response(request)

        # Log response info too
        logger.info(
            "[Response] %s %s -> %s", request.method, request.path, response.status_code
        )

        return response
