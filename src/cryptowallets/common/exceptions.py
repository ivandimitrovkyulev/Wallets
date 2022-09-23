from time import sleep
from functools import wraps
from datetime import datetime

from typing import (
    Callable,
    TypeVar,
)
from selenium.webdriver import Chrome
from selenium.common.exceptions import (
    WebDriverException,
    TimeoutException,
)

from src.common.message import telegram_send_message
from src.common.variables import time_format


# Define a Function type
Function = TypeVar("Function")


def driver_wait_exception_handler(
        wait_time: int = 10,
) -> Callable[[Function], Function]:
    """
    Decorator that infinitely re-tries to query website for information until
    the website responds. Useful when websites enforce a query limit.

    :param wait_time: Seconds to wait until refreshes pages and tries again
    :returns: Decorated function
    """

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            while True:
                try:
                    value = func(*args, **kwargs)

                except WebDriverException or TimeoutException:
                    # if unable to get WebElement - wait & repeat
                    sleep(wait_time)

                else:
                    # if able to retrieve WebElement break loop
                    break

            return value

        return wrapper

    return decorator


def exit_handler_driver(
        driver: Chrome,
        program_name: str = "",
        telegram_chat_id: str = "",
        info: str = "",
) -> None:
    """
    Sends a notification message in Telegram to notify of program termination and quits driver.

    :param driver: Web driver instance
    :param program_name: Name of running program
    :param telegram_chat_id: Telegram Chat ID to send message to
    :param info: Additional info to include in debug message
    :returns: None
    """

    timestamp = datetime.now().astimezone().strftime(time_format)

    message = f"--------------------WARNING--------------------\n" \
              f"{timestamp}: {program_name} has stopped.\n" \
              f"Please contact your administrator.\n" \
              f"{info}"

    # Send debug message in Telegram and print in terminal
    telegram_send_message(message, telegram_chat_id=telegram_chat_id, debug=True)

    print(message)

    # Quit chrome driver
    driver.quit()


def exit_handler_program(
        program_name: str = "",
        telegram_chat_id: str = "",
        info: str = "",
) -> None:
    """
    Sends a notification message in Telegram to notify of program termination.

    :param program_name: Name of running program
    :param telegram_chat_id: Telegram Chat ID to send message to
    :param info: Additional info to include in debug message
    :returns: None
    """

    timestamp = datetime.now().astimezone().strftime(time_format)

    message = f"--------------------WARNING--------------------\n" \
              f"{timestamp}: {program_name} has stopped.\n" \
              f"Please contact your administrator.\n" \
              f"{info}"

    # Send debug message in Telegram and print in terminal
    telegram_send_message(message, telegram_chat_id=telegram_chat_id, debug=True)

    print(message)
