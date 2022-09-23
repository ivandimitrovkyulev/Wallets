"""
Main script that screens specified blockchain wallets and notifies when a new transaction occurs.
Visit https://github.com/ivandimitrovkyulev/CryptoWallets.git for more info.
"""
import os
import sys
import json

from datetime import datetime
from atexit import register

from src.common.exceptions import exit_handler_program
from src.cli.interface import (
    args,
    parser,
)
from src.common.variables import time_format


timestamp = datetime.now().astimezone().strftime(time_format)
program_name = os.path.basename(__file__)


# If no arguments provided - print help and exit
if len(sys.argv) < 2:
    sys.exit(parser.print_help())

try:
    # Read argument and convert it into a dictionary
    address_dict = json.loads(sys.argv[-1])

    try:
        # Construct message for terminal info
        addresses = ""
        for index, address in enumerate(address_dict):
            wallet_name = address_dict[address]['name']
            addresses += f"{index + 1}. {address}, {wallet_name}\n"

        address_message = f"Started screening the following addresses:\n" \
                          f"{addresses}"
    except Exception as e:
        sys.exit(f"Invalid [ADDRESSES] argument - {e}")

except Exception as e:
    sys.exit(f"Invalid [ADDRESSES] argument - {e}")


# If subprocessing
if args.sub:
    # Import module
    from src.sub_process.scrape import scrape_wallets_subprocess

    message = f"{timestamp} - {program_name} - subprocessing has started\n"
    print(message + address_message)

    # Infinite scraping. Keyboard interrupt to stop.
    scrape_wallets_subprocess(address_dict=address_dict)

# If multiprocessing
elif args.multi:
    # Import module
    from src.common.driver.driver import chrome_driver
    from src.multi_process.scrape import scrape_wallets_multiprocess
    from src.common.variables import (
        table_element_name,
        table_element_id,
        sleep_time,
        request_wait_time,
        max_request_wait_time,
    )

    program_name += " multiprocessing"
    # Register function to be executed if script terminates
    register(exit_handler_program, program_name)

    message = f"{timestamp} - {program_name} - multiprocessing has started\n"
    print(message + address_message)

    # Infinite scraping. Keyboard interrupt to stop.
    scrape_wallets_multiprocess(driver=chrome_driver,
                                address_dict=address_dict,
                                element_name=table_element_name,
                                element_id=table_element_id,
                                time_to_sleep=sleep_time,
                                wait_time=request_wait_time,
                                max_wait_time=max_request_wait_time,
                                infinite=False)
