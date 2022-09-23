import os
from time import sleep
from lxml import html

from selenium.webdriver import Chrome
from multiprocessing.dummy import (
    Pool,
    Lock,
)

from src.common.format import dict_complement_b
from src.common.message import send_message
from src.common.page import (
    scrape_table,
    wait_history_table,
)


# Setup Global interpreter lock (GIL)
lock = Lock()


def refresh_tab(
        driver: Chrome,
        tab_name: str,
        element_name: str,
        wallet_name: str,
        wait_time: int = 30,
        max_wait_time: int = 50,
        infinite: bool = False,
) -> None:
    """
    Refreshes a tab given it's tab name

    :param driver: Web driver instance
    :param tab_name: Chrome Tab to switch to
    :param element_name: Element name to search for
    :param wallet_name: Name of browser being scraped
    :param wait_time: Seconds to wait before refreshing
    :param max_wait_time: Max seconds to wait before refreshing
    :param infinite: If True re-tries infinitely to retrieve response, default False
    :returns: None
    """
    lock.acquire()

    # Switch to window and Refresh tab
    driver.switch_to.window(tab_name)

    driver.refresh()

    # Wait for website to respond with History Table
    wait_history_table(driver, element_name, wallet_name, wait_time, max_wait_time, infinite)

    lock.release()


def get_last_txns(
        driver: Chrome,
        tab_name: str,
        element_name: str,
        element_id: str,
        wallet_name: str,
        no_of_txns: int = 100,
        wait_time: int = 30,
        max_wait_time: int = 50,
        infinite: bool = False,
) -> dict:
    """
    Searches DeBank for an Address Transaction history and returns its latest transactions.

    :param driver: Web driver instance
    :param tab_name: Chrome Tab to switch to
    :param element_name: Element name to search for
    :param element_id: Element ID to scrape
    :param wallet_name: Name of wallet to scrape
    :param no_of_txns: Number of transactions to return, up to 100
    :param wait_time: Seconds to wait before refreshing
    :param max_wait_time: Max seconds to wait before refreshing
    :param infinite: If True re-tries infinitely to retrieve response, default False
    :returns: Python Dictionary with  transactions
    """
    lock.acquire()

    driver.switch_to.window(tab_name)

    # Wait for website to respond with History Table
    wait_history_table(driver, element_name, wallet_name, wait_time, max_wait_time, infinite)

    try:
        root = html.fromstring(driver.page_source)
        table = root.find_class(element_id)[0]

        lock.release()

    except IndexError:
        lock.release()
        return {}

    # Return table as a Python Dictionary
    return scrape_table(table, no_of_txns)


def scrape_wallets_multiprocess(
        driver: Chrome,
        address_dict: dict,
        element_name: str,
        element_id: str,
        time_to_sleep: int = 30,
        wait_time: int = 30,
        max_wait_time: int = 50,
        infinite: bool = False,
) -> None:
    """
    Constantly scrapes multiple addresses and sends a Telegram message if new transaction is detected.

    :param driver: Web driver instance
    :param address_dict: Dictionary of addresses where keys are '0x63dhf6...9vs5' values
    :param element_name: Element name to wait for in HTML page
    :param element_id: Element ID to scrape from HTML page
    :param time_to_sleep: Time to sleep between queries
    :param wait_time: Seconds to wait before refreshing
    :param max_wait_time: Max seconds to wait before refreshing
    :param infinite: If True re-tries infinitely to retrieve response, default False
    :return: None
    """

    # construct url and open webpage
    tab_names = []
    wallet_names = []
    for address in address_dict:
        driver.execute_script(f"window.open('https://debank.com/profile/{address}/history')")
        tab_names.append(driver.window_handles[-1])
        wallet_names.append(address_dict[address]['name'])

    args_old_txn = [(driver, tab, element_name, element_id, wallet, 100, wait_time, max_wait_time, infinite)
                    for tab, wallet in zip(tab_names, wallet_names)]
    args_new_txn = [(driver, tab, element_name, element_id, wallet, 50, wait_time, max_wait_time, infinite)
                    for tab, wallet in zip(tab_names, wallet_names)]

    args_refresh = [(driver, tab, element_name, wallet, wait_time, max_wait_time, infinite)
                    for tab, wallet in zip(tab_names, wallet_names)]

    while True:

        with Pool(os.cpu_count()) as pool:
            # Get latest transactions
            old_txns = pool.starmap(get_last_txns, args_old_txn)

            # Sleep and refresh tabs
            sleep(time_to_sleep)
            pool.starmap(refresh_tab, args_refresh)

            # Get latest transactions
            new_txns = pool.starmap(get_last_txns, args_new_txn)

        # Send Telegram message if txns found
        for address, old_txn, new_txn in zip(address_dict, old_txns, new_txns):
            wallet_name = address_dict[address]['name']
            chat_id = address_dict[address]['chat_id']

            # If any new txns -> send Telegram message
            found_txns = dict_complement_b(old_txn, new_txn)
            send_message(found_txns, wallet_name, chat_id)
