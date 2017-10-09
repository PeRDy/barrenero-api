from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class Service(serializers.Serializer):
    name = serializers.CharField(label=_('Name'))

    def validate_name(self, value):
        if value in settings.SYSTEMD_SERVICES:
            return settings.SYSTEMD_SERVICES[value]
        elif value in settings.SYSTEMD_SERVICES.values():
            return value
        else:
            raise ValidationError(_('Unknown service'))
