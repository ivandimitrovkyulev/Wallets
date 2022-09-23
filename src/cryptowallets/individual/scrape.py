import os
import sys
from datetime import datetime
from atexit import register

from src.common.exceptions import exit_handler_driver
from src.common.variables import (
    request_wait_time,
    max_request_wait_time,
    sleep_time,
)

from src.sub_process.single_scrape import scrape_single_wallet
from src.common.variables import (
    table_element_name,
    table_element_id,
    time_format,
)


# Argument count
arg_len = len(sys.argv)

if arg_len < 3 or arg_len > 4:
    sys.exit("Please provide 2-3 arguments: [Address], [Name], [OPTIONAL Chat_id].")

address = str(sys.argv[1])
name = str(sys.argv[2])
# If chat_id not provided get from .env file by providing empty string
try:
    chat = str(sys.argv[3])
except IndexError:
    chat = ""


# Import chrome driver if args are correct
from src.common.driver.driver import chrome_driver

# Register function to be executed when script terminates
timestamp = datetime.now().astimezone().strftime(time_format)
program_name = os.path.basename(__file__)
register(exit_handler_driver, chrome_driver, program_name, "", f"Container for [{address}, {name}] has stopped.")

print(f"{timestamp} - {program_name} has started screening:\n"
      f"Address: {address}, Name: {name}")

# Get page to scrape
chrome_driver.get(f"https://debank.com/profile/{address}/history")

# Start screening single wallet address
scrape_single_wallet(driver=chrome_driver,
                     element_name=table_element_name,
                     element_id=table_element_id,
                     wallet_name=name,
                     chat_id=chat,
                     time_to_sleep=sleep_time,
                     wait_time=request_wait_time,
                     max_wait_time=max_request_wait_time)
