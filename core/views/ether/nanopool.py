import asyncio
import datetime
import logging
from typing import Dict, Union

import aiohttp
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from core.serializers.ether import nanopool

logger = logging.getLogger(__name__)

__all__ = ['NanopoolMixin']


class NanopoolMixin:
    """
    Query Nanopool account and payments info.
    """
    async def _nanopool_account(self, session: 'aiohttp.ClientSession', account: str) -> Dict:
        """
        Query Nanopool account info, such as balance, hashrate and workers, and return it properly formatted.

        :param session: aiohttp Session.
        :param account: Account address.
        :return: Account info including balance, hashrate and workers.
        """
        account_info = {}
        retries = 3
        url = f'{settings.NANOPOOL["url"]}user/{account}'
        while not account_info and retries > 0:
            async with session.get(url) as response:
                try:
                    response.raise_for_status()
                    data = await response.json()

                    account_info = {
                        'balance': {
                            'confirmed': data['data']['balance'],
                            'unconfirmed': data['data']['unconfirmed_balance']
                        },
                        'hashrate': {
                            'current': data['data']['hashrate'],
                            'one_hour': data['data']['avgHashrate']['h1'],
                            'three_hours': data['data']['avgHashrate']['h3'],
                            'six_hours': data['data']['avgHashrate']['h6'],
                            'twelve_hours': data['data']['avgHashrate']['h12'],
                            'twenty_four_hours': data['data']['avgHashrate']['h24'],
                        },
                        'workers': {w['id']: w['hashrate'] for w in data['data']['workers']}
                    }
                except aiohttp.ClientResponseError:
                    retries -= 1
                    logger.exception('Cannot retrieve Nanopool account info')
                    account_info = {}
                except Exception as e:
                    retries -= 1
                    logger.exception('Wrong response: %s', e)
                    account_info = {}

        return account_info

    async def _nanopool_payment(self, session: 'aiohttp.ClientSession', account: str) -> Union[Dict, None]:
        """
        Query Nanopool payments info.

        :param session: aiohttp Session.
        :param account: Account address.
        :return: Last payment.
        """
        payment = None
        retries = 3
        url = f'{settings.NANOPOOL["url"]}payments/{account}'
        while payment is None and retries > 0:
            async with session.get(url) as response:
                try:
                    response.raise_for_status()

                    payment = (await response.json())['data'][0]
                    payment['date'] = datetime.datetime.fromtimestamp(payment['date'])
                except (IndexError, KeyError):
                    retries -= 1
                except aiohttp.ClientResponseError:
                    retries -= 1
                    logger.exception('Cannot retrieve Nanopool account info')
                except Exception as e:
                    retries -= 1
                    logger.exception('Wrong response: %s', e)

        return payment

    async def _nanopool(self, session: 'aiohttp.ClientSession', account: str) -> Dict:
        """
        Async wrapper for get method.

        :param account: Account address.
        :return: Nanopool info including balance, hashrate, workers and last payment.
        """
        data = await self._nanopool_account(session, account)
        data['last_payment'] = await self._nanopool_payment(session, account)

        return data
