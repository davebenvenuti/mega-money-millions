def add_ranking(prices, on_stat, to_stat, threshold=None):
  prices[to_stat] = prices.groupby('time')[on_stat].rank(method='dense', ascending=False)
  if threshold is not None:
    prices[f'Past{to_stat}Threshold'] = prices[to_stat] <= threshold


def unique_dates(prices):
  return prices.index.get_level_values('time').unique()


def add_filter(prices, on_stat, to_stat, threshold_column='SMA45'):
  for date in unique_dates(prices):
    values_for_date = prices.loc[(date, on_stat)]
    prices.loc[date, to_stat] = values_for_date['close'] >= values_for_date[threshold_column]
