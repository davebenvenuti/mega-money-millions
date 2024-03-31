import pandas as pd
from functools import reduce


def __is_valid_single_ticker_df(prices):
  return 'ticker' in prices and len(prices['ticker'].unique()) == 1

def __is_valid_multi_ticker_df(prices):
  if not isinstance(prices.index, pd.MultiIndex):
    return False

  if not [pd.core.indexes.datetimes.DatetimeIndex, pd.core.indexes.base.Index] == [*map(type, prices.index.levels)]:
    return False

  return ['time', 'ticker'] == [*map(lambda x: x.name, prices.index.levels)]

def __combine_single_with_single(prices1, prices2):
  return prices1.set_index([prices1.index, 'ticker']).combine_first(prices2.set_index([prices2.index, 'ticker']))

def __combine_single_with_multi(single_prices, multi_prices):
  return multi_prices.combine_first(single_prices.set_index([single_prices.index, 'ticker']))

def __combine_multi_with_multi(prices1, prices2):
  return prices1.combine_first(prices2)

__VALIDATION_ERROR_MESSAGE = """
prices must either be a single-security dataframe with a 'ticker' column or a multi-security dataframe with a MultiIndex
of ('time', 'ticker')
"""

def ensure_correct_dtypes(combined_prices):
  new_prices = combined_prices.copy()
  for column in ['close', 'open', 'high', 'low', 'volume']:
    new_prices[column] = new_prices[column].astype('float')

  new_prices['complete'] = new_prices['complete'].astype('boolean')

  return new_prices

def combine_prices(prices1, prices2):
  prices1_is_single, prices_1_is_multi = __is_valid_single_ticker_df(prices1), __is_valid_multi_ticker_df(prices1)
  prices2_is_single, prices_2_is_multi = __is_valid_single_ticker_df(prices2), __is_valid_multi_ticker_df(prices2)

  if (not prices1_is_single and not prices_1_is_multi) or (not prices2_is_single and not prices_2_is_multi):
    raise ValueError(__VALIDATION_ERROR_MESSAGE)

  if prices1_is_single:
    if prices2_is_single:
      combined = __combine_single_with_single(prices1, prices2)
    else:
      combined = __combine_single_with_multi(prices1, prices2)
  else:
    if prices2_is_single:
      combined = __combine_single_with_multi(prices2, prices1)
    else:
      combined = __combine_multi_with_multi(prices1, prices2)

  return ensure_correct_dtypes(combined)
