import json
import logging
import shlex
import subprocess
from json import JSONDecodeError

from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from core.serializers.storj import Node

__all__ = ['Storj']

logger = logging.getLogger(__name__)


class Storj(APIView):
    """
    Retrieve Storj nodes status.
    """
    serializer_class = Node

    def _storj_status(self):
        """
        Gathers Storj nodes status.
        """
        command = f'docker exec {settings.STORJ_CONTAINER_NAME} storjshare status -j'
        result = subprocess.run(shlex.split(command), stdout=subprocess.PIPE, universal_newlines=True)
        try:
            return [{
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
            } for node in json.loads(result.stdout)]
        except JSONDecodeError:
            logger.exception("Error retrieving storj status")
            return []

    def get(self, request, format=None):
        """
        Retrieve Storj nodes status.
        """
        status = self._storj_status()

        serializer = self.serializer_class(status, many=True)
        return Response(serializer.data)
