import json
import asyncio
from typing import (
    Callable,
    List,
    Dict,
)
from aiohttp import ClientSession

from src.cryptowallets.common.logger import log_error
from src.cryptowallets.common.variables import timeout_class
from datetime import (
    datetime,
    timezone,
)

from src.cryptowallets.datatypes import Wallet
from src.cryptowallets.common.variables import (
    chains,
    time_format,
)


async def get_last_txns(wallet: Wallet, txn_count: int = 20, timeout: int = 5):
    """
    Get last 20 transactions for an address from https://debank.com/.

    :param wallet: Address to scrape for transactions
    :param txn_count: Number of transactions to return. Max 20.
    :param timeout: Maximum time to wait for response
    """

    start_time = 0

    api = f"https://api.debank.com/history/list"
    payload = {'user_addr': wallet.address, 'token_id': wallet.address,
               'start_time': start_time, 'page_count': txn_count, }

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
                              f"{api}?user_addr={wallet.address}&token_id={wallet.address}"
                              f"&start_time={start_time}&page_count=20 - {e}")
            return None

        return data['data']


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


def format_txn_message(txn: dict, wallet: Wallet, tokens_dicts: Dict[str, dict]) -> str:
    """
    Formats a transaction into a message string.

    :param txn: Transaction dictionary
    :param wallet: Wallet txn came from
    :param tokens_dicts: Dictionary with token info
    :return: Formatted message string
    """

    chain = txn['chain']  # Shortened name of blockchain
    txn_hash = txn['id']  # Transaction hash
    time_at_secs = int(txn['time_at'])  # eg. 1664049342 secs

    time_stamp = datetime.fromtimestamp(time_at_secs, timezone.utc).strftime(time_format)

    sends_info = txn['sends']
    send_items = []
    receive_info = txn['receives']
    receive_items = []

    if sends_info:
        for send in sends_info:
            amount = send['amount']
            token_id = send['token_id']
            try:
                token_name = tokens_dicts[token_id]['symbol']
            except KeyError:
                token_name = ''
            send_items.append(f"{amount:,} {token_name}")
    else:
        send_items.append(None)

    if receive_info:
        for receive in receive_info:
            amount = receive['amount']
            token_id = receive['token_id']
            try:
                token_name = tokens_dicts[token_id]['symbol']
            except KeyError:
                token_name = ''
            receive_items.append(f"{amount:,} {token_name}")
    else:
        receive_items.append(None)

    try:
        txn_type = txn['tx']['name']
    except TypeError or KeyError:
        txn_type = txn['cate_id']
    txn_type = txn_type[0].upper() + txn_type[1:]

    try:
        txn_link = chains[chain] + txn_hash
    except KeyError:
        txn_link = f"https://www.google.com/search?&rls=en&q={chain}+{txn_hash}&ie=UTF-8&oe=UTF-8"

    wallet_link = f"https://debank.com/profile/{wallet.address}/history"

    message = f"-> {time_stamp} - Txn from <a href='{wallet_link}'>{wallet.name}</a>\n" \
              f"{txn_type}, send{send_items}, receive{receive_items}\n" \
              f"Txn hash: <a href='{txn_link}'>{wallet.address}</a>"

    return message


def check_txn(txn: dict) -> bool:

    try:
        status = txn['tx']['status']
        if int(status) == 0:
            return False

    except TypeError or KeyError:
        pass


