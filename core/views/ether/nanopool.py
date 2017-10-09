import asyncio
import datetime
import logging
from typing import Dict

import aiohttp
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from core.serializers.ether import nanopool

logger = logging.getLogger(__name__)

__all__ = ['Nanopool']


class Nanopool(APIView):
    """
    Query Nanopool account and payments info.
    """
    serializer_class = nanopool.Nanopool

    async def _account(self, session: 'aiohttp.ClientSession', account: str) -> Dict:
        """
        Query Nanopool account info, such as balance, hashrate and workers, and return it properly formatted.

        :param session: aiohttp Session.
        :param account: Account address.
        :return: Account info including balance, hashrate and workers.
        """
        url = f'{settings.NANOPOOL["url"]}user/{account}'
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
                    'workers': [{'id': w['id'], 'hashrate': w['hashrate']} for w in data['data']['workers']]
                }
            except aiohttp.ClientResponseError:
                logger.exception('Cannot retrieve Nanopool account info')
                account_info = {}
            except Exception as e:
                logger.error('Wrong response: %s', e)
                account_info = {}

        return account_info

    async def _payment(self, session: 'aiohttp.ClientSession', account: str) -> Dict:
        """
        Query Nanopool payments info.

        :param session: aiohttp Session.
        :param account: Account address.
        :return: Last payment.
        """
        url = f'{settings.NANOPOOL["url"]}payments/{account}'
        async with session.get(url) as response:
            try:
                response.raise_for_status()

                payment = (await response.json())['data'][0]
                payment['date'] = datetime.datetime.fromtimestamp(payment['date'])
            except (IndexError, KeyError):
                pass
                payment = None
            except aiohttp.ClientResponseError:
                logger.exception('Cannot retrieve Nanopool account info')
                payment = None
            except Exception as e:
                logger.error('Wrong response: %s', e)
                payment = None

        return payment

    async def _get(self, account: str) -> Dict:
        """
        Async wrapper for get method.

        :param account: Account address.
        :return: Nanopool info including balance, hashrate, workers and last payment.
        """
        async with aiohttp.ClientSession() as session:
            data = await self._account(session, account)
            data['last_payment'] = await self._payment(session, account)

        return data

    def get(self, request, format=None):
        """
        Query Nanopool account and payments info.
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        data = loop.run_until_complete(self._get(request.user.account))

        serializer = self.serializer_class(data)
        return Response(serializer.data)
