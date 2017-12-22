import asyncio
import datetime
import logging
from itertools import chain
from typing import Dict, List
from urllib.parse import urljoin

import aiohttp
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from core.serializers import wallet
from core.utils import retry, get_event_loop

logger = logging.getLogger(__name__)

__all__ = ['Wallet']


class Wallet(APIView):
    """
    Wallet status provided by Etherscan.
    """
    serializer_class = wallet.Wallet

    @retry(3)
    async def _price(self, session: 'aiohttp.ClientSession') -> Dict:
        """
        Query Etherscan and retrieve currency Ether price.

        :param session: aiohttp Session.
        :return: Currency price.
        """
        params = {
            'module': 'stats',
            'action': 'ethprice',
            'apikey': settings.ETHERSCAN['token'],
        }
        async with session.get(settings.ETHERSCAN['url'], params=params) as response:
            try:
                response.raise_for_status()
                price = (await response.json())['result']
            except aiohttp.ClientResponseError:
                logger.exception('Cannot retrieve Etherscan price')
                price = None
            except Exception as e:
                logger.exception('Wrong response: %s', str(e))
                price = None

        return price

    @retry(3)
    async def _tokens(self, session: 'aiohttp.ClientSession', account: str) -> Dict:
        """
        Query Ethplorer and retrieve current wallet tokens.

        :param session: aiohttp Session.
        :param account: Account address.
        :return: Wallet tokens.
        """
        url = urljoin(settings.ETHPLORER["url"], f'/getAddressInfo/{account}')
        params = {'apiKey': settings.ETHPLORER['token']}
        async with session.get(url=url, params=params) as response:
            try:
                response.raise_for_status()
                result = await response.json(content_type='text/html')

                # Gets ETH/USD price
                price = await self._price(session)
                price_usd = float(price['ethusd']) if price else None
                balance_usd = price_usd * result['ETH']['balance'] if price else None

                # Add Ether token
                tokens = {
                    'ETH': {
                        'name': 'Ether',
                        'symbol': 'ETH',
                        'balance': result['ETH']['balance'],
                        'price_usd': price_usd,
                        'balance_usd': balance_usd
                    }
                }

                # All tokens
                for t in result.get('tokens', []):
                    decimals = 10 ** (-int(t['tokenInfo']['decimals']))
                    token = {
                        'name': t['tokenInfo']['name'],
                        'symbol': t['tokenInfo']['symbol'],
                        'balance': t['balance'] * decimals,
                    }

                    if t['tokenInfo']['price']:
                        token['price_usd'] = t['tokenInfo']['price']['rate']
                        token['balance_usd'] = t['balance'] * decimals * float(t['tokenInfo']['price']['rate'])

                    tokens[t['tokenInfo']['symbol']] = token
            except aiohttp.ClientResponseError:
                logger.exception('Cannot retrieve Ethplorer account info')
                tokens = None
            except Exception as e:
                logger.exception('Wrong response: %s', str(e))
                tokens = None

        return tokens

    @retry(3)
    async def _eth_transactions(self, session: 'aiohttp.ClientSession', account: str) -> List[Dict]:
        """
        Query Ethplorer and retrieve last transactions.

        :param session: aiohttp Session.
        :param account: Account address.
        :return: Wallet transactions.
        """
        url = urljoin(settings.ETHPLORER["url"], f'/getAddressTransactions/{account}')
        params = {'apiKey': settings.ETHPLORER['token']}
        async with session.get(url, params=params) as response:
            try:
                response.raise_for_status()
                transactions = [{
                    'token': {
                        'name': 'Ether',
                        'symbol': 'ETH',
                    },
                    'hash': t['hash'],
                    'source': t['from'],
                    'destination': t['to'],
                    'value': float(t['value']),
                    'timestamp': datetime.datetime.fromtimestamp(int(t['timestamp'])),
                } for t in (await response.json(content_type='text/html'))]
            except aiohttp.ClientResponseError:
                logger.exception('Cannot retrieve Ethplorer transactions')
                transactions = None
            except asyncio.TimeoutError:
                logger.exception('Timeout')
                transactions = None
            except Exception as e:
                logger.exception('Wrong response: %s', str(e))
                transactions = None

        return transactions

    @retry(3)
    async def _token_operations(self, session: 'aiohttp.ClientSession', account: str) -> List[Dict]:
        """
        Query Ethplorer and retrieve last token operations.

        :param session: aiohttp Session.
        :param account: Account address.
        :return: Wallet transactions.
        """
        url = urljoin(settings.ETHPLORER["url"], f'/getAddressHistory/{account}')
        params = {'apiKey': settings.ETHPLORER['token']}
        async with session.get(url, params=params) as response:
            try:
                response.raise_for_status()
                transactions = [{
                    'token': {
                        'name': t['tokenInfo']['name'],
                        'symbol': t['tokenInfo']['symbol'],
                    },
                    'hash': t['transactionHash'],
                    'source': t['from'],
                    'destination': t['to'],
                    'value': float(t['value']) * 10 ** (-int(t['tokenInfo']['decimals'])),
                    'timestamp': datetime.datetime.fromtimestamp(int(t['timestamp'])),
                } for t in (await response.json(content_type='text/html'))['operations']]
            except aiohttp.ClientResponseError:
                logger.exception('Cannot retrieve Ethplorer token operations')
                transactions = None
            except asyncio.TimeoutError:
                logger.exception('Timeout')
                transactions = None
            except Exception as e:
                logger.exception('Wrong response: %s', str(e))
                transactions = None

        return transactions

    async def _transactions(self, session: 'aiohttp.ClientSession', account: str) -> List[Dict]:
        """
        Query Ethplorer and retrieve last token operations.

        :param session: aiohttp Session.
        :param account: Account address.
        :return: Wallet transactions.
        """
        eth_tx = await self._eth_transactions(session, account) or []
        token_ops = await self._token_operations(session, account) or []

        return sorted(chain(eth_tx, token_ops), key=lambda x: x['timestamp'], reverse=True)

    async def _get(self, account):
        """
        Async wrapper for get method.

        :param account: Account address.
        :return: Wallet info including balance and transactions.
        """
        async with aiohttp.ClientSession() as session:
            transactions = await self._transactions(session, account)
            tokens = await self._tokens(session, account)

            data = {
                'tokens': tokens,
                'transactions': transactions,
            }

        return data

    def get(self, request, format=None):
        """
        Query Etherscan and retrieve current wallet info.
        """
        loop = get_event_loop()
        data = loop.run_until_complete(self._get(request.user.account))

        serializer = self.serializer_class(data)
        return Response(serializer.data)
