import os
import sys

from atexit import register
from datetime import datetime


if len(sys.argv) != 2:
    sys.exit(f"Usage: python3 {os.path.basename(__file__)} <input_file>\n")

# Send telegram debug message if program terminates
program_name = os.path.abspath(os.path.basename(__file__))
register(exit_handler, program_name)

# Fetch variables
info: dict = json.loads(sys.argv[-1])
sleep_time, base_token = info["settings"].values()