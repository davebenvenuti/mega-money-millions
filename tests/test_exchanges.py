import unittest
from mega_money_millions.exchange import Coinbase


class TestCoinbase(unittest.TestCase):
  def setUp(self):
    self.exchange = Coinbase()

  def test_max_quantity(self):
    self.assertEqual(0.9940, self.exchange.max_quantity('BTC', price=10000, cash=10000))
    self.assertEqual(0.0058, self.exchange.max_quantity('BTC', price=42341.01, cash=250))

  def test_fee_for_buy(self):
    pass

  def test_fee_for_sell(self):
    pass
