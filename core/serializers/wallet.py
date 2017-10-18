from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class Token(serializers.Serializer):
    name = serializers.CharField(label=_('Name'))
    symbol = serializers.CharField(label=_('Symbol'))
    balance = serializers.FloatField(label=_('Balance'), required=False)
    price_usd = serializers.FloatField(label=_('Token to USD conversion price'), required=False)
    balance_usd = serializers.FloatField(label=_('Balance in USD'), required=False)


class Transaction(serializers.Serializer):
    token = Token()
    hash = serializers.CharField(label=_('Transaction hash'))
    source = serializers.CharField(label=_('Source account'))
    destination = serializers.CharField(label=_('Destination account'))
    value = serializers.FloatField(label=_('Transaction value'))
    timestamp = serializers.DateTimeField(label=_('Transaction timestamp'))


class Wallet(serializers.Serializer):
    tokens = serializers.DictField(child=Token(), label=_('Tokens'))
    transactions = serializers.ListSerializer(child=Transaction(), label=_('Last transactions'))
