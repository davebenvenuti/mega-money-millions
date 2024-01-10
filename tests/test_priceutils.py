import unittest
from mega_money_millions.priceutils import combine_prices
import pandas as pd
from tests import BTC_PICKLE_PATH, ETH_PICKLE_PATH


class TestPortfolio(unittest.TestCase):
  def setUp(self):
    self.btc_prices = pd.read_pickle(BTC_PICKLE_PATH)
    self.eth_prices = pd.read_pickle(ETH_PICKLE_PATH)

  def test_combine_prices(self):
    prices = combine_prices(self.btc_prices, self.eth_prices)

    btc_prices = self.btc_prices.set_index([self.btc_prices.index, 'ticker'])
    eth_prices = self.eth_prices.set_index([self.eth_prices.index, 'ticker'])

    self.assertTrue(btc_prices.equals(prices.loc[prices.index.get_level_values('ticker') == 'BTC']))
    self.assertTrue(eth_prices.equals(prices.loc[prices.index.get_level_values('ticker') == 'ETH']))
