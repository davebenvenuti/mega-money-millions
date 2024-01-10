import pandas as pd
from functools import reduce

def __validate(*prices):
  for ticker_prices in prices:
    if 'ticker' not in ticker_prices:
      raise ValueError("prices must contain a 'ticker' column")

    if len(ticker_prices['ticker'].unique()) != 1:
      raise ValueError("prices must contain a single ticker")


def combine_prices(prices1, prices2):
  __validate(prices1, prices2)

  return prices1.set_index([prices1.index, 'ticker']).combine_first(prices2.set_index([prices2.index, 'ticker']))
