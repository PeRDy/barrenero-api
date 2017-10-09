import logging
import shlex
import subprocess

from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsAPISuperuser
from core.serializers import status

logger = logging.getLogger(__name__)

__all__ = ['Status']


class Status(APIView):
    """
    Retrieve graphic cards and systemd services status.
    """
    permission_classes = (IsAuthenticated, IsAPISuperuser)
    serializer_class = status.Status

    def _graphics_status(self):
        """
        Gathers graphic cards status.
        """
        try:
            cmd = 'nvidia-smi ' \
                  '--query-gpu=index,power.draw,fan.speed,utilization.gpu,utilization.memory,clocks.gr,clocks.mem ' \
                  '--format=csv'
            process = subprocess.run(shlex.split(cmd), stdout=subprocess.PIPE, universal_newlines=True)
            graphics_keys = ('id', 'power', 'fan', 'gpu_usage', 'mem_usage', 'gpu_clock', 'mem_clock')
            graphics_stats = [[j.split()[0] for j in i.split(', ')] for i in process.stdout.strip().split('\n')[1:]]
            result = [{k: v for k, v in zip(graphics_keys, values)} for values in graphics_stats]
        except FileNotFoundError:
            result = None
        except Exception:
            logger.exception('Cannot get graphics status')
            result = None

        return result

    def _services_status(self):
        """
        Gathers systemd services status.
        """
        services = []
        for service_name, service in settings.SYSTEMD_SERVICES.items():
            status = subprocess.run(shlex.split(f'systemctl is-active {service}'), stdout=subprocess.PIPE,
                                    universal_newlines=True).stdout.strip()
            services.append({'name': service_name, 'status': status})

        return services

    def get(self, request, format=None):
        """
        Retrieve graphic cards and systemd services status.
        """
        data = {
            'graphics': self._graphics_status(),
            'services': self._services_status(),
        }

        serializer = self.serializer_class(data)
        return Response(serializer.data)
