"""
Command to generate an encrypted password.
"""
from django.contrib.auth.hashers import make_password
from django.core.management import BaseCommand


class Command(BaseCommand):
    """
    Management command to load a batch of Metadata from a file.
    """
    def add_arguments(self, parser):
        parser.add_argument('password', type=str, help='Unencrypted password')
        parser.add_argument('--salt', type=str, help='Salt', default=None)
        parser.add_argument('--hasher', type=str, help='Hash algorithm', default='default')

    def handle(self, *args, **options):
        password = make_password(options['password'], options['salt'], options['hasher'])
        self.stdout.write(f'{options["password"]} -> {password}')
