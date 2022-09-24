import re
from typing import Optional

from datetime import (
    datetime,
    timedelta,
)
from src.cryptowallets.common.logger import (
    log_spam,
    log_error,
    log_fail,
)
from src.cryptowallets.common.variables import (
    time_format,
    ignore_list,
    ignore_list_type,
    ignore_list_swap,
)


def dict_complement_b(
        old_dict: dict,
        new_dict: dict,
) -> dict:
    """
    Compares dictionary A & B and returns the relative complement of A in B.
    Basically returns all members in B that are not in A as a python dictionary -
    as in Venn's diagrams.

    :param old_dict: dictionary A
    :param new_dict: dictionary B
    :returns: Python Dictionary
    """

    b_complement = {k: new_dict[k] for k in new_dict if k not in old_dict}

    return b_complement


def format_data(
        txn: list[list, list, list, list],
        time_diff_hours: int = 3,
        time_diff_mins: int = 0,
) -> Optional[tuple[list, str]]:
    """
    Takes a list of lists with transaction data and returns formatted list of information.

    :param txn: List of lists containing txn data.
    :param time_diff_hours: Skips transactions that occurred more than specified hours ago.
    :param time_diff_mins: Skips transactions that occurred more than specified mins ago.
    :return: Optional Tuple of List with formatted data & transaction type flag
    """
    data = []
    t_flag = ''

    # If txn does not have the right structure log and return none
    if not isinstance(txn, list):
        log_error.critical(f"{txn} is not a list.")
        return
    elif len(txn) != 4:
        log_error.critical(f"{txn} length does not equal 4.")
        return
    else:
        for item in txn:
            if not isinstance(item, list):
                log_error.critical(f"{txn} is not a list of lists.")
                return

    # Un-pack data
    t_date, t_type, t_swap, t_gas = txn

    # Return 0 if transaction is Failed or 'Approve'
    if 'Failed' in t_date:
        log_fail.info(f"{txn}")
        return
    elif 'Approve' in t_type[0]:
        log_spam.info(f"{txn}")
        return

    # filter out based on other spam criteria and mark as 'spam'
    else:
        for item in t_type:
            type_info = item.lower()
            if 'receive' == type_info:
                log_spam.info(f"{txn}")
                t_flag = 'spam'
            if type_info in ignore_list_type:
                t_flag = 'spam'

        for item in t_swap:
            swap_info = item.lower()
            if swap_info in ignore_list_swap:
                t_flag = 'spam'

    # Check against unwanted transactions
    for ignore in ignore_list:
        if ignore in t_type or ignore in t_swap:
            return

    # Format txn time
    try:
        time = t_date[0]
        now = datetime.now()

        # Append timestamp
        if 'hr' in time and 'min' in time:
            stamps = re.findall("[0-9]+", time)
            hours = int(stamps[0])
            mins = int(stamps[1])

            time_stamp = now - timedelta(hours=hours, minutes=mins)

            # Append formatted time to list
            data.append(time_stamp.astimezone().strftime(time_format))

        elif 'min' in time and 'sec' in time:
            stamps = re.findall("[0-9]+", time)
            mins = int(stamps[0])
            secs = int(stamps[1])

            time_stamp = now - timedelta(minutes=mins, seconds=secs)

            # Append formatted time to list
            data.append(time_stamp.astimezone().strftime(time_format))

        elif 'sec' in time and 'min' not in time:
            stamps = re.findall("[0-9]+", time)
            secs = int(stamps[0])

            time_stamp = now - timedelta(seconds=secs)

            # Append formatted time to list
            data.append(time_stamp.astimezone().strftime(time_format))

        else:
            time_stamp = datetime.strptime(time, "%Y/%m/%d %H:%M:%S")
            data.append(time)

        # If transaction occurred more that time_difference - skip
        if now - time_stamp > timedelta(hours=time_diff_hours, minutes=time_diff_mins):
            log_spam.info(f"{txn} time is old.")
            return

    except TypeError or IndexError as e:
        # log skipped txn
        log_error.critical(f"{e}: {txn} timestamp is missing.")
        return

    # Format txn type
    try:
        txn_type = "Type: "
        for item in t_type:
            txn_type += f"{item} "
        data.append(txn_type)
    except IndexError:
        data.append(t_type)

    # Format txn amount
    if len(t_swap) == 0:
        data.append("Swap: None")
        t_flag = 'spam'
    else:
        try:
            amount = "Swap: "
            for i, item in enumerate(t_swap):
                if i % 2 == 0:
                    amount += item + t_swap[i + 1] + " "
            data.append(amount)
        except IndexError:
            data.append(t_swap)

    return data, t_flag
