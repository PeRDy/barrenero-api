import copy
import logging

from django.db.utils import IntegrityError
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.serializers.auth import User, UserRegister

logger = logging.getLogger(__name__)


__all__ = ['ObtainUser', 'UserRegister']


class ObtainUser(APIView):
    """
    Retrieve user token and user given username and password.
    """
    permission_classes = (AllowAny,)
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        """
        Retrieve user token and user given username and password.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        data = User(user).data
        data['token'] = token.key
        return Response(data)


class UserRegister(APIView):
    """
    Register a new user.
    """
    permission_classes = (AllowAny,)
    serializer_class = UserRegister

    def post(self, request, format=None):
        """
        Register a new user providing username, password, account and api_password.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = serializer.save()

            response_data = copy.deepcopy(serializer.validated_data)
            del response_data['password']
            response_data['token'] = Token.objects.get(user=user).key

            return Response(response_data)
        except IntegrityError as e:
            return Response({'error': str(e)}, status=status.HTTP_409_CONFLICT)
