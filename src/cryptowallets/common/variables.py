"""
Set up program variables.
"""
import os
from dotenv import load_dotenv


load_dotenv()
# Get env variables
TOKEN = os.getenv("TOKEN")
CHAT_ID_ALERTS = os.getenv("CHAT_ID_ALERTS")
CHAT_ID_ALERTS_ALL = os.getenv("CHAT_ID_ALERTS_ALL")
CHAT_ID_DEBUG = os.getenv("CHAT_ID_DEBUG")
TOR_PASSWORD = os.getenv("TOR_PASSWORD")


time_format = "%Y-%m-%d %H:%M:%S, %Z"
log_format = "%(asctime)s - %(levelname)s - %(message)s"


chains = {
    'eth': 'https://etherscan.io',
    'op': 'https://optimistic.etherscan.io',
    'arb': 'https://arbiscan.io',
    'bsc': 'https://bscscan.com',
    'avax': 'https://snowtrace.io',
    'matic': 'https://polygonscan.com',
    'aurora': 'https://aurorascan.dev',
    'cro': 'https://cronoscan.com',
    'heco': 'https://www.hecoinfo.com/en-us',
    'doge': 'https://explorer.dogechain.dog',
    'canto': 'https://evm.explorer.canto.io/',
}
