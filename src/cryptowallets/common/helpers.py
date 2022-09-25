from tabulate import tabulate

from src.cryptowallets.common.variables import CHAT_ID_ALERTS


def print_start_message(info: dict, timestamp: str) -> None:
    """
    Prints start message showing which addresses are being scraped.

    :param info: Info dictionary with input data.
    :param timestamp: Timestamp of the beginning
    """

    print(f"{timestamp} - Started screening the following wallet addresses:")

    wallets = [wallet for wallet in info['wallets']]

    message = [['-', '-', '-']]
    for address, details in info['wallets'].items():

        wallet_name = details['name']
        chat_id = details['chat_id']

        address = address[0:6] + '...' + address[-4:]

        if not chat_id:
            chat_id = CHAT_ID_ALERTS

        message.append([address, wallet_name, chat_id])

    columns = ["Wallet\nName", "Wallet\nAddress", "Chat_ID", ]

    print(tabulate(message, showindex=True, tablefmt="fancy_grid", headers=columns))
