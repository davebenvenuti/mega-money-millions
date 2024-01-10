import pandas as pd

# Expects prices DataFrame for a _SINGLE_ asset.  Mutates prices.


def add_sma(prices, window, prefix='SMA'):
  prices[f'{prefix}{window}'] = prices['close'].rolling(window).mean().round(2)
  return prices

# Expects prices DataFrame for a _SINGLE_ asset.  Mutates prices.


def add_roc(prices, window, prefix='ROC'):
  prices[f'{prefix}{window}'] = ((prices['close'] - prices.shift(window)['close']) /
                                 prices.shift(window)['close'] * 100)
  return prices

# Expects prices DataFrame for _ALL_ assets, indexed on (date, ticker)  Mutates prices.


def add_ranking(prices, on_stat, to_stat, threshold=None):
  prices[to_stat] = prices.groupby('time')[on_stat].rank(method='dense', ascending=False)
  if threshold is not None:
    prices[f'Past{to_stat}Threshold'] = prices[to_stat] <= threshold


def unique_dates(prices):
  return prices.index.get_level_values('time').unique()


# Expected prices Dataframe for _ALL_ assets.  Mutates prices.
def add_filter(prices, on_stat, to_stat, threshold_column='SMA45'):
  for date in unique_dates(prices):
    btc = prices.loc[(date, on_stat)]
    prices.loc[date, to_stat] = btc['close'] >= btc[threshold_column]


def to_entries_and_exits(prices, boolean_column_name, *, regime_filter=None):
  entries_and_exits = pd.DataFrame(index=prices.index)
  diff_column_name = f'{boolean_column_name}Diff'

  for ticker in prices.index.get_level_values('ticker').unique():
    entries_and_exits.loc[prices.index.get_level_values('ticker') == ticker,
                          diff_column_name] = entries_and_exits.loc[prices.index.get_level_values('ticker') == ticker,
                                                                    boolean_column_name].diff()

  if regime_filter is not None:
    raise NotImplementedError("not supported yet!")

  entries_and_exits['EntriesWithoutRegimeFilter'] = entries_and_exits[diff_column_name] == 1
  entries_and_exits['ExitsWithoutRegimeFilter'] = entries_and_exits[diff_column_name] == -1

  return entries_and_exits
