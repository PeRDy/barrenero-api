# Barrenero API

REST API for interacting with Barrenero.

* **Version**: 1.0.0
* **Status**: Production/Stable
* **Author**: José Antonio Perdiguero López

This project defines a lightweight REST API on top of Barrenero Miner, providing an easy and simple way to interact
with all miners. This API exposes methods for:

* Query current machine status, such as active services, GPU stats...
* Query Ether miner and pool status.
* Restart Ether miner service.
* Query Storj miner status.
* Restart Storj miner service.
* Query Ethereum wallet value and last transactions.

Full [documentation](http://barrenero.readthedocs.io) for Barrenero project.

## Help us Donating
This project is free and open sourced, you can use it, spread the word, contribute to the codebase and help us donating:

* **Ether**: `0x566d41b925ed1d9f643748d652f4e66593cba9c9`
* **Bitcoin**: `1Jtj2m65DN2UsUzxXhr355x38T6pPGhqiA`
* **PayPal**: `barrenerobot@gmail.com`

## Requirements
* Docker. [Official docs](https://docs.docker.com/engine/installation/).

## Quick start

1. Configure api parameters in *setup.cfg* file. Parameters explained below.
2. Run the service: `docker run -p 80:80 --env-file=/etc/barrenero/api/setup.cfg perdy/barrenero-api:latest uwsgi`

## Configuration
Defines the following keys in *setup.cfg* file:

### Django Secret Key
Put the Django secret key in `DJANGO_SECRET_KEY` variable.

More info [here](https://docs.djangoproject.com/en/1.11/ref/settings/#secret-key>).

### API superuser password
To create an API superuser password that allows users to do actions such restarting services you must define a password
and encrypt it using Django tools:

```
from django.contrib.auth.hashers import make_password
password = make_password('foo_password')
```

You should put the result in `DJANGO_API_SUPERUSER` variable.

### Etherscan token
Put your Etherscan API token in `DJANGO_ETHERSCAN_TOKEN` variable.

More info [here](https://etherscan.io/apis).

### Ethplorer token
Put your Ethplorer API token in `DJANGO_ETHPLORER_TOKEN` variable.

More info [here](https://github.com/EverexIO/Ethplorer/wiki/Ethplorer-API).