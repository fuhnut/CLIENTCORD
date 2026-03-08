import asyncio
import time

class RateLimiter:
    def __init__(self) -> None:
        self.buckets: dict[str, dict] = {}
        self.global_lock = asyncio.Lock()
        self.global_reset = 0.0

    async def acquire(self, bucket: str) -> None:
        async with self.global_lock:
            now = time.time()
            if self.global_reset > now:
                await asyncio.sleep(self.global_reset - now)
        
        if bucket not in self.buckets:
            self.buckets[bucket] = {"lock": asyncio.Lock(), "remaining": 1, "reset": 0.0}
            
        b = self.buckets[bucket]
        async with b["lock"]:
            now = time.time()
            if b["remaining"] <= 0 and b["reset"] > now:
                await asyncio.sleep(b["reset"] - now)

    def update(self, bucket: str, remaining: int, reset: float, is_global: bool = False, retry_after: float = 0.0) -> None:
        if is_global:
            self.global_reset = time.time() + retry_after
        elif bucket in self.buckets:
            self.buckets[bucket]["remaining"] = remaining
            self.buckets[bucket]["reset"] = reset
