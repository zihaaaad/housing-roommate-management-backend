import time
from collections import defaultdict
from typing import Dict, List
from fastapi import Request
from app.core.exceptions import TooManyRequestsException


class InMemoryRateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def check(self, request: Request):
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        timestamps = self.requests[client_ip]
        cutoff_time = current_time - self.window_seconds
        valid_timestamps = [t for t in timestamps if t > cutoff_time]
        if len(valid_timestamps) >= self.max_requests:
            raise TooManyRequestsException(
                f"Rate limit exceeded. Maximum {self.max_requests} requests per {self.window_seconds} seconds."
            )
        valid_timestamps.append(current_time)
        self.requests[client_ip] = valid_timestamps


login_rate_limiter = InMemoryRateLimiter(max_requests=25, window_seconds=60)
register_rate_limiter = InMemoryRateLimiter(max_requests=15, window_seconds=60)
forgot_password_rate_limiter = InMemoryRateLimiter(max_requests=10, window_seconds=60)


def rate_limit_login(request: Request):
    login_rate_limiter.check(request)


def rate_limit_register(request: Request):
    register_rate_limiter.check(request)


def rate_limit_forgot_password(request: Request):
    forgot_password_rate_limiter.check(request)
