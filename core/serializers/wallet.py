from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class Token(serializers.Serializer):
    name = serializers.CharField(label=_('Name'))
    symbol = serializers.CharField(label=_('Symbol'))
    balance = serializers.FloatField(label=_('Balance'))
    price_usd = serializers.FloatField(label=_('Token to USD conversion price'))
    balance_usd = serializers.FloatField(label=_('Balance in USD'))


class Transaction(serializers.Serializer):
    hash = serializers.CharField(label=_('Transaction hash'))
    contract_address = serializers.CharField(label=_('Contract address'), allow_blank=True)
    source = serializers.CharField(label=_('Source account'))
    destination = serializers.CharField(label=_('Destination account'))
    value = serializers.FloatField(label=_('Transaction value'))
    timestamp = serializers.DateTimeField(label=_('Transaction timestamp'))


class Wallet(serializers.Serializer):
    tokens = serializers.DictField(child=Token(), label=_('Tokens'))
    transactions = serializers.ListSerializer(child=Transaction(), label=_('Last transactions'))
