from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class Payment(serializers.Serializer):
    date = serializers.DateTimeField(label=_('Timestamp'))
    hash = serializers.CharField(label=_('Transaction hash'), source='txHash')
    value = serializers.FloatField(label=_('Value'), source='amount')
    confirmed = serializers.BooleanField(label=_('Confirmed'))


class Balance(serializers.Serializer):
    confirmed = serializers.FloatField(label=_('Confirmed balance'))
    unconfirmed = serializers.FloatField(label=_('Unconfirmed balance'))


class Hashrate(serializers.Serializer):
    current = serializers.FloatField(label=_('Current'))
    one_hour = serializers.FloatField(label=_('1h'))
    three_hours = serializers.FloatField(label=_('3h'))
    six_hours = serializers.FloatField(label=_('6h'))
    twelve_hours = serializers.FloatField(label=_('12h'))
    twenty_four_hours = serializers.FloatField(label=_('24h'))


class Worker(serializers.Serializer):
    id = serializers.CharField(label=_('Worker name'))
    hashrate = serializers.FloatField(label=_('Current hashrate'))


class Nanopool(serializers.Serializer):
    balance = Balance(label=_('Current balance'))
    hashrate = Hashrate(label=_('Hashrate'))
    workers = serializers.ListField(child=Worker(), label=_('Worker info'))
    last_payment = Payment(required=False, label=_('Last payment'))
