import datetime
import json
import logging
from collections import deque
from enum import Enum
from typing import List, Dict

from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from core.serializers.ether import status

logger = logging.getLogger(__name__)


class StatusState(Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    UNKNOWN = 'unknown'


class Status(APIView):
    """
    Check Ether miner status info.
    """
    serializer_class = status.Status

    def _status(self) -> str:
        """
        Check Ether miner current status.
        """
        current_time = datetime.datetime.utcnow()
        with open('logs/miner/ether/values.log') as f:
            try:
                logs = deque(f, maxlen=10)
                values = [datetime.datetime.strptime(json.loads(e)['timestamp'], '%Y-%m-%d %H:%M:%S') for e in logs]

                if not values:
                    raise ValueError('No value entries found')

                values.append(current_time)
                deltas = [(x2 - x1).seconds < settings.ETHER_MAX_IDLE for x1, x2 in zip(values[:-1], values[1:])]
                current_status = StatusState.ACTIVE if all(deltas) else StatusState.INACTIVE
            except ValueError:
                current_status = StatusState.INACTIVE
            except Exception:
                logger.exception('Cannot check miner status')
                current_status = StatusState.UNKNOWN

        return current_status.value

    def _hashrate(self) -> List[Dict]:
        """
        Gathers Ether miner hashrate per graphic card.
        :return:
        """
        with open('logs/miner/ether/values.log') as f:
            try:
                log_entries = deque(f, maxlen=50)
                values = [tuple(json.loads(e)['value'].values()) for e in log_entries]
                values_per_gpu = list(zip(*values))
                hashrate = [{'hashrate': sum(v) / len(v), 'graphic_card': i} for i, v in enumerate(values_per_gpu)]
            except:
                hashrate = None

        return hashrate

    def get(self, request, format=None):
        """
        Check Ether miner status info.
        """
        data = {
            'status': self._status(),
            'hashrate': self._hashrate(),
        }

        serializer = self.serializer_class(data)
        return Response(serializer.data)
