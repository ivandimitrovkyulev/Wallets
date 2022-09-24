from lxml.html import HtmlElement

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    WebDriverException,
    TimeoutException
)

from src.cryptowallets.common.logger import log_error


def wait_history_table(
        driver: Chrome,
        element_name: str,
        wallet_name: str,
        wait_time: int = 30,
        max_wait_time: int = 50,
        infinite: bool = False,
) -> None:
    """
    Waits infinitely for the presence of a HTML element located by its name.

    :param driver: Web driver instance
    :param element_name: Element name to search for
    :param wallet_name: Name of wallet to include into logger
    :param wait_time: Seconds to wait before refreshing
    :param max_wait_time: Max seconds to wait before refreshing
    :param infinite: If True re-tries infinitely to retrieve response, default False
    :returns: None
    """

    while True:
        try:
            WebDriverWait(driver, wait_time).until(ec.presence_of_element_located(
                (By.CLASS_NAME, element_name)))

        except WebDriverException or TimeoutException:
            # Refresh page and log error
            driver.refresh()
            log_error.warning(f"Error while loading transactions. Wait time: {wait_time} secs; wallet: {wallet_name}")

            # If query infinitely continue loop
            if infinite:
                continue

            # If no response is returned break
            if wait_time >= max_wait_time:
                # wait_time = max_wait_time
                break

            # Wait for longer periods
            wait_time += 10

        # If response returned - break
        else:
            break


def scrape_table(
        table: HtmlElement,
        no_of_txns: int = 100,
) -> dict:
    """
    Scrapes an HTML table element.

    :param table: Table of <class 'lxml.html.HtmlElement'>
    :param no_of_txns: Number of transactions to return, up to 100
    :returns: Python Dictionary
    """
    transactions = {}

    try:
        for index, row in enumerate(table.xpath('./div')):

            # If limit reached, break
            if index >= int(no_of_txns):
                break

            # Get link to transaction
            link = row.xpath('./div/div/a/@href')[0]

            txn_list = []
            for col in row.xpath('./div'):
                # Get text for Txn, Type, Amount, Gas fee
                info = col.xpath('.//text()')
                txn_list.append(info)

            if len(txn_list) == 4:
                transactions[link] = txn_list
            elif len(txn_list) > 4:
                txn_list = txn_list[:4]
                transactions[link] = txn_list
            elif len(txn_list) < 4:
                [txn_list.append([]) for _ in range(4 - len(txn_list))]

        return transactions

    except IndexError or Exception:
        return {}
