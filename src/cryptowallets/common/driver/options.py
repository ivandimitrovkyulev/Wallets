"""
Configure Chrome settings and initiate it.
"""
import os
from dotenv import load_dotenv

from selenium.webdriver.chrome.options import Options


load_dotenv()
# Get env variables
CHROME_LOCATION = os.getenv('CHROME_LOCATION')

# Chrome driver options
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--disable-dev-shm-usage')
