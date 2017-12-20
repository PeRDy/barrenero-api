import datetime
import json
import logging
from collections import deque
from functools import partial
from typing import Dict, List

import aiohttp
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from core.serializers.ether import ether
from core.utils import get_event_loop, json_date_hook
from core.views.ether.nanopool import NanopoolMixin

logger = logging.getLogger(__name__)


json_datetime_format = partial(json_date_hook, keys=['timestamp'], date_format='%Y-%m-%d %H:%M:%S')


class Ether(APIView, NanopoolMixin):
    """
    Check Ether miner status info.
    """
    serializer_class = ether.Ether

    def _is_miner_active(self) -> str:
        """
        Check Ether miner current status.
        """
        try:
            with open('logs/miner/ether/values.log') as f:
                logs = deque(f, maxlen=30)
                raw_values = [json.loads(e, object_hook=json_datetime_format) for e in logs]
                values = [(v['timestamp'], v['value']) for v in raw_values if any(v['value'].values())]

                if not values:
                    raise ValueError('No value entries found')

                values.append((datetime.datetime.utcnow(), None))
                deltas = [(x2[0] - x1[0]).seconds < settings.ETHER_MAX_IDLE for x1, x2 in zip(values[:-1], values[1:])]
                current_status = all(deltas)
        except ValueError:
            current_status = False
        except Exception:
            logger.exception('Cannot check miner status')
            current_status = None

        return current_status

    def _hashrate(self) -> List[Dict]:
        """
        Gathers Ether miner hashrate per graphic card.
        :return:
        """
        try:
            with open('logs/miner/ether/values.log') as f:
                log_entries = deque(f, maxlen=30)
                values = [tuple(json.loads(e)['value'].values()) for e in log_entries]
                values_per_gpu = list(zip(*values))
                hashrate = [{'hashrate': sum(v) / len(v), 'graphic_card': i} for i, v in enumerate(values_per_gpu)]
        except:
            hashrate = None

        return hashrate

    def _is_active(self, nanopool: Dict=None):
        """
        Check if the miner is active looking for a recent hashrate entry in local miner and in some pools.

        :param nanopool: Nanopool query result.
        :return: True if miner is active, False if inactive, None if unknown status.
        """
        active = self._is_miner_active()

        if nanopool:
            active = active and float(nanopool.get('workers', {}).get(settings.NANOPOOL['worker'], 0)) > 0

        return active

    async def _get(self, account: str) -> Dict:
        """
        Async wrapper for get method.

        :param account: Account address.
        :return: Nanopool info including balance, hashrate, workers and last payment.
        """
        data = {'hashrate': self._hashrate()}

        async with aiohttp.ClientSession() as session:
            nanopool = await self._nanopool(session, account)

        if nanopool:
            data['nanopool'] = nanopool

        data['active'] = self._is_active(nanopool)

        return data

    def get(self, request, format=None):
        """
        Check Ether miner status info.
        """
        loop = get_event_loop()
        data = loop.run_until_complete(self._get(request.user.account))

        serializer = self.serializer_class(data)
        return Response(serializer.data)
