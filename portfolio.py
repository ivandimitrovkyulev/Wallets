import os
import sys
import requests
import pandas as pd


def chain_holdings(address: str, chain: str, min_value: float = 1.0) -> pd.DataFrame:
    """
    Returns address portfolio tokens for a specified chain.

    :param address: Wallet address, eg. 0xsa76d57519dbfe34a25eef1923b259ab05986b26
    :param chain: Which blockchain to display tokens from
    :param min_value: Min USD value below which not to display tokens
    :returns: Pandas DataFrame sorted by ascending USD values
    """
    api = f"https://api.debank.com/token/balance_list?user_addr={address}" \
          f"&is_all=false&chain={chain}"

    resp = requests.get(api, timeout=10)
    resp_data = resp.json()

    if resp.status_code == 200:
        if resp_data['error_code'] == 0:
            data = resp_data['data']
        else:
            raise Exception(f"Response Data not returned. Error message: {resp_data['error_msg']}")
    else:
        raise Exception(f"Could not request data for {api}")

    portfolio = []
    for item in data:
        holding = {}
        holding['name'] = item['name']
        holding['symbol'] = item['optimized_symbol']
        holding['balance'] = round(item['balance'] / 10 ** item['decimals'], 4)
        holding['usd_price'] = item['price']
        holding['value'] = holding['balance'] * holding['usd_price']
        portfolio.append(holding)

    total_value = sum([item['value'] for item in portfolio])
    data = [[i['name'], i['balance'], i['value'], i['value'] / total_value * 100]
            for i in portfolio if i['value'] >= min_value]

    rows = range(1, len(data) + 1)
    columns = ['Token', 'Balance', 'Value in $USD', 'Percentage']

    pd.options.display.float_format = '{:,.2f}'.format

    df = pd.DataFrame(data, columns=columns)
    df.sort_values('Value in $USD', inplace=True, ascending=False)
    df.index = rows

    df['Balance'] = [f"{val:,.2f}" for val in df['Balance']]
    df['Value in $USD'] = [f"${val:,.2f}" for val in df['Value in $USD']]
    df['Percentage'] = [f"{val:,.2f}%" for val in df['Percentage']]

    return df


if __name__ == "__main__":

    if len(sys.argv) != 3:
        sys.exit(f"Usage: python3 {os.path.basename(__file__)} <address> <chain_name>\n")

    wallet_address = sys.argv[1]
    chain_name = sys.argv[2]

    holdings = chain_holdings(wallet_address, chain_name)

    print(holdings)
