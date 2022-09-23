from argparse import ArgumentParser
from src import __version__


# Create CLI interface
parser = ArgumentParser(
    usage="python3 %(prog)s [MODE] [ADDRESSES]\n",
    description="Screens specified blockchain wallets and notifies when a new transaction occurs. "
                "Visit https://github.com/ivandimitrovkyulev/CryptoWallets.git for more info.",
    epilog=f"Version - {__version__}",
)

parser.add_argument(
    "-s", "--subprocess", action="store", type=str, nargs=1, metavar="\b", dest="sub",
    help=f"Creates a subprocess with 'subprocess.Popen' to scrape each wallet address individually."
)

parser.add_argument(
    "-m", "--multiprocess", action="store", type=str, nargs=1, metavar="\b", dest="multi",
    help=f"Creates a multiprocessing pool of wallet addresses to scrape with concurrency."
)

parser.add_argument(
    "-v", "--version", action="version", version=__version__,
    help="Prints the program's current version."
)

# Parse arguments
args = parser.parse_args()
