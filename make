#!/usr/bin/env python3
import logging
import os
import shlex
import shutil
import subprocess
import sys
import uuid
from functools import wraps

logger = logging.getLogger('cli')

try:
    import docker
    import jinja2
    from clinner.command import command, Type as CommandType
    from clinner.run import Main
except ImportError:
    import importlib
    import pip
    import site

    print('Installing dependencies')
    pip.main(['install', '--user', '-qq', 'clinner', 'docker', 'jinja2'])

    importlib.reload(site)

    import docker
    import jinja2
    from clinner.command import command, Type as CommandType
    from clinner.run import Main

docker_cli = docker.from_env()

DONATE_TEXT = '''
This project is free and open sourced, you can use it, spread the word, contribute to the codebase and help us donating:
* Ether: 0x566d41b925ed1d9f643748d652f4e66593cba9c9
* Bitcoin: 1Jtj2m65DN2UsUzxXhr355x38T6pPGhqiA
* PayPal: barrenerobot@gmail.com
'''


def superuser(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not os.geteuid() == 0:
            logger.error('Script must be run as root')
            return -1

        return func(*args, **kwargs)

    return wrapper


def donate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        logger.info(DONATE_TEXT)

        return result
    return wrapper


@command(command_type=CommandType.SHELL_WITH_HELP,
         args=((('--registry',), {'help': 'Docker registry'}),
               (('--name',), {'help': 'Docker image name', 'default': 'barrenero-api'}),
               (('--tag',), {'help': 'Docker image tag', 'default': 'latest'})),
         parser_opts={'help': 'Docker build for local environment'})
@donate
def build(*args, **kwargs):
    tag = '{name}:{tag}'.format(**kwargs)

    cmd = shlex.split('docker build -t {tag} .'.format(tag=tag)) + list(args)
    return [cmd]


@command(command_type=CommandType.SHELL_WITH_HELP,
         parser_opts={'help': 'Restart Systemd service'})
@donate
@superuser
def restart(*args, **kwargs):
    cmd = shlex.split('service barrenero_api restart')
    return [cmd]


def _docker_flags(name, code, ports, network):
    flags = []

    # App volumes
    if code:
        flags.append('-v {}:/srv/apps/barrenero-api'.format(os.getcwd()))

    flags.append('-v {}:/srv/apps/barrenero-api/.data'.format(os.path.join(os.getcwd(), ".data")))
    flags.append('-v {}:/srv/apps/barrenero-api/logs'.format(os.path.join("/var/log/barrenero")))

    # System volumes
    flags.append('-v /run/systemd:/run/systemd')
    flags.append('-v /var/run/docker.sock:/var/run/docker.sock')

    # Flags
    flags.append('--env-file=.env')
    flags.append('--rm --name={}'.format(name))
    flags.append('--network={}'.format(network))
    flags.append(' '.join(['-p {}'.format(port) for port in ports]))

    return ' '.join(flags)


def _create_network(name):
    if not docker_cli.networks.list(names=name):
        docker_cli.networks.create(name)


@command(command_type=CommandType.SHELL,
         args=((('-n', '--name',), {'help': 'Docker image name', 'default': 'barrenero-api'}),
               (('--network',), {'help': 'Docker network', 'default': 'barrenero'}),
               (('-c', '--code',), {'help': 'Add code folder as volume', 'action': 'store_true'}),
               (('-i', '--interactive'), {'help': 'Docker image tag', 'action': 'store_true'}),
               (('-p', '--ports'), {'help': 'Ports to bind', 'nargs': '*', 'default': ['80:80']}),
               (('--no-nvidia',), {'help': 'Run with docker', 'action': 'store_true'})),
         parser_opts={'help': 'Run application'})
@donate
def run(*args, **kwargs):
    _create_network(kwargs['network'])

    # Select docker binary
    docker = 'docker' if kwargs['no_nvidia'] else 'nvidia-docker'

    flags = _docker_flags(kwargs['name'], kwargs['code'], kwargs['ports'], kwargs['network'])
    interactive_flag = '-it' if kwargs['interactive'] else '-d'

    cmd = shlex.split('{} run {} {} {}:latest -q --skip-check'.format(docker, flags, interactive_flag, kwargs['name']))
    cmd += list(args)
    return [cmd]


@command(command_type=CommandType.SHELL,
         args=((('-n', '--name',), {'help': 'Docker image name', 'default': 'barrenero-api'}),
               (('--network',), {'help': 'Docker network', 'default': 'barrenero'}),
               (('-c', '--code',), {'help': 'Add code folder as volume', 'action': 'store_true'}),
               (('-p', '--ports'), {'help': 'Ports to bind', 'nargs': '*', 'default': ['80:80']}),
               (('--no-nvidia',), {'help': 'Run with docker', 'action': 'store_true'})),
         parser_opts={'help': 'Create application container'})
@donate
def create(*args, **kwargs):
    _create_network(kwargs['network'])

    # Select docker binary
    docker = 'docker' if kwargs['no_nvidia'] else 'nvidia-docker'

    flags = _docker_flags(kwargs['name'], kwargs['code'], kwargs['ports'], kwargs['network'])

    cmd = shlex.split('{} create {} {}:latest'.format(docker, flags, kwargs['name']))
    cmd += list(args)
    return [cmd]


@command(command_type=CommandType.PYTHON,
         args=((('--path',), {'help': 'Barrenero full path', 'default': '/usr/local/lib/barrenero'}),),
         parser_opts={'help': 'Install the application in the system'})
@donate
@superuser
def install(*args, **kwargs):
    path = os.path.abspath(os.path.join(kwargs['path'], 'barrenero-api'))

    # Jinja2 builder
    j2_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(path, 'templates')))
    systemd_j2_context = {
        'app': {
            'name': 'barrenero-api',
            'path': path,
        },
        'settings': {
            'secret_key': uuid.uuid4().hex,
            'ethplorer': 'freekey',
        },
    }

    # Create app directory
    logger.info("[Barrenero API] Install app under %s", path)
    shutil.rmtree(path, ignore_errors=True)
    shutil.copytree('.', path)

    # Create setup file
    logger.info("[Barrenero API] Defining config file")
    with open(os.path.join(path, '.env'), 'w') as f:
        f.write(j2_env.get_template('env.jinja2').render(systemd_j2_context))

    # Create Systemd unit
    logger.info("[Barrenero API] Create Systemd unit and enable it")
    with open('/etc/systemd/system/barrenero_api.service', 'w') as f:
        f.write(j2_env.get_template('barrenero_api.service.jinja2').render(systemd_j2_context))
    subprocess.run(shlex.split('systemctl enable barrenero_api.service'))
    subprocess.run(shlex.split('systemctl daemon-reload'))

    logger.info('[Barrenero API] Remember to configure API in file %s', os.path.join(path, '.env'))


if __name__ == '__main__':
    sys.exit(Main().run())
