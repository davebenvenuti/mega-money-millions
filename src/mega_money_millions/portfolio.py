import pandas as pd

from mega_money_millions.exchange import truncate_decimal


class InsufficientFunds(Exception):
  def __init__(self, cash, ticker, price, quantity, cost, fee):
    super().__init__(
      f"Cannot purchase {quantity} shares of {ticker} @ {price}: cost {cost} (+ fee {fee}) > available cash {cash}")


class InsufficientShares(Exception):
  def __init__(self, total_quantity, ticker, price, quantity, fee):
    super().__init__(
      f"Cannot sell {quantity} shares of {ticker} @ {price} (- fee {fee}): only {total_quantity} shares owned")


class Portfolio:
  def __init__(self, exchange, initial_cash):
    self.initial_cash = initial_cash
    self.exchange = exchange
    # cost does NOT include fee
    self.positions = pd.DataFrame(columns=['time', 'ticker', 'price', 'quantity', 'cost', 'fee', 'cash'])

  def buy(self, ticker, date, price, quantity=None, percentage_of_cash=None):
    if quantity is None and percentage_of_cash is None or quantity is not None and percentage_of_cash is not None:
      raise ValueError("Must specify either quantity or percentage_of_cash")

    cash = self.cash()

    if percentage_of_cash is not None:
      quantity = self.exchange.max_quantity(ticker, price, truncate_decimal(cash * percentage_of_cash / 100.00, 4))

    cost = round(price * quantity, 4)
    fee = self.exchange.fee_for_buy(ticker, date, price, quantity)
    total_cost = cost + fee

    if total_cost > cash or total_cost <= 0:
      raise InsufficientFunds(cash, ticker, price, quantity, cost, fee)

    cash -= total_cost

    self.positions.loc[len(self.positions)] = [date, ticker, price, quantity, cost, fee, cash]

  def sell(self, ticker, date, price, quantity=None, percentage_of_shares=None):
    if quantity is None and percentage_of_shares is None or quantity is not None and percentage_of_shares is not None:
      raise ValueError("Must specify either quantity or percentage_of_shares")

    cash = self.cash()

    owned = self.quantity_owned(ticker)

    if quantity is None:
      quantity = truncate_decimal(owned * (float(percentage_of_shares) / 100), 4)

    fee = self.exchange.fee_for_sell(ticker, date, price, quantity)

    if owned < quantity:
      raise InsufficientShares(owned, ticker, price, quantity, fee)

    cost = round(price * quantity, 4)
    total_cost = cost - fee

    cash += total_cost

    self.positions.loc[len(self.positions)] = [date, ticker, price, -quantity, cost, fee, cash]

  def quantity_owned(self, ticker):
    return self.positions.loc[self.positions.ticker == ticker, 'quantity'].sum()

  def cash(self):
    if len(self.positions) > 0:
      return self.positions.iloc[-1]['cash']

    return self.initial_cash
