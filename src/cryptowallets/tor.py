"""
torrc file located at /usr/local/etc/tor on mac.
"""
from stem import Signal
from stem.control import Controller
from fake_useragent import UserAgent
from requests import Session, session

from src.cryptowallets.common.variables import TOR_PASSWORD


headers = {"User_Agent": UserAgent(verify_ssl=False).random}


def change_ip(password: str = "", port: int = 9051) -> float:
    """
    Changes your IP address and returns Tor's NEWNYM wait time.

    :param password: Controller authentication password. No password by default
    :param port: Port number, defaults to 9050
    :returns: Number of seconds until a new NEWNYM can be requested
    """
    if password == "":
        password = TOR_PASSWORD

    with Controller.from_port(port=port) as controller:
        controller.authenticate(password=password)
        controller.signal(Signal.NEWNYM)
        secs = controller.get_newnym_wait()
        controller.close()

    return secs


def get_tor_session(port: int = 9050) -> Session:
    """
    Create a new socks5h:// configured Tor session.

    :param port: Port number, defaults to 9050
    :return: Session instance
    """

    tor_session = session()
    tor_session.proxies = {f'http': f'socks5h://localhost:{port}',
                           f'https': f'socks5h://localhost:{port}'}

    return tor_session