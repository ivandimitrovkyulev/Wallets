"""
Asynchronous transaction history scraping of https://debank.com/ for a specified wallet address.
"""
import time

from typing import List
from copy import deepcopy
from datetime import datetime
from requests import Response

from src.cryptowallets.datatypes import Wallet
from src.cryptowallets.compare import (
    compare_lists,
    alert_txns,
)
from src.cryptowallets.tor import (
    change_ip,
    get_tor_session,
)
from src.cryptowallets.common.logger import log_error
from src.cryptowallets.common.variables import time_format


def get_debank_resp(wallet: Wallet, txn_count: int = 20,
                    timeout: int = 10) -> Response | None:
    """
    Returns a GET response from https://api.debank.com/history/list for a wallet address.

    :param wallet: Address to scrape transactions from
    :param txn_count: Number of transactions to return. Max 20.
    :param timeout: Maximum time to wait for response
    :returns: History list transactions data
    """
    start_time = 0

    api = f"https://api.debank.com/history/list" \
          f"?page_count={txn_count}&start_time={start_time}&token_id=&user_addr={wallet.address}"

    try:
        resp = get_tor_session().get(api, timeout=timeout)
        return resp

    except Exception as e:
        log_error.warning(f"'get_debank_resp' - {Wallet} - {e}")
        return None


def get_last_txns(wallet: Wallet, txn_count: int = 20,
                  timeout: int = 10, max_wait_time: int = 15) -> dict | None:

    resp = get_debank_resp(wallet, txn_count, timeout)
    if not resp:
        return None

    start = time.perf_counter()
    while resp.status_code == 429:

        change_ip()
        resp = get_debank_resp(wallet, txn_count, timeout)

        if time.perf_counter() - start >= max_wait_time:
            log_error.warning(f"'get_last_txns' - Max wait time exceeded for {Wallet.name}")
            break

    data = resp.json()

    return data['data']


def scrape_wallets(wallets_list: List[Wallet], sleep_time: int) -> None:
    """
    Screens each wallet address for a new transaction and alerts via Telegram.

    :param wallets_list: List of Wallet[addr, name] data types.
    :param sleep_time: Time to sleep between loops
    """

    data = [get_last_txns(wallet) for wallet in wallets_list]
    old_txns = [[item['history_list'], item['token_dict']] if item else None for item in data]

    loop_counter = 1
    while True:
        # Wait for new transaction to appear
        start = time.perf_counter()
        time.sleep(sleep_time)

        data = [get_last_txns(wallet) for wallet in wallets_list]
        new_txns = [[item['history_list'], item['token_dict']] if item else None for item in data]

        # Iterate through all wallets
        for i, txns in enumerate(zip(new_txns, old_txns)):

            new_txn, old_txn = txns  # Unpack new and old txns

            new_history_list, new_token_dict = new_txn  # Unpack new history list & token dictionary
            old_history_list, old_token_dict = old_txn  # Unpack old history list & token dictionary
            wallet = wallets_list[i]  # Get wallet data

            # If empty list returned - no point to compare
            if len(new_history_list) == 0:
                continue

            # If new txns found - check them for spam
            found_txns = compare_lists(new_history_list, old_history_list)

            if found_txns:
                all_token_dict = new_token_dict | old_token_dict  # Merge dictionaries
                alert_txns(found_txns, wallet, all_token_dict)

                # Save latest txn data in old_txns only if there is a new txn
                old_txns[i] = deepcopy(new_txns[i])

        timestamp = datetime.now().astimezone().strftime(time_format)
        print(f"{timestamp} - Loop {loop_counter} executed in {(time.perf_counter() - start):,.2f} secs.")
        loop_counter += 1
