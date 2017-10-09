from __future__ import unicode_literals

import django.contrib.auth.validators
from django.db import migrations, models

import core.models.user


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('username', models.CharField(
                    error_messages={'unique': 'A user with that username already exists.'},
                    help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
                    max_length=150, unique=True,
                    validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
                    verbose_name='username')),
                ('account', models.CharField(max_length=100, unique=True, verbose_name='wallet account')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('is_admin', models.BooleanField(default=False, verbose_name='Is admin')),
                ('is_api_superuser', models.BooleanField(default=False, verbose_name='Is API superuser')),
                ('groups', models.ManyToManyField(
                    blank=True,
                    help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
                    related_name='user_set', related_query_name='user', to='auth.Group',
                    verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(
                    blank=True, help_text='Specific permissions for this user.',
                    related_name='user_set', related_query_name='user',
                    to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', core.models.user.UserManager()),
            ],
        ),
    ]
