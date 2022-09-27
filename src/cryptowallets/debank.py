"""
Asynchronous transaction history scraping of https://debank.com/ for a specified wallet address.
"""
import json
import time
import asyncio

from aiohttp import ClientSession
from typing import (
    Callable,
    List,
)

from src.cryptowallets.datatypes import Wallet
from src.cryptowallets.common.logger import log_error
from src.cryptowallets.common.variables import timeout_class


async def gather_funcs(function: Callable, func_args: List[list]) -> tuple:
    """
    Gathers all asyncio http requests to be scheduled.

    :param function: Function name pointer to execute
    :param func_args: List of function arguments
    :return: List of all 1inch swaps
    """
    function_list = [function(*arg) for arg in func_args]

    func_results = await asyncio.gather(*function_list)

    return func_results


async def get_last_txns(wallet: Wallet, txn_count: int = 20,
                        sleep_time: float = 1, timeout: int = 10) -> dict | None:
    """
    Get last 20 transactions for an address from https://debank.com/.

    :param wallet: Address to scrape for transactions
    :param txn_count: Number of transactions to return. Max 20.
    :param sleep_time: Amount of time to sleep to avoid a potential rate limit.
    :param timeout: Maximum time to wait for response
    :returns: History list transactions data
    """
    start_time = 0

    # Sleep time for potential rate limits imposed
    time.sleep(sleep_time)

    api = f"https://api.debank.com/history/list?" \
          f"page_count={txn_count}&start_time={start_time}&token_id=&user_addr={wallet.address}"

    async with ClientSession(timeout=timeout_class) as async_http_session:
        try:
            async with async_http_session.get(api, ssl=False, timeout=timeout, raise_for_status=True) as response:

                data = json.loads(await response.text())

                if response.status != 200:
                    log_error.warning(
                        f"'get_last_txns', 'ResponseError', status: {response.status}, "
                        f"{data['error']} - {response.url}")
                    return None

        except Exception as e:
            log_error.warning(f"'get_last_txns', 'async_http_session' - {e}")
            return None

        return data['data']
