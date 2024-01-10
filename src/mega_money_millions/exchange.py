from abc import ABC, abstractmethod


class Exchange(ABC):
  @abstractmethod
  def fee_for_buy(self, ticker, date, price, quantity):
    pass

  @abstractmethod
  def fee_for_sell(self, ticker, date, price, quantity):
    pass


class FreeExchange(Exchange):
  def fee_for_buy(self, ticker, date, price, quantity):
    return 0.0

  def fee_for_sell(self, ticker, date, price, quantity):
    return 0.0


class Coinbase(Exchange):
  def fee_for_buy(self, ticker, date, price, quantity):
    # https://help.coinbase.com/en/exchange/trading-and-funding/exchange-fees
    # Assume taker
    return price * quantity * 0.0060

  def fee_for_sell(self, ticker, date, price, quantity):
    # https://help.coinbase.com/en/exchange/trading-and-funding/exchange-fees
    # Assume taker
    return price * quantity * 0.0060
