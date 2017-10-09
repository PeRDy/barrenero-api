from django.contrib.auth.hashers import make_password
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from core import models


class User(serializers.Serializer):
    username = serializers.CharField(label=_('Username'))
    account = serializers.CharField(label=_('Wallet account'))
    is_api_superuser = serializers.BooleanField(label=_('Is API superuser'))


class UserRegister(serializers.Serializer):
    username = serializers.CharField(label=_('Username'))
    account = serializers.CharField(label=_('Wallet account'))
    password = serializers.CharField(
        label=_('Password'),
        style={'input_type': 'password'},
        trim_whitespace=False
    )
    api_password = serializers.CharField(
        label=_('API Superuser Password'),
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate_password(self, value):
        if value:
            return make_password(value)
        return None

    def validate(self, attrs):
        attrs['is_api_superuser'] = models.User.check_api_superuser(attrs['api_password'])
        del attrs['api_password']

        return attrs

    def create(self, validated_data):
        return models.User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.account = validated_data.get('account', instance.account)
        instance.password = validated_data.get('password', instance.password)
        instance.api_password = validated_data.get('api_password', instance.api_password)

        instance.save()

        return instance
