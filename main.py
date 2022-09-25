import os
import sys
import json
import time
import asyncio

from atexit import register
from datetime import datetime
from copy import deepcopy

from src.cryptowallets.datatypes import Wallet
from src.cryptowallets.debank import (
    get_last_txns,
    gather_funcs,
)
from src.cryptowallets.compare import (
    compare_lists,
)
from src.cryptowallets.common.exceptions import exit_handler
from src.cryptowallets.common.helpers import print_start_message
from src.cryptowallets.common.variables import time_format


if len(sys.argv) != 2:
    sys.exit(f"Usage: python3 {os.path.basename(__file__)} <input_file>\n")

# Send telegram debug message if program terminates
program_name = os.path.abspath(os.path.basename(__file__))
#register(exit_handler, program_name)

# Fetch variables
info: dict = json.loads(sys.argv[-1])
sleep_time = info["settings"]['sleep_time']

timestamp = datetime.now().astimezone().strftime(time_format)
print_start_message(info, timestamp)


wallets = [Wallet(address, info['wallets'][address]['name']) for address in info['wallets']]
args = [[wallet] for wallet in wallets]

data = list(asyncio.run(gather_funcs(get_last_txns, args)))
old_txns = [[item['history_list'], item['token_dict']] for item in data]

loop_counter = 1
while True:
    # Wait for new transaction to appear
    start = time.perf_counter()
    time.sleep(sleep_time)

    data = list(asyncio.run(gather_funcs(get_last_txns, args)))
    new_txns = [[item['history_list'], item['token_dict']] for item in data]

    # Iterate through all wallets
    for i, txns in enumerate(zip(new_txns, old_txns)):

        new_txn, old_txn = txns  # Unpack new and old txns

        new_history_list, new_token_dict = new_txn  # Unpack new history list & token dictionary
        old_history_list, old_token_dict = old_txn  # Unpack old history list & token dictionary
        wallet = wallets[i]  # Get wallet data

        # If empty list returned - no point to compare
        if len(new_history_list) == 0:
            continue

        # If new txns found - check them for spam
        found_txns = compare_lists(new_history_list, old_history_list)

        if found_txns:
            pass  # history_list, wallet, tokens_dicts

        # Save latest txn data in old_txns
        old_txns[i] = deepcopy(new_txns[i])

    timestamp = datetime.now().astimezone().strftime(time_format)
    print(f"{timestamp} - Loop {loop_counter} executed in {(time.perf_counter() - start):,.2f} secs.")
    loop_counter += 1
