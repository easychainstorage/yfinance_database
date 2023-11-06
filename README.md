# Yfinance_database
Python script to create jsonl files to load sqlite3 database while storing list of currency pairs and their historical rates from finance.yahoo.com/currencies 

## Installation
```
pip3 install -r requirements.txt
```
## Usage
```bash
python main.py --yahoo_link https://sg.finance.yahoo.com/currencies/ --rates_model ExchangeRate --currency_model Currency
```
```
arguments:
  --yahoo_link           Link to list currencies in yahoo finance. Like https://sg.finance.yahoo.com/currencies/, https://nz.finance.yahoo.com/currencies/ etc.
  --rates_model          Name of your model in Django for historical rates
  --currency_model       Name of your model in Django for list of currencies.
```

Example output:
 - [currency pairs](example/list_pairs_currency.jsonl)
 - [historical rates](example/historical_rates.jsonl)