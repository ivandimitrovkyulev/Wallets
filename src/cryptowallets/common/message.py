from time import sleep
from typing import Optional
from datetime import datetime

from requests.exceptions import ConnectionError
from requests import (
    post,
    Response,
)
from src.common.logger import log_error
from src.common.format import format_data
from src.common.variables import (
    TOKEN,
    CHAT_ID_ALERTS,
    CHAT_ID_DEBUG,
    CHAT_ID_SPECIAL,
    time_format,
)


def telegram_send_message(
        message_text: str,
        disable_web_page_preview: bool = True,
        telegram_token: Optional[str] = "",
        telegram_chat_id: Optional[str] = "",
        debug: bool = False,
) -> Response:
    """
    Sends a Telegram message to a specified chat.
    Must have a .env file with the following variables:
    TOKEN: your Telegram access token.
    CHAT_ID: the specific id of the chat you want the message sent to
    Follow telegram's instruction on how to set up a bot using the bot father
    and configure it to be able to send messages to a chat.

    :param message_text: Text to be sent to the chat
    :param disable_web_page_preview: Set web preview on/off
    :param telegram_token: Telegram TOKEN API, default take from .env
    :param telegram_chat_id: Telegram chat ID for alerts, default is 'CHAT_ID_ALERTS' from .env file
    :param debug: If true sends message to Telegram chat with 'CHAT_ID_DEBUG' from .env file
    :return: requests.Response
    """
    telegram_token = str(telegram_token)
    telegram_chat_id = str(telegram_chat_id)

    # if URL not provided - try TOKEN variable from the .env file
    if telegram_token == "":
        telegram_token = TOKEN

    # if chat_id not provided - try CHAT_ID_ALERTS or CHAT_ID_DEBUG variable from the .env file
    if telegram_chat_id == "":
        if debug:
            telegram_chat_id = CHAT_ID_DEBUG
        else:
            telegram_chat_id = CHAT_ID_ALERTS

    # construct url using token for a sendMessage POST request
    url = "https://api.telegram.org/bot{}/sendMessage".format(telegram_token)

    # Construct data for the request
    data = {"chat_id": telegram_chat_id, "text": message_text,
            "disable_web_page_preview": disable_web_page_preview}

    # send the POST request
    while True:
        try:
            post_request = post(url, data)

            return post_request

        except ConnectionError as e:
            log_error.warning(f"{e}")
            sleep(3)


def send_message(
        found_txns: dict,
        wallet_name: str,
        chat_id: str,
) -> None:
    """
    Sends a Telegram message with txns from Dictionary.

    :param found_txns: Dictionary with transactions
    :param wallet_name: Name of wallet
    :param chat_id: Telegram chat ID for this address
    :returns: None
    """
    # If a txn is found
    if len(found_txns) > 0:
        for txn in found_txns.keys():
            # Format dict value and filter out specific transactions
            data = format_data(found_txns[txn])

            # Do not send message if Txn does not meet criteria
            if not data:
                break

            # Un-pack data
            info, flag = data

            # Construct message string
            formatted_info = ""
            for item in info:
                formatted_info += f"         {item}\n"

            message = f"-->New txn from {wallet_name.upper()}:\n" \
                      f"{txn}\n" \
                      f"Details: \n" \
                      f"{formatted_info}"

            # Send Telegram message with found txns to specified chat
            telegram_send_message(message, telegram_chat_id=chat_id)

            # Send Telegram message to a dedicated chat
            if CHAT_ID_SPECIAL and chat_id != "" and flag != 'spam':
                telegram_send_message(message, telegram_chat_id=CHAT_ID_SPECIAL)

            # Print result to terminal
            timestamp = datetime.now().astimezone().strftime(time_format)
            print(f"{timestamp} - {message}")
