import asyncio
import datetime
import logging
from typing import Dict, List
from urllib.parse import urljoin

import aiohttp
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from core.serializers import wallet

logger = logging.getLogger(__name__)

__all__ = ['Wallet']


class Wallet(APIView):
    """
    Wallet status provided by Etherscan.
    """
    serializer_class = wallet.Wallet

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
                logger.error('Wrong response: %s', str(e))
                price = None

        return price

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
                # All tokens
                tokens = {t['tokenInfo']['symbol']: {
                    'name': t['tokenInfo']['name'],
                    'symbol': t['tokenInfo']['symbol'],
                    'balance': t['balance'],
                    'price_usd': t['tokenInfo']['price']['rate'],
                    'balance_usd': t['balance'] * t['tokenInfo']['price']['rate'],
                } for t in result.get('tokens', [])}

                # Gets ETH/USD price
                price = await self._price(session)
                price_usd = float(price['ethusd']) if price else None
                balance_usd = price_usd * result['ETH']['balance'] if price else None

                # Add Ether token
                tokens['ETH'] = {
                    'name': 'Ether',
                    'symbol': 'ETH',
                    'balance': result['ETH']['balance'],
                    'price_usd': price_usd,
                    'balance_usd': balance_usd,
                }
            except aiohttp.ClientResponseError:
                logger.exception('Cannot retrieve Etherscan account info')
                tokens = None
            except Exception as e:
                logger.error('Wrong response: %s', str(e))
                tokens = None

        return tokens

    async def _transactions(self, session: 'aiohttp.ClientSession', account: str, number: int = 10) -> List[Dict]:
        """
        Query Etherscan and retrieve last transactions.

        :param session: aiohttp Session.
        :param account: Account address.
        :param number: Number of transactions to retrieve.
        :return: Wallet transactions.
        """
        params = {
            'module': 'account',
            'action': 'txlist',
            'address': account,
            'sort': 'desc',
            'startblock': 0,
            'endblock': 99_999_999,
            'page': 1,
            'offset': number,
            'apikey': settings.ETHERSCAN['token'],
        }
        async with session.get(settings.ETHERSCAN['url'], params=params) as response:
            try:
                response.raise_for_status()
                transactions = [{
                    'hash': t['hash'],
                    'contract_address': t['contractAddress'],
                    'source': t['from'],
                    'destination': t['to'],
                    'value': float(t['value']) / 10 ** 18,
                    'timestamp': datetime.datetime.fromtimestamp(int(t['timeStamp'])),
                } for t in (await response.json())['result']]
            except aiohttp.ClientResponseError:
                logger.exception('Cannot retrieve Etherscan transactions')
                transactions = None
            except Exception as e:
                logger.error('Wrong response: %s', str(e))
                transactions = None

        return transactions

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
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        data = loop.run_until_complete(self._get(request.user.account))

        serializer = self.serializer_class(data)
        return Response(serializer.data)
