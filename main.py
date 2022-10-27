import os
import sys
import json
import time

from atexit import register
from multiprocessing import Process

from src.cryptowallets.datatypes import Wallet
from src.cryptowallets.debank import scrape_wallets
from src.cryptowallets.common.exceptions import exit_handler
from src.cryptowallets.common.helpers import print_start_message


def start_tor():
    """Starts a Tor client"""
    os.system("tor")


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

    tor.start()  # Start Process 1 - Tor
    print(f"Starting Tor onion router...")
    time.sleep(30)  # Wait for Tor to initialise
    wallets.start()  # Start Process 2 - Main wallet screener
    print_start_message(info)
