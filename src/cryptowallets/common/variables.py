"""
Set up program variables.
"""
import os
from dotenv import load_dotenv

from aiohttp import ClientTimeout
from urllib3 import Retry
from requests import Session
from requests.adapters import HTTPAdapter


load_dotenv()
# Get env variables
TOKEN = os.getenv("TOKEN")
CHAT_ID_ALERTS = os.getenv("CHAT_ID_ALERTS")
CHAT_ID_DEBUG = os.getenv("CHAT_ID_DEBUG")

# Set up and configure requests session
http_session = Session()
retry_strategy = Retry(total=2, status_forcelist=[429, 500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry_strategy)
http_session.mount("https://", adapter)
http_session.mount("http://", adapter)
# Configure aiohttp timeout
timeout_class = ClientTimeout(total=3)

time_format = "%Y-%m-%d %H:%M:%S, %Z"
log_format = "%(asctime)s - %(levelname)s - %(message)s"

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

chains = {
    'eth': 'https://etherscan.io/tx/',
    'op': 'https://optimistic.etherscan.io/tx/',
    'arb': 'https://arbiscan.io/tx/',
    'bsc': 'https://bscscan.com/tx/',
    'avax': 'https://snowtrace.io/tx/',
    'matic': 'https://polygonscan.com/tx/',
    'aurora': 'https://aurorascan.dev/tx/',
    'cro': 'https://cronoscan.com/tx/',
}
