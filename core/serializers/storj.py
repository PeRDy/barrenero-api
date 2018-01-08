from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _


class Node(serializers.Serializer):
    id = serializers.CharField(label=_('Node ID'))
    status = serializers.CharField(label=_('Node status'))
    config_path = serializers.CharField(label=_('Storage path'))
    uptime = serializers.CharField(label=_('Uptime'))
    restarts = serializers.IntegerField(label=_('# of restarts'))
    peers = serializers.IntegerField(label=_('# of peers'))
    allocs = serializers.IntegerField(label=_('# of allocs'))
    data_received = serializers.IntegerField(label=_('Total data received'), allow_null=True)
    delta = serializers.IntegerField(label=_('Delta (ms)'), allow_null=True)
    port = serializers.IntegerField(label=_('Connection port'))
    shared = serializers.CharField(label=_('Total space shared'), allow_null=True)
    shared_percent = serializers.IntegerField(label=_('Percent of space shared'), allow_null=True)
    response_time = serializers.FloatField(label=_('Node response time'), allow_null=True)
    reputation = serializers.IntegerField(label=_('Node reputation'), allow_null=True)
    version = serializers.CharField(label=_('Node version'), allow_null=True)

