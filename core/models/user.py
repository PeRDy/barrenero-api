import six
from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.validators import ASCIIUsernameValidator, UnicodeUsernameValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

__all__ = ['User']


class UserManager(BaseUserManager):
    use_in_migrations = True

    @classmethod
    def normalize_account(cls, account):
        account = '0x' + account if not account.startswith('0x') else account
        return account

    def _create_user(self, username, account, password=None):
        if not account:
            raise ValueError('Users must have an account address')

        user = self.model(username=username, account=self.normalize_account(account))

        user.set_password(password)

        return user

    def create_user(self, username, account, password=None):
        """
        Creates and saves a User with the given username, account, password and api password.
        """
        user = self._create_user(username, account, password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, account, password):
        """
        Creates and saves a superuser with the given username, account, password and api password.
        """
        user = self._create_user(username, account, password)
        user.is_admin = True
        user.is_api_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator() if six.PY3 else ASCIIUsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    account = models.CharField(_('wallet account'), max_length=100, unique=True)
    is_active = models.BooleanField(_('Is active'), default=True)
    is_admin = models.BooleanField(_('Is admin'), default=False)
    is_api_superuser = models.BooleanField(_('Is API superuser'), default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['account']

    def has_perm(self, perm, obj=None):
        if perm == 'global_permissions.restart' and self.is_api_superuser:
            return True

        return super().has_perm(perm, obj)

    def get_full_name(self):
        """
        The user is identified by their wallet account address.
        """
        return f'{self.username} ({self.account})'

    def get_short_name(self):
        """
        The user is identified by their wallet account address.
        """
        return self.username

    def __str__(self):
        return self.username

    @property
    def is_staff(self):
        """
        Is the user a member of staff?
        """
        return self.is_admin

    @property
    def is_superuser(self):
        return self.is_admin

    @classmethod
    def check_api_superuser(cls, password):
        """
        Check if the password matches with API superuser's.
        """
        return check_password(password, settings.API_SUPERUSER)
