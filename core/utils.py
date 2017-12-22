import asyncio
import datetime
from functools import wraps

from typing import List, Dict


def get_event_loop():
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop


def json_date_hook(obj: Dict, keys: List[str], date_format: str='%Y-%m-%d %H:%M:%S'):
    for k in (k for k in keys if k in obj):
        obj[k] = datetime.datetime.strptime(obj[k], date_format)

    return obj


def retry(max_retries, default=None):
    def outer(f):
        @wraps(f)
        async def inner(*args, **kwargs):
            retries = max_retries
            result = None
            while result is None and retries > 0:
                result = await f(*args, **kwargs)
                retries -= 1

            if result is None:
                result = default

            return result
        return inner
    return outer
