import os
import sys
import json
import time

from atexit import register
from multiprocessing import Process

from src.cryptowallets.datatypes import Wallet
from src.cryptowallets.debank import scrape_wallets
from src.cryptowallets.common.exceptions import exit_handler
from src.cryptowallets.common.helpers import (
    print_start_message,
    send_pin_message,
)


def start_tor():
    """Starts a Tor client"""
    os.system("nohup tor")


if __name__ == "__main__":

    if len(sys.argv) != 2:
        sys.exit(f"Usage: python3 {os.path.basename(__file__)} <input_file>\n")

    # Send telegram debug message if program terminates
    program_name = os.path.abspath(os.path.basename(__file__))
    register(exit_handler, program_name)

    # Fetch variables
    info: dict = json.loads(sys.argv[-1])
    loop_sleep, request_sleep = info["settings"].values()

    wallets_info = [Wallet(address, info['wallets'][address]['name']) for address in info['wallets']]

    tor = Process(target=start_tor)
    wallets = Process(target=scrape_wallets, args=(wallets_info,loop_sleep, ))

    # Start Process 1 - Tor
    tor.start()
    print(f"Starting Tor onion router...")

    time.sleep(30)  # Wait for Tor to initialise

    # Start Process 2 - Main wallet screener
    wallets.start()
    print_start_message(info)
    send_pin_message(info)
