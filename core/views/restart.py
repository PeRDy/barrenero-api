import shlex
import subprocess

from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from core.permissions import IsAPISuperuser
from core.serializers import restart, status

__all__ = ['RestartService']


class RestartService(APIView):
    """
    Restart Barrenero's Systemd services.
    """
    permission_classes = (IsAuthenticated, IsAPISuperuser)
    serializer_class = restart.Service

    def post(self, request, format=None):
        """
        Restart a Barrenero's Systemd service giving the name.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        subprocess.run(shlex.split(f'service {serializer.data["name"]} restart'))

        return Response(status.Service({'name': serializer.data['name'], 'status': 'restarted'}).data)
