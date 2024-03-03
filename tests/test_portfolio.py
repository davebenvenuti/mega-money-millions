import unittest
import numpy as np
from mega_money_millions.portfolio import Portfolio, InsufficientFunds, InsufficientShares
from mega_money_millions.exchange import FreeExchange, Coinbase


class TestPortfolio(unittest.TestCase):
  def setUp(self):
    self.portfolio = Portfolio(FreeExchange(), 10000)
    self.coinbase_portfolio = Portfolio(Coinbase(), 10000)

  def test_buy(self):
    self.portfolio.buy('BTC', '2023-12-23', 40000, 0.125)

    self.assertEqual(('2023-12-23', 'BTC', 40000, 0.125, 5000, 0, -5000, 0, 5000),
                     tuple(self.portfolio.transactions.loc[0]))
    self.assertEqual(self.portfolio.cash(), 5000)

    with self.assertRaises(InsufficientFunds):
      self.portfolio.buy('BTC', '2023-12-24', 40000, 1)

    self.portfolio.buy('ETH', '2023-12-24', 5000, 0.75)

    self.assertEqual(('2023-12-24', 'ETH', 5000, 0.75, 3750, 0, -3750, 0, 1250), tuple(self.portfolio.transactions.loc[1]))
    self.assertEqual(self.portfolio.cash(), 1250)

  def test_buy_with_percentage_of_cash(self):
    with self.assertRaises(ValueError):
      self.portfolio.buy('BTC', '2023-12-23', 40000, percentage_of_cash=50, quantity=0.125)

    self.portfolio.buy('BTC', '2023-12-23', 40000, percentage_of_cash=50)
    self.assertEqual(('2023-12-23', 'BTC', 40000, 0.125, 5000, 0, -5000, 0, 5000),
                     tuple(self.portfolio.transactions.iloc[-1]))

    self.portfolio.buy('BTC', '2023-12-24', 40000, percentage_of_cash=50)
    self.assertEqual(('2023-12-24', 'BTC', 40000, 0.0625, 2500, 0, -2500, 0, 2500),
                     tuple(self.portfolio.transactions.iloc[-1]))

    self.portfolio.buy('BTC', '2023-12-25', 40000, percentage_of_cash=100)
    self.assertEqual(('2023-12-25', 'BTC', 40000, 0.0625, 2500, 0, -2500, 0, 0),
                     tuple(self.portfolio.transactions.iloc[-1]))

    with self.assertRaises(InsufficientFunds):
      self.portfolio.buy('BTC', '2023-12-26', 40000, percentage_of_cash=100)

  def test_buy_with_percentage_of_cash_bug_that_came_up_in_bugtester_where_buying_and_selling_100_percent_raises(self):
    """
    Original Exception
      InsufficientFunds: Cannot purchase 1.2349 shares of BTC @ 10933.09:
        cost 13501.272841000002 (+ fee 81.00763704600001) > available cash 13581.828871282001
    """

    self.portfolio.initial_cash = 13581.828871282001
    self.portfolio.buy('BTC', '2020-09-01', 10933.09, percentage_of_cash=100)

  def test_coinbase_buy(self):
    self.coinbase_portfolio.buy('BTC', '2023-12-23', 40000, 0.125)

    self.assertEqual(('2023-12-23', 'BTC', 40000, 0.125, 5000, 30, -5030, 0, 4970),
                     tuple(self.coinbase_portfolio.transactions.loc[0]))
    self.assertEqual(self.coinbase_portfolio.cash(), 4970)

    with self.assertRaises(InsufficientFunds):
      self.coinbase_portfolio.buy('BTC', '2023-12-24', 40000, 1)

    self.coinbase_portfolio.buy('ETH', '2023-12-24', 5000, 0.75)

    self.assertEqual(('2023-12-24', 'ETH', 5000, 0.75, 3750, 22.5, -3772.5, 0, 1197.5),
                     tuple(self.coinbase_portfolio.transactions.loc[1]))
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

  def test_sell_with_percentage_of_shares(self):
    self.portfolio.buy('BTC', '2023-12-23', 40000, percentage_of_cash=50)

    with self.assertRaises(ValueError):
      self.portfolio.sell('BTC', '2023-12-23', 40000, percentage_of_shares=50, quantity=0.125)

    self.portfolio.sell('BTC', '2023-12-24', 40000, percentage_of_shares=50)
    self.assertEqual(('2023-12-24', 'BTC', 40000, -0.0625, 2500, 0, 2500, 0, 7500),
                     tuple(self.portfolio.transactions.iloc[-1]))
    self.assertEqual(self.portfolio.cash(), 7500)

    self.portfolio.sell('BTC', '2023-12-25', 40000, percentage_of_shares=100)
    self.assertEqual(('2023-12-25', 'BTC', 40000, -0.0625, 2500, 0, 2500, 0, 10000),
                     tuple(self.portfolio.transactions.iloc[-1]))
    self.assertEqual(self.portfolio.cash(), 10000)

  def test_coinbase_sell(self):
    with self.assertRaises(InsufficientShares):
      self.coinbase_portfolio.sell('BTC', '2023-12-23', 40000, 1)

    self.coinbase_portfolio.buy('BTC', '2023-12-23', 40000, 0.20)

    with self.assertRaises(InsufficientShares):
      self.coinbase_portfolio.sell('BTC', '2023-12-23', 40000, 1)

    self.coinbase_portfolio.sell('BTC', '2023-12-24', 45000, 0.125)

    self.assertEqual(self.coinbase_portfolio.cash(), 7543.25)

  def test_buys_and_sells(self):
    self.coinbase_portfolio.buy('BTC', '2023-12-23', 35000, 0.1125)
    self.coinbase_portfolio.buy('BTC', '2023-12-24', 40000, 0.1125)
    self.coinbase_portfolio.sell('BTC', '2023-12-25', 41000, 0.1125)
    self.coinbase_portfolio.buy('BTC', '2023-12-26', 40500, 0.1125)
    self.coinbase_portfolio.sell('BTC', '2023-12-27', 42000, 0.1125)
    self.coinbase_portfolio.sell('BTC', '2023-12-28', 43000, 0.1125)

    buys = self.coinbase_portfolio.buys()

    self.assertEqual([
      (0, ['2023-12-23', 'BTC', 35000, 0.1125, 3937.5, 23.625, -3961.125, 0, 6038.875]),
      (1, ['2023-12-24', 'BTC', 40000, 0.1125, 4500.0, 27.0, -4527.0, 0, 1511.875]),
      (3, ['2023-12-26', 'BTC', 40500, 0.1125, 4556.25, 27.3375, -4583.5875, 0, 1513.1125]),
    ], list(zip(buys.index, buys.values.tolist())))

    sells = self.coinbase_portfolio.sells()

    self.assertEqual([
      (2, ['2023-12-25', 'BTC', 41000, -0.1125, 4612.5, 27.675, 4584.825, 363.2273, 6096.7]),
      (4, ['2023-12-27', 'BTC', 42000, -0.1125, 4725.0, 28.35, 4696.65, 165.4685, 6209.7625]),
      (5, ['2023-12-28', 'BTC', 43000, -0.1125, 4837.5, 29.025, 4808.475, 249.1495, 11018.2375]),
    ], list(zip(sells.index, sells.values.tolist())))

    self.coinbase_portfolio.buy('ETH', '2023-12-28', 5000, 1)
    self.coinbase_portfolio.sell('ETH', '2023-12-29', 6000, 1)

    buys = self.coinbase_portfolio.buys()

    self.assertEqual([
      (0, ['2023-12-23', 'BTC', 35000, 0.1125, 3937.5, 23.625, -3961.125, 0, 6038.875]),
      (1, ['2023-12-24', 'BTC', 40000, 0.1125, 4500.0, 27.0, -4527.0, 0, 1511.875]),
      (3, ['2023-12-26', 'BTC', 40500, 0.1125, 4556.25, 27.3375, -4583.5875, 0, 1513.1125]),
      (6, ['2023-12-28', 'ETH', 5000, 1.0, 5000.0, 30.0, -5030.0, 0, 5988.2375]),
    ], list(zip(buys.index, buys.values.tolist())))

    eth_buys = self.coinbase_portfolio.buys('ETH')

    self.assertEqual([
      (6, ['2023-12-28', 'ETH', 5000, 1.0, 5000.0, 30.0, -5030.0, 0, 5988.2375])
    ], list(zip(eth_buys.index, eth_buys.values.tolist())))

    sells = self.coinbase_portfolio.sells()

    self.assertEqual([
      (2, ['2023-12-25', 'BTC', 41000, -0.1125, 4612.5, 27.675, 4584.825, 363.2273, 6096.7]),
      (4, ['2023-12-27', 'BTC', 42000, -0.1125, 4725.0, 28.35, 4696.65, 165.4685, 6209.7625]),
      (5, ['2023-12-28', 'BTC', 43000, -0.1125, 4837.5, 29.025, 4808.475, 249.1495, 11018.2375]),
      (7, ['2023-12-29', 'ETH', 6000, -1.0, 6000.0, 36.0, 5964.0, 934.0, 11952.2375])
    ], list(zip(sells.index, sells.values.tolist())))

    sells_eth = self.coinbase_portfolio.sells('ETH')

    self.assertEqual([
      (7, ['2023-12-29', 'ETH', 6000, -1.0, 6000.0, 36.0, 5964.0, 934.0, 11952.2375]),
    ], list(zip(sells_eth.index, sells_eth.values.tolist())))

  def test_net_performance(self):
    self.coinbase_portfolio.buy('BTC', '2023-12-23', 40000, 0.125)
    self.coinbase_portfolio.sell('BTC', '2023-12-24', 45000, 0.125)

    self.assertEqual(5.6125, self.coinbase_portfolio.net_performance())

    self.coinbase_portfolio.buy('BTC', '2023-12-25', 40000, 0.125)
    self.coinbase_portfolio.sell('BTC', '2023-12-26', 35000, 0.125)

    self.assertEqual(-1.2, self.coinbase_portfolio.net_performance())

  def test_reset(self):
    self.coinbase_portfolio.buy('BTC', '2023-12-23', 40000, 0.125)
    self.coinbase_portfolio.sell('BTC', '2023-12-24', 45000, 0.125)

    self.coinbase_portfolio.reset()

    self.assertEqual(10000, self.coinbase_portfolio.cash())
    self.assertEqual(0, len(self.coinbase_portfolio.transactions))

  def test_avg_purchase_price(self):
    self.coinbase_portfolio.buy('BTC', '2023-12-23', 30000, 0.125)
    self.coinbase_portfolio.buy('BTC', '2023-12-24', 35000, 0.125)

    self.assertEqual(32500, self.coinbase_portfolio.avg_purchase_price('BTC'))
    self.assertEqual(32524.375, self.coinbase_portfolio.avg_purchase_price('BTC', include_fees=True))

    self.coinbase_portfolio.sell('BTC', '2023-12-25', 40000, 0.25)

    self.assertEqual(0, self.coinbase_portfolio.avg_purchase_price('BTC'))
    self.assertEqual(0, self.coinbase_portfolio.avg_purchase_price('BTC', include_fees=True))

    self.coinbase_portfolio.buy('BTC', '2023-12-26', 40000, 0.25)

    self.assertEqual(40000, self.coinbase_portfolio.avg_purchase_price('BTC'))
    self.assertEqual(40060.0, self.coinbase_portfolio.avg_purchase_price('BTC', include_fees=True))

    self.coinbase_portfolio.sell('BTC', '2023-12-27', 45000, 0.125)

    self.assertEqual(40000, self.coinbase_portfolio.avg_purchase_price('BTC'))
    self.assertEqual(40060.0, self.coinbase_portfolio.avg_purchase_price('BTC', include_fees=True))

  def test_wins_and_losses(self):
    self.skipTest("Need to figure out entry price first")
    self.coinbase_portfolio.initial_cash = 50000

    self.coinbase_portfolio.buy('BTC', '2023-12-23', 40000, 0.125)
    self.coinbase_portfolio.sell('BTC', '2023-12-24', 45000, 0.125)
    self.coinbase_portfolio.buy('BTC', '2023-12-25', 40000, 0.125)
    self.coinbase_portfolio.sell('BTC', '2023-12-26', 35000, 0.125)
    self.coinbase_portfolio.buy('BTC', '2023-12-27', 40000, 0.125)
    self.coinbase_portfolio.sell('BTC', '2023-12-28', 46000, 0.125)

    wins = self.coinbase_portfolio.wins()

    self.assertEqual([
      (1, ['2023-12-24', 'BTC', 45000, -0.125, 5625.0, 33.75, 5591.25, 50561.25]),
      (3, ['2023-12-26', 'BTC', 35000, -0.125, 4375.0, 26.25, 4348.75, 49880.0]),
      (5, ['2023-12-28', 'BTC', 46000, -0.125, 5750.0, 34.5, 5715.5, 50565.5])],
      list(zip(wins.index, wins.values.tolist())))

    losses = self.coinbase_portfolio.losses()

    self.assertEqual([
      (4, ['2023-12-27', 'BTC', 40000, 0.125, 5000.0, 30.0, -5030.0, 4850.0])],
      list(zip(losses.index, losses.values.tolist())))
