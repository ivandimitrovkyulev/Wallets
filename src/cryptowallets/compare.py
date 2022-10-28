from typing import (
    Dict,
    List,
)
from datetime import (
    datetime,
    timezone,
)

from src.cryptowallets.datatypes import Wallet
from src.cryptowallets.common.message import telegram_send_message
from src.cryptowallets.common.logger import (
    log_error,
    log_spam,
    log_fail,
    log_txns,
)
from src.cryptowallets.common.variables import (
    chains,
    time_format,
    CHAT_ID_ALERTS,
    CHAT_ID_ALERTS_ALL,
)


def compare_lists(new_list: List[dict], old_list: List[dict],
                  keyword: str = 'id') -> list[dict] | None:
    """
    Compares two lists of dictionaries.

    :param new_list: New list
    :param old_list: Old list
    :param keyword: Keyword to compare with
    :return: List of dictionaries that are in new list but not in old list
    """

    try:
        ids = [txn[keyword] for txn in old_list]

        list_diff = [txn for txn in new_list if txn[keyword] not in ids]

        return list_diff

    except TypeError:
        log_error.warning(f"'compare_lists' Error - unable to compare")
        return None


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
    formatted_txn_hash = f"{txn_hash[0:6]}...{txn_hash[-4:]}"  # eg. 0xc43c...37ea
    time_at_secs = int(txn['time_at'])  # eg. 1664049342 secs
    other_addr = txn['other_addr']  # eg. Interacted With (To):

    txn_stamp = datetime.fromtimestamp(time_at_secs, timezone.utc).strftime(time_format)

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
        send_items.append('None')

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
        receive_items.append('None')

    try:
        txn_type = txn['tx']['name']
    except TypeError or KeyError:
        txn_type = txn['cate_id']

    if txn_type and len(txn_type) > 0:
        txn_type = txn_type[0].upper() + txn_type[1:]
    else:
        txn_type = ''

    try:
        txn_link = f"{chains[chain]}/tx/{txn_hash}"
    except KeyError:
        txn_link = f"https://www.google.com/search?&rls=en&q={chain}+{txn_hash}&ie=UTF-8&oe=UTF-8"

    wallet_link = f"https://debank.com/profile/{wallet.address}/history"
    try:
        interacted_with_link = f"{chains[chain]}/address/{other_addr}"
    except KeyError:
        interacted_with_link = f"https://www.google.com/search?&rls=en&q={chain}+{other_addr}&ie=UTF-8&oe=UTF-8"

    timestamp = datetime.now().astimezone().strftime(time_format)
    message = f"-> {timestamp}\n" \
              f"New txn <a href='{txn_link}'>{formatted_txn_hash}</a> " \
              f"from <a href='{wallet_link}'>{wallet.name}</a>\n" \
              f"Timestamp:  {txn_stamp}\n" \
              f"Type: <a href='{interacted_with_link}'>{txn_type}</a>\n" \
              f"Send: {', '.join(send_items)}\n" \
              f"Receive: {', '.join(receive_items)}\n"

    return message


def check_txn(txn: dict, tokens_dicts: Dict[str, dict]) -> bool:
    """
    Checks whether a transaction is Normal or Spam.

    :param txn: Transaction dictionary
    :param tokens_dicts: Dictionary with token info
    :return: True if transaction is Normal, False if Spam or Failed
    """

    try:
        status = txn['tx']['status']  # Check transaction status - 0 for Failed
        if int(status) == 0:
            log_fail.info(txn)
            return False

    except TypeError or KeyError:
        pass

    for receive in txn['receives']:
        # Get token ID
        token_id = receive['token_id']

        # If token_id len is less than 42 -> likely a spam NFT
        if len(token_id) < 42:
            log_spam.info(txn)
            return False

        token_is_verified = tokens_dicts[token_id]['is_verified']
        if not token_is_verified:
            log_spam.info(txn)
            return False


def alert_txns(txns: List[dict], wallet: Wallet, tokens_dicts: Dict[str, dict]) -> None:
    """
    Alerts for any matching transactions via Telegram message.

    :param txns: Transaction dictionary
    :param wallet: Wallet txn came from
    :param tokens_dicts: Dictionary with token info
    """

    for txn in txns:

        # If nothing returned - continue
        if not txn or len(txn) == 0:
            continue

        txn_message = format_txn_message(txn, wallet, tokens_dicts)

        # Send every txns to All Chat
        telegram_send_message(txn_message, telegram_chat_id=CHAT_ID_ALERTS_ALL)
        log_txns.info(txn_message)

        # Send filtered txns to Filtered Chat
        if check_txn(txn, tokens_dicts):
            telegram_send_message(txn_message, telegram_chat_id=CHAT_ID_ALERTS)
