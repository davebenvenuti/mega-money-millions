import unittest
from mega_money_millions.portfolio import Portfolio, InsufficientFunds, InsufficientShares
from mega_money_millions.exchange import FreeExchange, Coinbase


class TestPortfolio(unittest.TestCase):
  def setUp(self):
    self.portfolio = Portfolio(FreeExchange(), 10000)
    self.coinbase_portfolio = Portfolio(Coinbase(), 10000)

  def test_buy(self):
    self.portfolio.buy('BTC', '2023-12-23', 40000, 0.125)

    self.assertEqual(('2023-12-23', 'BTC', 40000, 0.125, 5000, 0, 5000), tuple(self.portfolio.positions.loc[0]))
    self.assertEqual(self.portfolio.cash(), 5000)

    with self.assertRaises(InsufficientFunds):
      self.portfolio.buy('BTC', '2023-12-24', 40000, 1)

    self.portfolio.buy('ETH', '2023-12-24', 5000, 0.75)

    self.assertEqual(('2023-12-24', 'ETH', 5000, 0.75, 3750, 0, 1250), tuple(self.portfolio.positions.loc[1]))
    self.assertEqual(self.portfolio.cash(), 1250)

  def test_coinbase_buy(self):
    self.coinbase_portfolio.buy('BTC', '2023-12-23', 40000, 0.125)

    self.assertEqual(('2023-12-23', 'BTC', 40000, 0.125, 5000, 30, 4970),
                     tuple(self.coinbase_portfolio.positions.loc[0]))
    self.assertEqual(self.coinbase_portfolio.cash(), 4970)

    with self.assertRaises(InsufficientFunds):
      self.coinbase_portfolio.buy('BTC', '2023-12-24', 40000, 1)

    self.coinbase_portfolio.buy('ETH', '2023-12-24', 5000, 0.75)

    self.assertEqual(('2023-12-24', 'ETH', 5000, 0.75, 3750, 22.5, 1197.5),
                     tuple(self.coinbase_portfolio.positions.loc[1]))
    self.assertEqual(self.coinbase_portfolio.cash(), 1197.5)

  def test_quantity_owned(self):
    self.portfolio.buy('BTC', '2023-12-23', 40000, 0.125)
    self.portfolio.buy('BTC', '2023-12-23', 40000, 0.125)

    self.assertEqual(0.25, self.portfolio.quantity_owned('BTC'))

  def test_sell(self):
    with self.assertRaises(InsufficientShares):
      self.portfolio.sell('BTC', '2023-12-23', 40000, 1)

    self.portfolio.buy('BTC', '2023-12-23', 40000, 0.25)

    with self.assertRaises(InsufficientShares):
      self.portfolio.sell('BTC', '2023-12-23', 40000, 1)

    self.portfolio.sell('BTC', '2023-12-24', 45000, 0.125)

    self.assertEqual(self.portfolio.cash(), 5625)

  def test_coinbase_sell(self):
    with self.assertRaises(InsufficientShares):
      self.coinbase_portfolio.sell('BTC', '2023-12-23', 40000, 1)

    self.coinbase_portfolio.buy('BTC', '2023-12-23', 40000, 0.20)

    with self.assertRaises(InsufficientShares):
      self.coinbase_portfolio.sell('BTC', '2023-12-23', 40000, 1)

    self.coinbase_portfolio.sell('BTC', '2023-12-24', 45000, 0.125)

    self.assertEqual(self.coinbase_portfolio.cash(), 7543.25)
