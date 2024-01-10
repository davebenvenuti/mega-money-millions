from .portfolio import Portfolio
from .exchange import Coinbase
from .dateutils import now


# on_tick is called 1x/day.  TODO (davebenvenuti 2023-01-10): support configurable tick frequency
def run_backtest(prices, initial_cash, start_at, end_at=now(), *, on_tick):
  portfolio = Portfolio(Coinbase(), initial_cash)

  for date in range(start_at, end_at):
    prices_for_date = prices.loc[date]

    on_tick(date, portfolio, prices_for_date)

  return portfolio
