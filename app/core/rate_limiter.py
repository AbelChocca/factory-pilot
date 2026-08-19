from collections import defaultdict
from datetime import datetime, timedelta, timezone
from threading import Lock

from fastapi import HTTPException, Request
from app.core.pydantic_settings import settings

class RateLimiter:
    def __init__(
        self,
        max_requests: int,
        window: timedelta,
    ):
        self.max_requests = max_requests
        self.window = window

        self._requests: dict[str, list[datetime]] = defaultdict(list)
        self._lock = Lock()

    async def __call__(
        self,
        request: Request,
    ) -> None:

        if settings.ENV == "development":
            return

        # Temporary identifier.
        # Replace with authenticated user ID when available.
        client_id = request.client.host

        now = datetime.now(timezone.utc)
        window_start = now - self.window

        with self._lock:
            requests = self._requests[client_id]

            requests[:] = [
                timestamp
                for timestamp in requests
                if timestamp > window_start
            ]

            if len(requests) >= self.max_requests:
                raise HTTPException(
                    status_code=429,
                    detail=(
                        "AI usage limit reached. "
                        "You can make up to "
                        f"{self.max_requests} requests per "
                        f"{self.window.days} days."
                    ),
                )

            requests.append(now)

ai_rate_limit = RateLimiter(
    max_requests=6,
    window=timedelta(days=7),
)