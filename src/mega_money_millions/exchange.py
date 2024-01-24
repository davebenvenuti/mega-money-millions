from abc import ABC, abstractmethod


class Exchange(ABC):
  @abstractmethod
  def max_quantity(self, ticker, price, cash):
    pass

  @abstractmethod
  def fee_for_buy(self, ticker, date, price, quantity):
    pass

  @abstractmethod
  def fee_for_sell(self, ticker, date, price, quantity):
    pass


# TODO: (davebenvenuti 2023-01-17) this doesn't belong here
def truncate_decimal(number, decimal_places=4):
  multiplier = 10 ** decimal_places
  return int(number * multiplier) / multiplier


class FreeExchange(Exchange):
  def max_quantity(self, ticker, price, cash):
    return cash / price

  def fee_for_buy(self, ticker, date, price, quantity):
    return 0.0

  def fee_for_sell(self, ticker, date, price, quantity):
    return 0.0


class Coinbase(Exchange):
  FEE = 0.0060

  def max_quantity(self, ticker, price, cash):
    # https://help.coinbase.com/en/exchange/trading-and-funding/trading-rules-and-fees/fees
    # Assume taker
    price_with_fee = price * (1 + self.FEE)
    return truncate_decimal(cash / price_with_fee, 4)

  def fee_for_buy(self, ticker, date, price, quantity):
    # https://help.coinbase.com/en/exchange/trading-and-funding/exchange-fees
    # Assume taker
    return round(price * quantity * self.FEE, 4)

  def fee_for_sell(self, ticker, date, price, quantity):
    # https://help.coinbase.com/en/exchange/trading-and-funding/exchange-fees
    # Assume taker
    return truncate_decimal(price * quantity * self.FEE, 4)
