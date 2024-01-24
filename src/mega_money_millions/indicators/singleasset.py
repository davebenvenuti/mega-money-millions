import pandas as pd


def add_sma(prices, window, prefix='SMA'):
  prices[f'{prefix}{window}'] = prices['close'].rolling(window).mean().round(2)
  return prices


def add_roc(prices, window, prefix='ROC'):
  prices[f'{prefix}{window}'] = ((prices['close'] - prices.shift(window)['close']) /
                                 prices.shift(window)['close'] * 100)
  return prices


def add_crossover(prices, on_stat1, on_stat2, to_stat1, to_stat2):
  previous = prices.shift(1)
  prices[to_stat1] = (previous[on_stat1] > previous[on_stat2]) & (prices[on_stat1] < prices[on_stat2])
  prices[to_stat2] = (previous[on_stat1] < previous[on_stat2]) & (prices[on_stat1] > prices[on_stat2])
