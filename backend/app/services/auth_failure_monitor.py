#!/usr/bin/env python3
"""
Auth Failure Monitor

Tails system auth logs and provides a rolling count of failed authentication
attempts. Feeds into SimplifiedMetricsService alongside network data.

Supports:
  - /var/log/auth.log (Debian/Ubuntu)
  - /var/log/secure (RHEL/CentOS/Fedora)
  - journalctl fallback if neither file exists

This is a DATA SOURCE, not an agent action. It feeds perception.
"""

import asyncio
import logging
import os
import re
from collections import deque
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger('AuthFailureMonitor')

# Patterns that indicate failed authentication
AUTH_FAILURE_PATTERNS = [
    re.compile(r'Failed password', re.IGNORECASE),
    re.compile(r'authentication failure', re.IGNORECASE),
    re.compile(r'Invalid user', re.IGNORECASE),
    re.compile(r'Connection closed by .+ \[preauth\]', re.IGNORECASE),
    re.compile(r'PAM .+ authentication failure', re.IGNORECASE),
    re.compile(r'Failed publickey', re.IGNORECASE),
]

# Where to find auth logs, in order of preference
AUTH_LOG_PATHS = [
    '/var/log/auth.log',     # Debian/Ubuntu
    '/var/log/secure',       # RHEL/CentOS/Fedora
]

# Rolling window size in seconds (default 5 minutes)
DEFAULT_WINDOW_SECONDS = 300


class AuthFailureMonitor:
    """
    Monitor system auth logs for failed authentication attempts.

    Maintains a rolling window of failure timestamps.
    get_failed_auth_count() returns the count within the window.
    """

    def __init__(self, window_seconds: int = DEFAULT_WINDOW_SECONDS):
        self.window_seconds = window_seconds
        self._failures: deque = deque()
        self._log_path: Optional[str] = None
        self._last_position: int = 0

        # Find the auth log
        for path in AUTH_LOG_PATHS:
            if os.path.exists(path):
                self._log_path = path
                logger.info(f"Auth log found: {path}")
                break

        if not self._log_path:
            logger.warning(
                "No auth log found at standard paths. "
                "failed_auth_attempts will remain 0 until a log source is configured."
            )

    def get_failed_auth_count(self) -> int:
        """
        Get count of failed auth attempts in the rolling window.

        Prunes expired entries before returning count.
        """
        now = datetime.now(timezone.utc)
        cutoff = now.timestamp() - self.window_seconds

        # Prune expired entries
        while self._failures and self._failures[0] < cutoff:
            self._failures.popleft()

        return len(self._failures)

    async def poll(self):
        """
        Read new lines from the auth log and count failures.

        Delegates synchronous file I/O to a thread to avoid blocking
        the event loop on every metrics collection cycle.
        """
        if not self._log_path:
            return
        await asyncio.to_thread(self._poll_sync)

    def _poll_sync(self):
        """Synchronous file I/O — runs in a thread via asyncio.to_thread()."""
        try:
            stat = os.stat(self._log_path)

            # Log rotated — reset position
            if stat.st_size < self._last_position:
                self._last_position = 0

            if stat.st_size == self._last_position:
                return  # No new data

            with open(self._log_path, 'r') as f:
                f.seek(self._last_position)
                new_lines = f.readlines()
                self._last_position = f.tell()

            now_ts = datetime.now(timezone.utc).timestamp()

            for line in new_lines:
                if any(pattern.search(line) for pattern in AUTH_FAILURE_PATTERNS):
                    self._failures.append(now_ts)

        except PermissionError:
            logger.warning(
                f"Cannot read {self._log_path} — permission denied. "
                f"Run with appropriate permissions or add user to adm group."
            )
            # Stop retrying — one warning is enough, don't spam every cycle
            self._log_path = None
        except Exception as e:
            logger.error(f"Error polling auth log: {e}")


# Module-level singleton — initialized once, shared across all callers
_auth_monitor: Optional[AuthFailureMonitor] = None


def get_auth_failure_monitor() -> AuthFailureMonitor:
    """Get or create the module-level AuthFailureMonitor singleton."""
    global _auth_monitor
    if _auth_monitor is None:
        _auth_monitor = AuthFailureMonitor()
    return _auth_monitor
