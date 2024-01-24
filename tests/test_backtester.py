import unittest
from mega_money_millions.backtester import run_backtest
from mega_money_millions.dateutils import days_ago, start_of_day_utc, parse_date
from mega_money_millions.indicators.singleasset import add_crossover, add_sma
from mega_money_millions.priceutils import combine_prices
from tests import load_btc_pickle, load_eth_pickle, BTC_SMA45_CROSSUPS, BTC_SMA45_CROSSDOWNS


class TestBacktester(unittest.TestCase):
  def setUp(self):
    self.btc_prices = load_btc_pickle()
    self.eth_prices = load_eth_pickle()

    def add_indicators(prices):
      add_sma(prices, 45)
      add_sma(prices, 90)
      add_crossover(prices, 'SMA45', 'SMA90', 'SMACrossUp', 'SMACrossDown')

    add_indicators(self.btc_prices)
    add_indicators(self.eth_prices)

    self.prices = combine_prices(self.btc_prices, self.eth_prices)

  def test_run_backtest(self):
    end_at = start_of_day_utc(parse_date('2024-01-06'))

    def __on_tick(date, portfolio, prices_for_date):
      btc = prices_for_date.loc['BTC']

      if btc['SMACrossUp'] and portfolio.cash() > 0:
        portfolio.buy('BTC', date, btc['close'], percentage_of_cash=100)
      elif btc['SMACrossDown'] and portfolio.quantity_owned('BTC') > 0:
        portfolio.sell('BTC', date, btc['close'], percentage_of_shares=100)

    portfolio = run_backtest(self.prices, 10000, days_ago(365 * 5, end_at), end_at, on_tick=__on_tick)

    self.assertEqual(20803.781399999993, portfolio.cash())

    buy_dates = portfolio.positions.query('ticker == "BTC" & quantity > 0')['time'].tolist()
    sell_dates = portfolio.positions.query('ticker == "BTC" & quantity < 0')['time'].tolist()

    crossups = list(filter(lambda date: date.year >= 2019, BTC_SMA45_CROSSUPS))
    crossdowns = list(filter(lambda date: date.year >= 2019 and date > crossups[0], BTC_SMA45_CROSSDOWNS))

    self.assertEqual(crossups, buy_dates)
    self.assertEqual(crossdowns, sell_dates)
