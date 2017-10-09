from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class Hashrate(serializers.Serializer):
    graphic_card = serializers.IntegerField(label=_('Graphic card'))
    hashrate = serializers.FloatField(label=_('Hashrate'))


class Status(serializers.Serializer):
    status = serializers.CharField(label=_('Status'))
    hashrate = serializers.ListSerializer(child=Hashrate(), label=_('Hashrate per graphic'))
