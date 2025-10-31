import time
from typing import Dict, Tuple

from fastapi import Request, HTTPException


class InMemoryRateLimiter:
    def __init__(self, limit_per_minute: int = 100):
        self.limit = limit_per_minute
        self.storage: Dict[str, Tuple[int, int]] = {}

    def check(self, key: str):
        now = int(time.time())
        window = now // 60
        count, win = self.storage.get(key, (0, window))
        if win != window:
            count = 0
            win = window
        count += 1
        self.storage[key] = (count, win)
        if count > self.limit:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")


rate_limiter = InMemoryRateLimiter()


async def rate_limit_dependency(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    rate_limiter.check(client_ip)


