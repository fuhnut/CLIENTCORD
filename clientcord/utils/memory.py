import psutil
import os

def get_ram_usage_mb() -> int:
    try:
        process = psutil.Process(os.getpid())
        return process.memory_info().rss // (1024 * 1024)
    except Exception:
        return 0
