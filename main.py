import os
import sys
import json
import time

from atexit import register
from datetime import datetime
from multiprocessing import Process

from src.cryptowallets.datatypes import Wallet
from src.cryptowallets.debank import scrape_wallets
from src.cryptowallets.common.exceptions import exit_handler
from src.cryptowallets.common.variables import time_format
from src.cryptowallets.common.helpers import (
    print_start_message,
    send_pin_message,
)


def start_tor(out_file_name: str):
    """Starts a Tor client"""
    os.system(f"nohup tor > {out_file_name}")


if __name__ == "__main__":

    if len(sys.argv) != 2:
        sys.exit(f"Usage: python3 {os.path.basename(__file__)} <input_file>\n")

    # Send telegram debug message if program terminates
    program_name = os.path.abspath(os.path.basename(__file__))
    register(exit_handler, program_name)
    timestamp = datetime.now().astimezone().strftime(time_format)

    # Fetch variables
    info: dict = json.loads(sys.argv[-1])
    loop_sleep, request_sleep = info["settings"].values()

    wallets_info = [Wallet(address, info['wallets'][address]['name']) for address in info['wallets']]
    out_file = "tor_output.txt"

    tor = Process(target=start_tor, args=(out_file, ))
    wallets = Process(target=scrape_wallets, args=(wallets_info,loop_sleep, ))

    # Start Process 1 - Tor
    tor.start()
    print(f"{timestamp} - Starting Tor onion router...\nAppending Tor output to {out_file}")

    time.sleep(30)  # Wait for Tor to initialise

    # Start Process 2 - Main wallet screener
    wallets.start()
    print_start_message(info)
    send_pin_message(info)
