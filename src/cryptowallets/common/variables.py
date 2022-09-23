"""
Set up program variables.
"""
import os
from dotenv import load_dotenv


load_dotenv()
# Get env variables
TOKEN = os.getenv("TOKEN")
CHAT_ID_ALERTS = os.getenv("CHAT_ID_ALERTS")
CHAT_ID_DEBUG = os.getenv("CHAT_ID_DEBUG")
CHAT_ID_SPECIAL = os.getenv("CHAT_ID_SPECIAL")


time_format = "%Y-%m-%d %H:%M:%S, %Z"

log_format = "%(asctime)s - %(levelname)s - %(message)s"

# Name of HTML element to scrape
table_element_name = "History_tableLine__3dtlF"
table_element_id = "History_table__9zhFG"

# Amount of time to sleep after each scrape
sleep_time = 120

# Time to wait for page to respond
request_wait_time = 20

# Max time to wait for page to respond
max_request_wait_time = 30

# List of strings to ignore if contained in the transaction info
ignore_list = (
    '0x0000…0000',
    'play888.io',
    '1 Unknown NFT',
    '4Gambling.io',
)
ignore_list_type = (
    'claim',
    'getreward',
)
ignore_list_swap = (
    '#',
    'nft',
    'variabledebt',
)
