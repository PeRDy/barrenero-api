from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class GraphicCard(serializers.Serializer):
    id = serializers.IntegerField(label=_('Graphic card number'))
    power = serializers.FloatField(label=_('Current power usage'))
    fan = serializers.IntegerField(label=_('Fan speed (%)'))
    gpu_usage = serializers.IntegerField(label=_('GPU usage (%)'))
    mem_usage = serializers.IntegerField(label=_('Memory usage (%)'))
    gpu_clock = serializers.IntegerField(label=_('GPU clock speed (MHz)'))
    mem_clock = serializers.IntegerField(label=_('Memory clock speed (MHz)'))


class Service(serializers.Serializer):
    name = serializers.CharField(label=_('Service name'))
    status = serializers.CharField(label=_('Status'))


class Status(serializers.Serializer):
    graphics = serializers.ListField(child=GraphicCard(), label=_('Graphics status'))
    services = serializers.ListField(child=Service(), label=_('Services status'))

