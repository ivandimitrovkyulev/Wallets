"""
Configure Chrome settings and initiate it.
"""
from atexit import register

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service

from src.common.driver.options import (
    CHROME_LOCATION,
    options,
)

# Open Chromium web driver
chrome_driver = Chrome(service=Service(CHROME_LOCATION), options=options)

# Quit chrome driver after whole script has finished execution
register(chrome_driver.quit)
