import time
import json
import asyncio
import requests
from pprint import pprint
from typing import (
    Callable,
    List,
)

from json.decoder import JSONDecodeError
from aiohttp import ClientSession
from src.cryptowallets.common.logger import log_error
from src.cryptowallets.common.variables import (
    http_session,
    timeout_class,
)


async def get_last_txns(address: str, timeout: int = 5):

    start_time = 0

    api = f"https://api.debank.com/history/list"
    payload = {'user_addr': address, 'token_id': address,
               'start_time': start_time, 'page_count': 20,}

    async with ClientSession(timeout=timeout_class) as async_http_session:
        try:
            async with async_http_session.get(api, ssl=False, params=payload, timeout=timeout) as response:

                data = json.loads(await response.text())

                if response.status != 200:
                    log_error.warning(
                        f"'get_last_txns', 'ResponseError', status: {response.status}, "
                        f"{data['error']} - {response.url}")
                    return None

        except Exception as e:
            log_error.warning(f"'get_last_txns', 'async_http_session' Error - could not connect to "
                              f"{api}?user_addr={address}&token_id={address}"
                              f"&start_time={start_time}&page_count=20 - {e}")
            return None

        return data


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


args = [['0x19cd713c3ea67285a8bbc378fda9769106597392'], ['0x4eb0a45D3fba156965Dcd9aCbd34DAf4533dBcC1']]
results = asyncio.run(gather_funcs(get_last_txns, args))
for res in results:
    print(res)
