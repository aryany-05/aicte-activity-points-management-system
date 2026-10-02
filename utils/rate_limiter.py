"""
utils/rate_limiter.py - Lightweight In-Memory Rate Limiter
AICTE Activity & Points Management System

Provides simple IP-based rate limiting for authentication endpoints
to protect against brute-force attacks without requiring external infrastructure.
"""

import time
from collections import defaultdict
from threading import Lock


class InMemoryRateLimiter:
    """
    Thread-safe in-memory rate limiter using a sliding time window.
    Designed for small college projects and local development.
    """

    def __init__(self, max_attempts=5, window_seconds=300):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self._attempts = defaultdict(list)
        self._lock = Lock()

    def _cleanup_old_attempts(self, now, key):
        """Remove timestamps older than the configured window."""
        cutoff = now - self.window_seconds
        self._attempts[key] = [ts for ts in self._attempts[key] if ts > cutoff]
        if not self._attempts[key]:
            del self._attempts[key]

    def is_rate_limited(self, key):
        """
        Check if a given key has exceeded the maximum allowed attempts.
        Returns:
            (is_limited: bool, retry_after_seconds: int)
        """
        now = time.time()
        with self._lock:
            self._cleanup_old_attempts(now, key)
            attempts = self._attempts.get(key, [])
            if len(attempts) >= self.max_attempts:
                oldest = attempts[0]
                retry_after = max(1, int(self.window_seconds - (now - oldest)))
                return True, retry_after
            return False, 0

    def record_failure(self, key):
        """Record a failed attempt."""
        now = time.time()
        with self._lock:
            self._cleanup_old_attempts(now, key)
            self._attempts[key].append(now)

    def record_success(self, key):
        """Reset attempts on successful authentication."""
        with self._lock:
            if key in self._attempts:
                del self._attempts[key]


# Singleton instance for login rate limiting: 5 failed attempts per 5 minutes
login_limiter = InMemoryRateLimiter(max_attempts=5, window_seconds=300)


def get_client_ip(request):
    """Safely determine the client IP address from the request."""
    if request.headers.get('X-Forwarded-For'):
        # Take the first IP if behind a proxy
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr or '127.0.0.1'
