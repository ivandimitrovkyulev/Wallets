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
    'eth': 'https://etherscan.io/tx/',
    'op': 'https://optimistic.etherscan.io/tx/',
    'arb': 'https://arbiscan.io/tx/',
    'bsc': 'https://bscscan.com/tx/',
    'avax': 'https://snowtrace.io/tx/',
    'matic': 'https://polygonscan.com/tx/',
    'aurora': 'https://aurorascan.dev/tx/',
    'cro': 'https://cronoscan.com/tx/',
}
