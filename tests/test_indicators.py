import unittest
import pandas as pd
from mega_money_millions.indicators import add_sma, add_filter, add_ranking, add_roc
from tests import BTC_PICKLE_PATH


class TestIndicators(unittest.TestCase):
  def setUp(self):
    self.btc_prices = pd.read_pickle(BTC_PICKLE_PATH)
    pass

  def test_add_sma(self):
    add_sma(self.btc_prices, 45)

    for date, expected in (
      ('2024-01-02', 41272.24),
      ('2024-01-03', 41393.83),
      ('2024-01-04', 41543.11),
      ('2024-01-05', 41730.54),
      ('2024-01-06', 41876.50)):
      self.assertEqual(expected, self.btc_prices.loc[date]['SMA45'])

  def test_add_roc(self):
    add_roc(self.btc_prices, 20)

    for date, expected in (
      ('2024-01-02', 4.867048427045577),
      ('2024-01-03', -0.38424022439460487),
      ('2024-01-04', 5.3880047856280475),
      ('2024-01-05', 4.615116168674637),
      ('2024-01-06', 6.391478125901625)):
      self.assertEqual(expected, self.btc_prices.loc[date]['ROC20'])

  def test_add_filter(self):
    pass

  def test_add_ranking(self):
    pass
