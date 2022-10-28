import requests
from datetime import datetime
from tabulate import tabulate

from src.cryptowallets.common.message import telegram_send_message
from src.cryptowallets.common.variables import (
    CHAT_ID_ALERTS,
    CHAT_ID_ALERTS_ALL,
    TOKEN,
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

        if not chat_id:
            chat_id = CHAT_ID_ALERTS

        message.append([wallet_name, address, chat_id])

    columns = ["Wallet Name", "Wallet Address", "Chat ID", ]

    row_ids = [i for i in range(1, len(message) + 1)]

    print(tabulate(message, showindex=row_ids, tablefmt="fancy_grid", headers=columns))


def send_pin_message(info: dict) -> None:
    """
    Sends a Telegram message with a list of all addresses that will be monitored and pins it.

    :param info: Info dictionary with input data.
    """
    timestamp = datetime.now().astimezone().strftime(time_format)
    url = f"https://api.telegram.org/bot{TOKEN}/pinChatMessage"

    address_list = [f"-->{timestamp}\nStarted screening the following wallet addresses:"]
    counter = 1
    for address, details in info['wallets'].items():
        wallet_name = details['name']
        wallet_link = f"https://debank.com/profile/{address}/history"

        address_list.append(f"{counter}. {address}, <a href='{wallet_link}'>{wallet_name}</a>")

        counter += 1

    message = "\n".join(address_list)

    resp = telegram_send_message(message, telegram_chat_id=CHAT_ID_ALERTS)
    message_id = resp.json()['result']['message_id']
    payload = {'chat_id': CHAT_ID_ALERTS, 'message_id': message_id}
    requests.post(url=url, data=payload, timeout=10)

    resp = telegram_send_message(message, telegram_chat_id=CHAT_ID_ALERTS_ALL)
    message_id = resp.json()['result']['message_id']
    payload = {'chat_id': CHAT_ID_ALERTS_ALL, 'message_id': message_id}
    requests.post(url=url, data=payload, timeout=10)
