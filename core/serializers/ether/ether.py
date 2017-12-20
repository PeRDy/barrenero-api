from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from core.serializers.ether.nanopool import Nanopool


class Hashrate(serializers.Serializer):
    graphic_card = serializers.IntegerField(label=_('Graphic card'))
    hashrate = serializers.FloatField(label=_('Hashrate'))


class Ether(serializers.Serializer):
    active = serializers.NullBooleanField(label=_('Is active'))
    nanopool = Nanopool(required=False, label=_('Nanopool info'))
    hashrate = serializers.ListSerializer(child=Hashrate(), label=_('Hashrate per graphic'))
