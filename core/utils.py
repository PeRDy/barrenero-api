import asyncio
import datetime

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
