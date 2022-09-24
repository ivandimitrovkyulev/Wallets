from argparse import ArgumentParser
from src.cryptowallets import __version__


# Create CLI interface
parser = ArgumentParser(
    usage="python3 %(prog)s [ADDRESSES]\n",
    description="Screens specified blockchain wallets and notifies when a new transaction occurs. "
                "Visit https://github.com/ivandimitrovkyulev/Wallets.git for more info.",
    epilog=f"Version - {__version__}",
)

parser.add_argument(
    "-v", "--version", action="version", version=__version__,
    help="Prints the program's current version."
)

# Parse arguments
args = parser.parse_args()
