import json
import logging
import shlex
import subprocess
from json import JSONDecodeError

import aiohttp
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from core.serializers.storj import Node
from core.utils import retry, get_event_loop

__all__ = ['Storj']

logger = logging.getLogger(__name__)


class Storj(APIView):
    """
    Retrieve Storj nodes status.
    """
    serializer_class = Node

    @retry(3, {})
    async def _storj_api_status(self, session: 'aiohttp.ClientSession', node_id: str):
        url = f'{settings.STORJ_API["url"]}contacts/{node_id}/'
        async with session.get(url) as response:
            try:
                response.raise_for_status()

                storj_api_response = await response.json()
            except aiohttp.ClientResponseError:
                storj_api_response = None

        return storj_api_response

    async def _storj_status(self, session: 'aiohttp.ClientSession'):
        """
        Gathers Storj nodes status.
        """
        command = f'docker exec {settings.STORJ_CONTAINER_NAME} storjshare status -j'
        result = subprocess.run(shlex.split(command), stdout=subprocess.PIPE, universal_newlines=True)
        try:
            for node in json.loads(result.stdout):
                storj_api = await self._storj_api_status(session, node['id'])
                yield {
                    'id': node['id'],
                    'status': node['status'],
                    'config_path': node['configPath'],
                    'uptime': node['uptime'],
                    'restarts': node['restarts'],
                    'peers': node['peers'],
                    'allocs': node['allocs'],
                    'data_received': node['dataReceivedCount'] if node['dataReceivedCount'] != '...' else None,
                    'delta': node['delta'][:-2] if node['delta'] != '...' else None,
                    'port': node['port'],
                    'shared': node['shared'] if node['shared'] != '...' else None,
                    'shared_percent': node['sharedPercent'] if node['sharedPercent'] != '...' else None,
                    'response_time': storj_api.get('responseTime', None),
                    'reputation': storj_api.get('reputation', None),
                    'version': storj_api.get('userAgent', None)
                }
        except JSONDecodeError:
            logger.exception("Error retrieving storj status")

    async def _get(self):
        """
        Retrieve Storj nodes status.
        """
        async with aiohttp.ClientSession() as session:
            status = [i async for i in self._storj_status(session)]

        return status

    def get(self, request, format=None):
        """
        Check Ether miner status info.
        """
        loop = get_event_loop()
        data = loop.run_until_complete(self._get())

        serializer = self.serializer_class(data, many=True)
        return Response(serializer.data)
