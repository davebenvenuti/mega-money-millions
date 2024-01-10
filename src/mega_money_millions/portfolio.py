import pandas as pd


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

  def buy(self, ticker, date, price, quantity):
    cost = price * quantity
    fee = self.exchange.fee_for_buy(ticker, date, price, quantity)
    total_cost = cost + fee
    cash = self.cash()

    if total_cost > cash:
      raise InsufficientFunds(cash, ticker, price, quantity, cost, fee)

    cash -= total_cost

    self.positions.loc[len(self.positions)] = [date, ticker, price, quantity, cost, fee, cash]

  def sell(self, ticker, date, price, quantity):
    owned = self.quantity_owned(ticker)
    fee = self.exchange.fee_for_sell(ticker, date, price, quantity)

    if owned < quantity:
      raise InsufficientShares(owned, ticker, price, quantity, fee)

    cash = self.cash()

    cost = price * quantity
    total_cost = cost - fee

    cash += total_cost

    self.positions.loc[len(self.positions)] = [date, ticker, price, -quantity, cost, fee, cash]

  def quantity_owned(self, ticker):
    return self.positions.loc[self.positions.ticker == ticker, 'quantity'].sum()

  def cash(self):
    if len(self.positions) > 0:
      return self.positions.iloc[-1]['cash']

    return self.initial_cash
