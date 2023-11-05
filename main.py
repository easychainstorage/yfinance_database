import argparse
import requests
import datetime as dt

import yfinance as yf
from bs4 import BeautifulSoup
import pandas as pd


def get_symbols(url):
    """Get currency pair from yahoo website."""
    response = requests.get(url)
    if response.status_code == 200:
        html_doc = response.text
        soup = BeautifulSoup(html_doc, "html.parser")

        symbols = [
            symbol["title"].replace("/", "")
            for symbol in soup.find_all("a", {"data-test": "quoteLink"})
        ]
        return symbols
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        return None


def get_prices(symbol):
    """Get prices 1year period"""
    return yf.Ticker(f"{symbol}=X").history(period="1y")


def main(yahoo_link, rates, currency):
    """Function to create jsonl file to dump to sqlite3 database."""
    symbols = get_symbols(yahoo_link)
    if not symbols:
        print(f"Bad url link.")
        return None
    df_exchange_rate = pd.DataFrame()
    df_currency = []
    for symbol in symbols:
        price = get_prices(symbol)
        price.reset_index(inplace=True)
        price["base_currency"] = symbol[:3]
        price["target_currency"] = symbol[3:]
        price["currency_pair"] = symbol[:3] + "/" + symbol[3:]
        price["date"] = price["Date"].dt.strftime("%Y-%m-%d")
        price["rate"] = price["Close"]
        df_exchange_rate = pd.concat([df_exchange_rate, price], ignore_index=True)
        currency_row = {
            "model": f"currency.{currency}",
            "fields": {
                "symbol": symbol[:3] + "/" + symbol[3:],
                "base_currency": symbol[:3],
                "target_currency": symbol[3:],
            },
        }
        df_currency.append(currency_row)

    df_with_fields = []
    for index, row in df_exchange_rate[["currency_pair", "date", "rate"]].iterrows():
        fields = dict()
        for key, value in row.items():
            fields[key] = value
        df_with_fields.append({"fields": fields})

    df = pd.DataFrame(df_with_fields)
    df["model"] = f"currency.{rates}"
    df.to_json("historical_rates.jsonl", lines=True, orient="records")
    pd.DataFrame(df_currency).to_json(
        "list_pairs_currency.jsonl", lines=True, orient="records"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--yahoo_link",
        default="https://finance.yahoo.com/currencies",
        help="Link to list currencies in yahoo finance.",
    )
    parser.add_argument(
        "--rates",
        default="ExchangeRate",
        help="Name of model in Django for historical rates.",
    )
    parser.add_argument(
        "--currency",
        default="Currency",
        help="Name of model in Django for list of currencies.",
    )
    args = parser.parse_args()
    main(args.yahoo_link, args.rates, args.currency)
