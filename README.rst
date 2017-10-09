=============
Barrenero API
=============

REST API for interacting with Barrenero.

:Version: 1.0.0
:Status: final
:Author: José Antonio Perdiguero López

This project defines a lightweight REST API on top of Barrenero Miner, providing an easy and simple way to interact
with all miners. This API exposes methods for:

* Query current machine status, such as active services, GPU stats...
* Query Ether miner and pool status.
* Restart Ether miner service.
* Query Storj miner status.
* Restart Storj miner service.
* Query Ethereum wallet value and last transactions.

Full `documentation <http://barrenero.readthedocs.io>`_ for Barrenero project.

Help us Donating
----------------

This project is free and open sourced, you can use it, spread the word, contribute to the codebase and help us donating:

:Ether: 0x566d41b925ed1d9f643748d652f4e66593cba9c9
:Bitcoin: 1Jtj2m65DN2UsUzxXhr355x38T6pPGhqiA

Requirements
------------

* Python 3.5 or newer. Download `here <https://www.python.org/>`_.
* Docker. `Official docs <https://docs.docker.com/engine/installation/>`_.

Quick start
-----------

1. Install services:

    .. code:: console

        sudo ./make install

2. Move to installation folder:

    .. code:: console

        cd /usr/local/lib/barrenero/barrenero-api/

3. Configure api parameters in *.env* file. Parameters explained below.

4. Build the service:

    .. code:: console

        ./make build

5. Reboot or restart Systemd unit:

    .. code:: console

        sudo service barrenero_api restart

Systemd
-------
The project provides a service file for Systemd that will be installed. These service files gives a reliable way to run
each miner, as well as overclocking scripts.

To check a miner service status:

.. code:: bash

    service barrenero_api status

Run manually
------------
As well as using systemd services you can run miners manually using:

.. code:: bash
    ./make run passenger

Configuration
-------------
Defines the following keys in `.env` file:

Django Secret Key
^^^^^^^^^^^^^^^^^
Put the Django secret key in `DJANGO_SECRET_KEY` variable.

More info `here <https://docs.djangoproject.com/en/1.11/ref/settings/#secret-key>`_.

API superuser password
^^^^^^^^^^^^^^^^^^^^^^
To create an API superuser password that allows users to do actions such restarting services you must define a password
and encrypt it using Django tools:

.. code:: python

    from django.contrib.auth.hashers import make_password

    password = make_password('foo_password')

You should put the result in `DJANGO_API_SUPERUSER` variable.

Etherscan token
^^^^^^^^^^^^^^^
Put your Etherscan API token in `DJANGO_ETHERSCAN_TOKEN` variable.

More info `here <https://etherscan.io/apis>`_.

Ethplorer token
^^^^^^^^^^^^^^^
Put your Ethplorer API token in `DJANGO_ETHPLORER_TOKEN` variable.

More info `here <https://github.com/EverexIO/Ethplorer/wiki/Ethplorer-API>`_.
