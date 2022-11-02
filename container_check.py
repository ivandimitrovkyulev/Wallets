"""
Program that constantly checks if a docker container is running.
It checks the Loop timestamps and notifies vie Telegram if the last timestamp was older than 15 mins.
"""
import os
import re
import sys
import time
import datetime
import requests
from atexit import register


def telegram_send_message(message_text: str, teleg_chat_id: str,
                          teleg_token: str) -> requests.Response or None:
    """Sends a Telegram message to a specified chat."""

    message_text = str(message_text)

    if teleg_token == "":
        raise Exception("Invalid Telegram Token!")

    if teleg_chat_id == "":
        raise Exception("Invalid Telegram Chat ID!")

    # construct url using token for a sendMessage POST request
    url = f"https://api.telegram.org/bot{teleg_token}/sendMessage"

    # Construct data for the request
    payload = {"chat_id": teleg_chat_id, "text": message_text,
               "disable_web_page_preview": False, "parse_mode": "HTML"}

    # send the POST request
    try:
        # If too many requests, wait for Telegram's rate limit
        while True:
            post_request = requests.post(url=url, data=payload, timeout=15)

            if post_request.json()['ok']:
                return post_request

            time.sleep(3)

    except ConnectionError:
        return None


if len(sys.argv) != 2:
    sys.exit(f"Usage: python3 {os.path.basename(__file__)} <container_name>\n")


env_text = os.popen("cat .env").read()
values = [val for val in env_text.split("\n") if val != ""]
env_vals = {}
for val in values:
    buff = val.split("=")
    if len(buff) == 2:
        env_vals[f"{buff[0]}"] = buff[1]

chat_id_alerts = env_vals['CHAT_ID_ALERTS']
chat_id_alerts_all = env_vals['CHAT_ID_ALERTS_ALL']
chat_id_debug = env_vals['CHAT_ID_DEBUG']
token = env_vals['TOKEN']

current_dir = os.getcwd()
time_format = "%Y-%m-%d %H:%M:%S, %Z"
time_format_regex = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}, [A-Za-z]*")
program_name = os.path.abspath(os.path.basename(__file__))
program_start_time = datetime.datetime.now()

container_name = sys.argv[-1]
register(telegram_send_message, f"⚠️ <b>{container_name.upper()}: container_check.py</b> stopped!",
         chat_id_debug, token)

wait_time = 5 * 60  # 5 mins (5 * 60 secs) sleep time in each loop
max_time_diff = 10 * 60  # 5 mins max difference(in secs) between current and script's last timestamp
update_time = 12  # 12 hour check 'OK' message to Telegram to notify container_check is still running

# Sleep before starting the script - 15 mins
time.sleep(15 * 60)


while True:
    # Get timestamp of last execution loop
    command = f"docker logs {container_name} | tail -n 50"
    output = os.popen(command).read()

    # Find last Loop timestamp
    time_str = time_format_regex.findall(output)[-1]

    # Construct date_time object from string
    script_time = datetime.datetime.strptime(time_str, time_format)

    now_time = datetime.datetime.now()

    # Calculate time difference in seconds
    time_diff = (now_time - script_time).seconds

    # Calculate last loop execution time
    temp = re.split(r"[ ]?sec[s]?", output)[0]
    loop_time = float(re.split(r" ", temp)[-1])

    # Alert if container has stopped or is lagging behind
    if time_diff > max_time_diff:

        timestamp = datetime.datetime.now().astimezone().strftime(time_format)
        message = f"<b>⚠️ {container_name.upper()}</b> - {timestamp}\n" \
                  f"<b>{program_name}</b> stopped!\n Last loop time: {loop_time:,.2f} secs.\n"

        # Send Telegram message in Alerts and Debug Chat and Break
        telegram_send_message(message, teleg_chat_id=chat_id_alerts, teleg_token=token)
        telegram_send_message(message, teleg_chat_id=chat_id_alerts_all, teleg_token=token)
        telegram_send_message(message, teleg_chat_id=chat_id_debug, teleg_token=token)

        break

    # Alert every 12hours if the script is still running
    if now_time - program_start_time > datetime.timedelta(hours=update_time):
        message = f"✅ {container_name.upper()}. Last loop time: {loop_time:,.2f} secs."

        # Send Telegram message in Debug Chat
        telegram_send_message(message, teleg_chat_id=chat_id_debug, teleg_token=token)
        program_start_time = datetime.datetime.now()

    time.sleep(wait_time)
