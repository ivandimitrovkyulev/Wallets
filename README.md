<h1>CryptoWallets</h1>
<h3>version 1.0.0</h3>

Screener that follows specified blockchain wallets and notifies when a new transaction occurs via Telegram message.

<br> 

## Installation

This project uses **Python 3.9.6** and requires a
[Chromium WebDriver](https://chromedriver.chromium.org/getting-started/) installed.

Clone the project:
```
git clone https://github.com/ivandimitrovkyulev/CryptoWallets.git

cd CryptoWallets
```

Create a virtual environment in the current working directory and activate it:

```
python3 -m venv <current-directory>

source <current/directory>/bin/activate
```

Install all third-party project dependencies:
```
pip install -r requirements.txt
```

You will also need to save the following variables in a **.env** file in ../CryptoWallets:
```
CHROME_LOCATION=<your/web/driver/path/location> 

TOKEN=<telegram-token-for-your-bot>

CHAT_ID_ALERTS=<id-of-telegram-chat-for-alerts>

CHAT_ID_DEBUG=<id-of-telegram-chat-for-debugging>

CHAT_ID_SPECIAL=<id-of-telegram-chat-for-special-alerts>
```
<br/>

## Running the script
<br/>

Create a **wallets.json** file with addresses of the following structure, where **name** is the name of the address to be screened, **chat_id** is the Telegram chat to send transactions to of this specific address:

```
{
    "0xb62530ee059c17caf3c82300b44aa9813cb0731f6": {
        "name": "CoinBase",
        'chat_id': ''
    },
    "0xg55e4b5d659a7fhb0d6eb52lp515f4833cf211gy": {
        "name": "Binance",
        'chat_id': ''
    },
    "0xju67d57519dbff34a28eef0923b259ab07985d33": {
        "name": "Crypto.com",
        'chat_id': ''
    }
}
```
Save the contents of the **wallets.json** file in a variable:
```
var="$(cat wallets.json)"
```
To start screening addresses in a multiprocessing mode by passing addresses to **main.py**:
```
python main.py -m "$var"
```
To start screening addresses in a subprocessing mode by passing addresses to **main.py**:
```
python main.py -s "$var"
```
**Difference between subprocessing and multiprocessing:**
<br>
Subprocessing runs a separate Python program for each address in the list and it is completely separated from the rest.
Multiprocessing runs in the same script but with different processes concurently within. This means that processes are not completely isolated and if, for example, DeBank does not return any response to one address the whole script will get stucked. 

<br/>

## Docker deployment
<br/>

Build a docker image named **wallet-scrape**:
```
cd CryptoWallets
docker build . -t <image-name>
```
Run docker container:
```
var="$(cat wallets.json)"

docker run --shm-size="2g" -it <image-id> python3 main.py <mode> "$var"  
```

where **--shm-size="2g"** docker argument is provided to prevent Chromium from the **"from tab crashed"** error.

<br>

Or to run an individual container for a single address:
```
docker run --shm-size="2g" -it <image-id> python3 -m src.individual.scrape <address> <name>
```

Or run all containers in **wallets.json** individually, where each wallet gets its own container:
```
python3 run_containers.py wallets.json
```
To stop all containers at once:
```
docker kill $(docker ps -q)
```

<br/>
<br/>

Email: ivandkyulev@gmail.com