from collections import defaultdict
import pandas as pd
import numpy as np

from mega_money_millions.exchange import truncate_decimal, Exchange


class InsufficientFunds(Exception):
  def __init__(self, cash: float, ticker: str, price: float, quantity: float, cost: float, fee: float):
    super().__init__(
      f"Cannot purchase {quantity} shares of {ticker} @ {price}: cost {cost} (+ fee {fee}) > available cash {cash}")


class InsufficientShares(Exception):
  def __init__(self, total_quantity: float, ticker: str, price: float, quantity: float, fee: float):
    super().__init__(
      f"Cannot sell {quantity} shares of {ticker} @ {price} (- fee {fee}): only {total_quantity} shares owned")


# Unused currently
def weighed_average(df, column, weight_column):
  return (df[column] * df[weight_column]).sum() / df[weight_column].sum()


class InsufficentInventory(Exception):
  def __init__(self, ticker: str, desired_quantity: float, total: float):
    super().__init__(f"Cannot remove {desired_quantity} of {ticker}: only {total} shares owned")


class InventoryEntry:
  def __init__(self, ticker: str, quantity: float, price: float, removed: bool = False):
    self.ticker = ticker
    self.quantity = quantity
    self.price = price
    self.removed = removed

  def __eq__(self, other: any) -> bool:
    if not isinstance(other, InventoryEntry):
      return False
    if self.ticker != other.ticker:
      return False
    if self.quantity != other.quantity:
      return False

    return self.price == other.price

  def weighted_average(entries: list) -> float:
    return sum(map(lambda item: item.quantity * item.price, entries)) / sum(map(lambda item: item.quantity, entries))


class Inventory:
  def __init__(self):
    self.inventory: defaultdict[str, list[InventoryEntry]] = defaultdict(list)
    self.counts: dict[str, int] = {}

  def quantity(self, ticker: str) -> float:
    return self.counts.get(ticker, 0)

  def add(self, ticker: str, quantity: float, price: float):
    # Cronological order is important; sales should be FIFO
    self.inventory[ticker].append(InventoryEntry(ticker, quantity, price))
    self.counts[ticker] = self.counts.get(ticker, 0) + quantity

  def remove(self, ticker: str, quantity: float) -> list[InventoryEntry]:
    if quantity > self.quantity(ticker):
      raise InsufficentInventory(ticker, quantity, self.quantity(ticker))

    quantity_accounted_for = 0

    removed = []

    for entry in self.inventory[ticker]:
      remainder = quantity - quantity_accounted_for

      if entry.quantity <= remainder:
        removed.append(entry)
        entry.removed = True
      else:
        removed.append(InventoryEntry(entry.ticker, remainder, entry.price))
        entry.quantity -= remainder

      quantity_accounted_for += removed[-1].quantity

      if quantity_accounted_for == quantity:
        break

    self.counts[ticker] -= quantity

    assert quantity_accounted_for == quantity, f"{quantity_accounted_for} != {quantity}"

    self.inventory[ticker] = list(filter(lambda item: not item.removed, self.inventory[ticker]))

    return removed


class Portfolio:
  ROUND_TO: int = 4
  # purchase_price will only be present for sells
  TRANSACTIONS_COLUMNS: list[str] = [
      'time',
      'ticker',
      'price',
      'quantity',
      'cost',
      'fee',
      'cash_delta',
      'gain', # None for buys.  TODO: it's also currently None for sells but shouldn't be
      'cash']

  def __init__(self, exchange: Exchange, initial_cash: float):
    self.initial_cash: float = initial_cash
    self.exchange: str = exchange
    # cost does NOT include fee
    self.transactions: pd.DataFrame = pd.DataFrame(columns=Portfolio.TRANSACTIONS_COLUMNS)
    # Iterating over DataFrames is slow so we should use our own Inventory class
    self.inventory: Inventory = Inventory()

  def buy(self, ticker: str, date: str, price: float, quantity: float = None, percentage_of_cash: float = None):
    if quantity is None and percentage_of_cash is None or quantity is not None and percentage_of_cash is not None:
      raise ValueError("Must specify either quantity or percentage_of_cash")

    cash = self.cash()

    if percentage_of_cash is not None:
      quantity = self.exchange.max_quantity(ticker, price, truncate_decimal(cash * percentage_of_cash / 100.00, 4))

    cost = round(price * quantity, Portfolio.ROUND_TO)
    fee = self.exchange.fee_for_buy(ticker, date, price, quantity)
    cash_delta = -(cost + fee)

    if -cash_delta > cash or cash_delta >= 0:
      raise InsufficientFunds(cash, ticker, price, quantity, cost, fee)

    # This is a little confusing - cash_delta should be negative.  But it makes sense for consistency's sake.
    cash = round(cash + cash_delta, Portfolio.ROUND_TO)

    self.transactions.loc[len(self.transactions)] = [date, ticker, price, quantity, cost, fee, cash_delta, None, cash]
    self.inventory.add(ticker, quantity, price)

  def sell(self, ticker: str, date: str, price: float, quantity: float = None, percentage_of_shares: float = None):
    if quantity is None and percentage_of_shares is None or quantity is not None and percentage_of_shares is not None:
      raise ValueError("Must specify either quantity or percentage_of_shares")

    cash = self.cash()

    owned = self.quantity_owned(ticker)

    if quantity is None:
      quantity = truncate_decimal(owned * (float(percentage_of_shares) / 100), 4)

    fee = self.exchange.fee_for_sell(ticker, date, price, quantity)

    if owned < quantity:
      raise InsufficientShares(owned, ticker, price, quantity, fee)

    cost = round(price * quantity, Portfolio.ROUND_TO)
    cash_delta = cost - fee

    cash = round(cash + cash_delta, Portfolio.ROUND_TO)

    # removed = self.inventory.remove(ticker, quantity)
    # avg_purchase_price = InventoryEntry.weighted_average(removed)

    # avg_purchase_price = self.determine_avg_purchase_price(ticker, quantity)

    self.transactions.loc[len(self.transactions)] = [date, ticker, price, -quantity,
                                                     cost, fee, cash_delta, None, cash]

  def quantity_owned(self, ticker: str) -> float:
    transactions = self.transactions.loc[self.transactions['ticker'] == ticker]

    return transactions['quantity'].sum()

  def cash(self) -> float:
    if len(self.transactions) > 0:
      return self.transactions.iloc[-1]['cash']

    return self.initial_cash

  def reset(self):
    self.transactions = pd.DataFrame(columns=Portfolio.TRANSACTIONS_COLUMNS)

  def buys(self, ticker: str | None = None) -> pd.DataFrame:
    buys = self.transactions.loc[self.transactions['quantity'] > 0]

    if ticker is None:
      return buys
    else:
      return buys.loc[self.transactions['ticker'] == ticker]

  def sells(self, ticker: str | None = None) -> pd.DataFrame:
    sells = self.transactions.loc[self.transactions['quantity'] < 0]

    if ticker is None:
      return sells
    else:
      return sells.loc[self.transactions['ticker'] == ticker]

  def avg_purchase_price(self, ticker: str, include_fees=False) -> float:
    quantity = self.quantity_owned(ticker)
    # Position sells before buys, cumsum quantity, then select rows from cumsum_quantity >=0 to <= quantity.  This gives
    # us a share inventory.
    previous_sells = self.sells(ticker=ticker).copy()
    previous_buys = self.buys(ticker=ticker).copy()

    # Rewrite the indices so the sells come before the buys
    previous_sells_count = len(previous_sells)
    previous_sells.index = [i for i in range(previous_sells_count)]
    previous_buys.index = [i for i in range(previous_sells_count, previous_sells_count + len(previous_buys))]
    sells_then_buys = previous_sells.combine_first(previous_buys)
    sells_then_buys['qcs'] = sells_then_buys['quantity'].cumsum()
    inventory = sells_then_buys.loc[(sells_then_buys['qcs'] > 0) & (sells_then_buys['qcs'] <= quantity)]

    if len(inventory) == 0:
      return 0

    prices = inventory['price']
    if include_fees:
      prices += inventory['fee']
    quantities = inventory['quantity'].copy()

    # The last row may have more than we need
    if inventory.iloc[-1]['qcs'] > quantity:
      quantities.iloc[-1] = inventory.iloc[-1]['qcs'] - quantity

    return (prices * quantities).sum() / quantities.sum()

  # https://trendspider.com/learning-center/basic-backtesting-metrics/
  """
    Net Performance: Net Performance represents the overall performance of the strategy during the backtest period.
      It is measured as a percentage and indicates the net gain or loss generated by the strategy.
    Positions: Positions represents the total number of positions generated by the strategy during the backtest.
      Each position represents a trade or a set of trades with a specific entry and exit point.
    Wins: Wins represents the percentage of trades that resulted in a profit. A higher percentage indicates a higher win
      rate for the strategy.
    Win Streak, avg: Win Streak, avg. calculates the average number of consecutive winning trades. This metric helps
      assess the strategy’s ability to generate profitable trades consistently.
    Win Streak, max: Win Streak, max. represents the maximum number of consecutive winning trades. This metric provides
      insights into the strategy’s best winning streak.
    Losses: Losses represents the percentage of trades that resulted in a loss. A lower percentage indicates a higher
      percentage of profitable trades.
    Loss Streak, avg: Loss Streak, avg. calculates the average number of consecutive losing trades. It helps assess the
      strategy’s ability to withstand losing streaks.
    Loss Streak, max: Loss Streak, max. represents the maximum number of consecutive losing trades experienced by the
      strategy. This metric provides insights into the strategy’s worst losing streak.
    Max DD (Max Drawdown): Max Drawdown measures the largest percentage decline in the strategy’s overall equity from a
      peak to a subsequent trough. It indicates the maximum loss suffered by the strategy at any point during the
      backtest.
    Average Win: Average Win calculates the average return for winning trades. This metric provides insights into the
      average profitability of successful trades.
    Average Loss: Average Loss calculates the average return for losing trades. This metric helps assess the average
      magnitude of losses incurred by the strategy.
    Average Return: Average Return calculates the average return for all trades, whether they are winners or losers.
      This metric gives an overall picture of the average profitability of the strategy’s trades.
    Rew/Risk Ratio (Reward-to-Risk Ratio): The Reward-to-Risk Ratio is calculated by dividing the average win by the
      average loss. This ratio provides insights into the potential reward relative to the risk taken by the strategy.
    Avg. Length (Average Length): Average Length represents the average duration of a position, measured in candlestick
      periods. This metric helps assess the average holding period of trades generated by the strategy.
    Trades/Day: Trades/Day calculates the average number of trades executed per day during the backtest.
      This metric provides insights into the frequency of trading activity.
    Trades/Month: Trades/Month calculates the average number of trades executed per month during the backtest.
      This metric provides insights into the monthly trading activity of the strategy.
  """

  # Returns a percentage
  def net_performance(self) -> float:
    return round(((self.cash() - self.initial_cash) / self.initial_cash * 100), Portfolio.ROUND_TO)

  def wins(self) -> pd.DataFrame:
    sells = self.sells()

    return sells.loc[sells['cash_delta'] > 0]

  def losses(self) -> pd.DataFrame:
    sells = self.sells()

    return sells.loc[sells['cash_delta'] < 0]

  def avg_win_streak(self) -> float:
    pass

    self.wins().index
    import pdb
    pdb.set_trace()
    return 0

  def max_win_streak(self) -> int:
    pass

  def avg_loss_streak(self):
    pass

  def max_loss_streak(self):
    pass

  def max_drawdown(self):
    pass

  def avg_win(self):
    pass

  def avg_loss(self):
    pass

  def avg_return(self):
    pass

  def reward_to_risk_ratio(self):
    pass

  def avg_length(self):
    pass

  def trades_per_day(self):
    pass

  def trades_per_month(self):
    pass
