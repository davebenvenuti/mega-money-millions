import unittest
from mega_money_millions.priceutils import combine_prices, ensure_correct_dtypes
import pandas as pd
from tests import BTC_PICKLE_PATH, ETH_PICKLE_PATH, SHIB_PICKLE_PATH, XRP_PICKLE_PATH
from pandas.testing import assert_frame_equal


class TestPortfolio(unittest.TestCase):
  # Hoops we have to jump through just to get pandas.assert_frame_equal working with unittest.  Python is a wasteland.
  def assertDataframeEqual(self, a, b, msg=None):
    try:
      assert_frame_equal(a, b)
    except AssertionError as e:
      raise self.failureException(msg) from e

  def setUp(self):
    self.addTypeEqualityFunc(pd.DataFrame, self.assertDataframeEqual)

    self.btc_prices = pd.read_pickle(BTC_PICKLE_PATH)
    self.eth_prices = pd.read_pickle(ETH_PICKLE_PATH)
    self.xrp_prices = pd.read_pickle(XRP_PICKLE_PATH)
    self.shib_prices = pd.read_pickle(SHIB_PICKLE_PATH)

  def test_ensure_correct_dtypes(self):
    for column in ['open', 'close', 'high', 'low', 'volume', 'complete']:
      self.btc_prices[column] = self.btc_prices[column].astype('object')

    fixed = ensure_correct_dtypes(self.btc_prices)

    for column in ['open', 'close', 'high', 'low', 'volume']:
      self.assertEqual('float64', fixed[column].dtype)

    self.assertEqual('boolean', fixed['complete'].dtype)

  def test_combine_prices(self):
    prices = combine_prices(self.btc_prices, self.eth_prices)

    btc_prices = self.btc_prices.set_index([self.btc_prices.index, 'ticker'])
    eth_prices = self.eth_prices.set_index([self.eth_prices.index, 'ticker'])

    self.assertTrue(btc_prices.equals(prices.loc[prices.index.get_level_values('ticker') == 'BTC']))
    self.assertTrue(eth_prices.equals(prices.loc[prices.index.get_level_values('ticker') == 'ETH']))

  def test_combine_single_ticker_prices_with_combined_prices(self):
    prices = combine_prices(combine_prices(self.btc_prices, self.eth_prices), self.xrp_prices)

    btc_prices = ensure_correct_dtypes(self.btc_prices.set_index([self.btc_prices.index, 'ticker']))
    eth_prices = ensure_correct_dtypes(self.eth_prices.set_index([self.eth_prices.index, 'ticker']))
    xrp_prices = ensure_correct_dtypes(self.xrp_prices.set_index([self.xrp_prices.index, 'ticker']))

    self.assertEqual(btc_prices, prices.loc[prices.index.get_level_values('ticker') == 'BTC'])
    self.assertEqual(eth_prices, prices.loc[prices.index.get_level_values('ticker') == 'ETH'])
    self.assertEqual(xrp_prices, prices.loc[prices.index.get_level_values('ticker') == 'XRP'])

  def test_combine_combined_prices_with_combined_prices(self):
    combined1 = combine_prices(self.btc_prices, self.eth_prices)
    combined2 = combine_prices(self.xrp_prices, self.shib_prices)

    btc_prices = ensure_correct_dtypes(self.btc_prices.set_index([self.btc_prices.index, 'ticker']))
    eth_prices = ensure_correct_dtypes(self.eth_prices.set_index([self.eth_prices.index, 'ticker']))
    xrp_prices = ensure_correct_dtypes(self.xrp_prices.set_index([self.xrp_prices.index, 'ticker']))
    shib_prices = ensure_correct_dtypes(self.shib_prices.set_index([self.shib_prices.index, 'ticker']))

    all_combined = combine_prices(combined1, combined2)

    self.assertEqual(btc_prices, all_combined.loc[all_combined.index.get_level_values('ticker') == 'BTC'])
    self.assertEqual(eth_prices, all_combined.loc[all_combined.index.get_level_values('ticker') == 'ETH'])
    self.assertEqual(xrp_prices, all_combined.loc[all_combined.index.get_level_values('ticker') == 'XRP'])
    self.assertEqual(shib_prices, all_combined.loc[all_combined.index.get_level_values('ticker') == 'SHIB'])
