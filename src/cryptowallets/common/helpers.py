from datetime import datetime
from tabulate import tabulate

from src.cryptowallets.common.variables import (
    CHAT_ID_ALERTS,
    time_format,
)


def print_start_message(info: dict) -> None:
    """
    Prints start message showing which addresses are being scraped.

    :param info: Info dictionary with input data.
    """

    timestamp = datetime.now().astimezone().strftime(time_format)
    print(f"{timestamp} - Started screening the following wallet addresses:")

    message = []
    for address, details in info['wallets'].items():

        wallet_name = details['name']
        chat_id = details['chat_id']

        address = address[0:6] + '...' + address[-4:]

        if not chat_id:
            chat_id = CHAT_ID_ALERTS

        message.append([wallet_name, address, chat_id])

    columns = ["Wallet Name", "Wallet Address", "Chat ID", ]

    row_ids = [i for i in range(1, len(message) + 1)]

    print(tabulate(message, showindex=row_ids, tablefmt="fancy_grid", headers=columns))
