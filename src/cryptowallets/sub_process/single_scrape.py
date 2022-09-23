from lxml import html
from time import sleep
from selenium.webdriver import Chrome

from src.common.message import send_message
from src.common.format import dict_complement_b
from src.common.page import (
    scrape_table,
    wait_history_table,
)
from src.common.variables import (
    table_element_name,
    table_element_id,
)


def refresh_tab(
        driver: Chrome,
        element_name: str,
        wallet_name: str,
        wait_time: int = 30,
        max_wait_time: int = 50,
) -> None:
    """
    Refreshes driver's current page.

    :param driver: Web driver instance
    :param element_name: Element name to wait for in HTML page
    :param wallet_name: Name of browser being scraped
    :param wait_time: Seconds to wait before refreshing
    :param max_wait_time: Max seconds to wait before refreshing
    :returns: None
    """

    # Refresh tab
    driver.refresh()

    # Wait for website to respond with History Table
    wait_history_table(driver, element_name, wallet_name, wait_time, max_wait_time)


def get_last_txns(
        driver: Chrome,
        element_name: str,
        element_id: str,
        wallet_name: str,
        no_of_txns: int = 100,
        wait_time: int = 30,
        max_wait_time: int = 50,
) -> dict:
    """
    Searches DeBank for an Address Transaction history and returns its latest transactions.

    :param driver: Web driver instance
    :param element_name: Element name to wait for in HTML page
    :param element_id: Element ID to scrape from HTML page
    :param wallet_name: Name of wallet to scrape
    :param no_of_txns: Number of transactions to return, up to 100
    :param wait_time: Seconds to wait before refreshing
    :param max_wait_time: Max seconds to wait before refreshing
    :returns: Python Dictionary with  transactions
    """

    # Wait for website to respond with History Table
    wait_history_table(driver, element_name, wallet_name, wait_time, max_wait_time)

    try:
        root = html.fromstring(driver.page_source)
        table = root.find_class(element_id)[0]

    except IndexError:
        # If element not found return an empty dictionary
        return {}

    else:
        # Return table as a Python Dictionary
        return scrape_table(table, no_of_txns)


def scrape_single_wallet(
        driver: Chrome,
        element_name: str,
        element_id: str,
        wallet_name: str,
        chat_id: str,
        time_to_sleep: int = 30,
        wait_time: int = 30,
        max_wait_time: int = 50,
):
    """
    Scrapes a single wallet address until terminated.

    :param driver: Web driver instance
    :param element_name: Element name to wait for in HTML page
    :param element_id: Element ID to scrape from HTML page
    :param wallet_name: Name of wallet
    :param chat_id: Telegram chat ID to send messages to
    :param time_to_sleep: Time to sleep between queries
    :param wait_time: Seconds to wait before refreshing
    :param max_wait_time: Max seconds to wait before refreshing
    :returns: None
    """

    while True:
        # Get latest transactions
        old_txns = get_last_txns(driver=driver,
                                 element_name=element_name,
                                 element_id=element_id,
                                 wallet_name=wallet_name,
                                 no_of_txns=100,
                                 wait_time=wait_time,
                                 max_wait_time=max_wait_time)

        # Sleep and refresh tab
        sleep(time_to_sleep)
        refresh_tab(driver=driver,
                    element_name=element_name,
                    wallet_name=wallet_name,
                    wait_time=wait_time,
                    max_wait_time=max_wait_time)

        # Get latest transactions
        new_txns = get_last_txns(driver=driver,
                                 element_name=element_name,
                                 element_id=element_id,
                                 wallet_name=wallet_name,
                                 no_of_txns=50,
                                 wait_time=wait_time,
                                 max_wait_time=max_wait_time)

        # If any new txns -> send Telegram message
        found_txns = dict_complement_b(old_txns, new_txns)
        send_message(found_txns=found_txns,
                     wallet_name=wallet_name,
                     chat_id=chat_id)


if __name__ == "__main__":

    import os
    import sys
    import ast

    from atexit import register

    from src.common.exceptions import exit_handler_driver
    from src.common.driver.driver import chrome_driver
    from src.common.variables import (
        request_wait_time,
        max_request_wait_time,
        sleep_time,
    )

    if len(sys.argv) != 3:
        sys.exit("Please provide 2 arguments: [Address] & [Address Info dictionary].")

    address = sys.argv[1]
    address_dict = ast.literal_eval(sys.argv[2])
    name = address_dict['name']
    chat = address_dict['chat_id']

    # Register function to be executed when script terminates
    program_name = f"{os.path.basename(__file__)} - {name} wallet"
    register(exit_handler_driver, chrome_driver, program_name)

    # Get page to scrape
    chrome_driver.get(f"https://debank.com/profile/{address}/history")

    # Start screening single wallet address
    scrape_single_wallet(driver=chrome_driver,
                         element_name=table_element_name,
                         element_id=table_element_id,
                         wallet_name=name,
                         chat_id=chat,
                         time_to_sleep=sleep_time,
                         wait_time=request_wait_time,
                         max_wait_time=max_request_wait_time)
