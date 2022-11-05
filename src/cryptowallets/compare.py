from typing import (
    Dict,
    List,
    Tuple,
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

    except (TypeError, KeyError):
        log_error.warning(f"'compare_lists' Error - unable to compare")
        return None


def format_send_receive(txn: dict, keyword: str, chain: str, tokens_dict: Dict[str, dict]) -> list:
    """
    Formats 'sends' or 'receives' list of items for a transaction.

    :param txn: Transaction dictionary
    :param keyword: 'sends' or 'receives'
    :param chain: Chain name, eg. eth, ftm, avax
    :param tokens_dict: Dictionary with token info
    """
    keyword = keyword.lower()

    if keyword == 'sends':
        sign = '-'
    elif keyword == 'receives':
        sign = '+'
    else:
        raise Exception(f"Keyword must be 'sends' or 'receives' string.")

    txn_info = txn[keyword]
    txn_items = []

    if txn_info:
        for send in txn_info:
            amount = send['amount']
            token_id = send['token_id']
            try:
                token_url = f"{chains[chain]}/address/{token_id}"
            except KeyError:
                token_url = f"https://www.google.com/search?&rls=en&q={chain}+{token_id}&ie=UTF-8&oe=UTF-8"

            try:
                token_name = tokens_dict[token_id]['symbol']
            except KeyError:
                if len(token_id) < 42:
                    token_name = "+1 Unknown NFT"
                else:
                    token_name = "+1 Unknown Item"

                txn_items.append(f"<a href='{token_url}'>{token_name}</a>")
                continue

            try:
                token_price = tokens_dict[token_id]['price'] * amount
                token_price = f"{token_price:,.2f}"
            except (TypeError, KeyError):
                token_price = 'n/a'

            txn_items.append(f"<a href='{token_url}'>{sign}{amount:,.2f} {token_name}</a>(${token_price})")
    else:
        txn_items.append('None')

    return txn_items


def format_txn_message(txn: dict, wallet: Wallet, tokens_dict: Dict[str, dict],
                       project_dict: Dict[str, dict]) -> Tuple[str, str]:
    """
    Formats a transaction into a message string.

    :param txn: Transaction dictionary
    :param wallet: Wallet txn came from
    :param tokens_dict: Dictionary with token info
    :param project_dict: Dictionary with project info
    :return: Formatted message string
    """

    chain = str(txn['chain'])  # Shortened name of blockchain
    txn_hash = txn['id']  # Transaction hash
    formatted_txn_hash = f"{txn_hash[0:6]}...{txn_hash[-4:]}"  # eg. 0xc43c...37ea
    time_at_secs = int(txn['time_at'])  # eg. 1664049342 secs
    other_addr = txn['other_addr']  # eg. Interacted With (To):
    project_id = txn['project_id']  # Name of project if present
    token_approve = txn['token_approve']  # If token approval get data

    txn_stamp = datetime.fromtimestamp(time_at_secs, timezone.utc).strftime(time_format)

    receive_items: list = format_send_receive(txn, 'receives', chain, tokens_dict)
    send_items: list = format_send_receive(txn, 'sends', chain, tokens_dict)

    if txn['tx']:
        if txn['tx']['name']:
            txn_type = str(txn['tx']['name']).title()
        else:
            txn_type = 'Contract Interaction'
    elif txn['cate_id']:
        txn_type = str(txn['cate_id']).title()
    else:
        txn_type = 'Contract Interaction'

    if project_id:
        project_name = project_dict[project_id]['name']

        if token_approve:
            approve_token_id = txn['token_approve']['token_id']
            approve_token_name = tokens_dict[approve_token_id]['optimized_symbol']

            txn_type = f"{txn_type} {approve_token_name} on {project_name}"
        else:
            txn_type = f"{txn_type}, {project_name}"

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
              f"<a href='{txn_link}'>{formatted_txn_hash} on {chain.title()}</a> " \
              f"from <a href='{wallet_link}'>{wallet.name}</a>\n" \
              f"Stamp:  {txn_stamp}\n" \
              f"Type: <a href='{interacted_with_link}'>{txn_type}</a>\n" \
              f"Send: {', '.join(send_items)}\n" \
              f"Receive: {', '.join(receive_items)}\n"

    log_msg = f"{wallet.address}, {wallet.name} - {txn_stamp}, {formatted_txn_hash}"

    return message, log_msg


def check_txn(txn: dict, tokens_dict: Dict[str, dict], txn_message: str) -> bool:
    """
    Checks whether a transaction is Normal or Spam.

    :param txn: Transaction dictionary
    :param tokens_dict: Dictionary with token info
    :param txn_message: Log message string to save txn
    :return: True if transaction is Normal, False if Spam or Failed
    """
    try:
        status = txn['tx']['status']  # Check transaction status - 0 for Failed
        if int(status) == 0:
            log_fail.info(f"check_txn - Txn failed - {txn_message}")
            return False
    except (TypeError, KeyError):
        pass

    if len(txn['receives']) == 0 and len(txn['sends']) == 0:
        log_spam.info(f"check_txn - Txn likely an approval - {txn_message}")
        return False

    try:
        txn_type = str(txn['tx']['name']).lower()
    except (TypeError, KeyError):
        txn_type = str(txn['cate_id']).lower()

    for receive in txn['receives']:
        token_id = receive['token_id']
        nft_error_msg = f"check_txn - Txn likely an NFT - {txn_message}"

        # If token_id len is less than 42 -> likely a spam NFT
        if len(token_id) < 42:
            log_spam.info(nft_error_msg)
            return False

        if 'receive' in txn_type:
            # Get token ID
            is_verified = tokens_dict[token_id]['is_verified']
            if not is_verified:
                log_spam.info(nft_error_msg)
                return False

    return True


def alert_txns(txns: List[dict], wallet: Wallet, tokens_dict: Dict[str, dict],
               project_dict: Dict[str, dict]) -> None:
    """
    Alerts for any matching transactions via Telegram message.

    :param txns: Transaction dictionary
    :param wallet: Wallet txn came from
    :param tokens_dict: Dictionary with token info
    :param project_dict: Dictionary with project info
    """

    for txn in txns:

        # If nothing returned - continue
        if not txn or len(txn) == 0:
            continue

        telegram_msg, log_msg = format_txn_message(txn, wallet, tokens_dict, project_dict)

        # Send every new txn to All Chat
        telegram_send_message(telegram_msg, telegram_chat_id=CHAT_ID_ALERTS_ALL)
        log_txns.info(log_msg)

        # Send filtered txns to Filtered Chat
        if check_txn(txn, tokens_dict):
            telegram_send_message(telegram_msg, telegram_chat_id=CHAT_ID_ALERTS)
