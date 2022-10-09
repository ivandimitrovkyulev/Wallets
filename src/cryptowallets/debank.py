"""
Asynchronous transaction history scraping of https://debank.com/ for a specified wallet address.
"""
import time

from requests import Response

from src.cryptowallets.datatypes import Wallet
from src.cryptowallets.tor import (
    change_ip,
    get_tor_session,
)
from src.cryptowallets.common.logger import log_error


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
        log_error.warning(f"'get_debank_resp' - {Wallet.name} - {e}")
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
