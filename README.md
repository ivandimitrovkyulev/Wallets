CryptoWallets
===============
### version 0.1.0

-----------------------------------------------------------------------------------------------------

Screener that follows specified blockchain wallets and notifies when a new transaction occurs via Telegram message.
<br>This relies entirely on <a href="https://debank.com/">DeBank</a> for data all retrieval.
<br>

### Installation

This project uses **Python 3.10** and <a href="https://www.torproject.org/about/history/">**Tor onion router**</a>.

Clone the project:
```shell
git clone https://github.com/ivandimitrovkyulev/CryptoWallets.git

cd CryptoWallets
```

Activate virtual environment and install all third-party project dependencies
```shell
poetry shell

poetry install
```

<br>Then install tor by following this link: https://community.torproject.org/onion-services/setup/install/


You will also need to save the following variables in a **.env** file in **./Wallets**:
```dotenv
TOKEN=<telegram-token-for-your-bot>

CHAT_ID_ALERTS=<id-of-telegram-chat-for-alerts>
CHAT_ID_ALERTS_ALL=<id-of-telegram-chat-for-special-alerts>
CHAT_ID_DEBUG=<id-of-telegram-chat-for-debugging-chat>

TOR_PASSWORD=<tor-password>
```

### Running the script

Create **wallets.json** file with addresses of the following structure, where **name** is the name of the address to screen for, **chat_id** is the Telegram chat to send transactions to:

```json
{   
    "settings": {"loop_sleep": 5, "whale_txn_limit":  100000},
    "wallets": {
        "0pa4fc4ec2f81a4897743c5b4f45907c02ce06s119": {
            "name": "wallet1",
            "chat_id": ""
            },
        "0xg9e025a1363373e48da72f5e4f6eb7cddf2f3101": {
            "name": "wallet2",
            "chat_id": ""
            },
        "0xda86d5t519dbfe34a25eef0923b259ab07986a52": {
            "name": "wallet3",
            "chat_id": ""
            }
    }
}
```

Configure your torrc file. On MacOS it is located in: **/usr/local/etc/tor** <br>
Unhash the following lines:
```shell
ControlPort 9051
HashedControlPassword 16:4BF9B2165F77FADG60C55120EC84BA0237A810FFACF67F8A9310E570G4
CookieAuthentication 1
```
Create a password and update torrc file:
```shell
tor --hash-password <your-tor-password>
# Should print the following format: 
# 16:575E816B529092446013A0AB974300E16B0A5543B73271E1FB1708CCEC
```
Then update HashedControlPassword in your torrc file and save. <br>
Finally, add your HashedControlPassword to TOR_PASSWORD in your directory's **.env** file.

<br>

Then start the script:
```shell
python3 main.py "$(cat wallets.json)"
```
Telegram alert message looks like the following:
```text
-> 2022-10-31 01:54:59, GMT
0xf28a...cdb0 on Eth from Wallet1
Stamp:  2022-10-31 01:19:59, UTC
Type: Uniswap, 1inch
Send: 2,500.00 USDT($2,500.00)
Receive: 109,330.67 WCI($2,434.80)
```

### Docker deployment

Copy your torrc file in your project's directory.
<br>
Then build a docker image named **wallets**:
```shell
docker build . -t wallets
```

Start a docker container, named **wallets**:
```shell
docker run --name="wallets" "wallets" python3 main.py "$(cat wallets.json)"
```

Additionally you can run **container_check.py** to monitor whether the docker container is running as expected. It sends error notifications to CHAT_ID_DEBUG if container has stopped. Also, every 12hours sends an alert to show it script itself is running and container's last execution loop.

```shell
# copy .env file first
docker cp wallets:/wallets/.env . | chmod go-rw .env

# then start script in the background
nohup python3 container_check.py wallets &
```

<br/>
Email: <a href="mailto:ivandkyulev@gmail.com">ivandkyulev@gmail.com</a>