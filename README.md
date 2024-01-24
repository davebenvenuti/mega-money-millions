# Mega Money Millions

An opinionated trading strategy backtesting framework for python.

## Usage

Generally speaking, `mega_money_millions` expects Pandas Dataframes of Price information indexed by either `time` or
multi-indexed on `time` AND `ticker`.

There is also a fair amount of unit test coverage so working examples can be found in `tests/**/test_*.py`.

### `indicators`
`mega_money_millions.indicators.singleasset` includes functions that add the given indicator to a Dataframe indexed by
`time`.

#### `add_sma(prices, window, prefix='SMA')`

Add a Simple Moving Average to the given `prices` DataFrame for a _single_
asset.  `prices` will be mutated and the moving average will be found in a new column named `f'{prefix}{window}`.  Eg:
`add_sma(prices, 45)` will add a new column `SMA45` to `prices`.

#### `add_roc(prices, window, prefix='ROC)`

Add a Rate of Change to the given `prices` DataFrame for a _single_ asset.  `prices` will be mutated and the rate of
change will be found in a new column named `f'{prefix}{window}`.  Eg:  `add_roc(prices, 20)` will add a new column
`ROC20` to `prices`.

#### `add_crossover(prices, on_stat1, on_stat2, to_stat1, to_stat2)`

Add two boolean fields to `prices` based on when `on_stat1` crosses over `on_stat2` and vice versa.  For example:

```python
# Adds two columns to `prices`: 'SMACrossUp' and 'SMACrossDown'.  On the bar where the SMA45 crosses over
# (becomes greater than) the SMA90, 'SMACrossUp' will be true.  On the bar when the SMA90 crosses over the SMA45,
# 'SMACrossDown' will be true.  Note that the value will only be true _on the bar_ when the crossover occurs; it
# will become false again on the next bar.  This is meant to track when the change occurs, not every tick when one
# bar is greater than the other.
add_crossover(prices, 'SMA45', 'SMA90', 'SMACrossUp', 'SMACrossDown')
```

### `priceutils`

#### `combine_prices(prices1, prices2)`

Takes two _single asset_ price DataFrames and combines them into a new DataFrame with a multi-index on `time` and `ticker`.
Expects `prices1` and `prices2` to each have a `time` and `ticker` column.

### `exchange`

Includes `Exchange` subclasses that represent places where securities are traded.  These are responsible for things like
estimating trading fees.  The only current option is `CoinBase()`.

### `portfolio`

Defines an object that helps simulate trades.

#### `class Portfolio`

A new `Portfolio` can be initialized with `Portfolio(exchange, initial_cash)`.  `exchange` is an `Exchange` instance as
defined above.  `initial_cash` is an integer or float.  It exposes the following methods:

##### `Portfolio#buy(ticker, date, price, quantity=None, percentage_of_cash=None)`

Buy either `quantity` shares at the given `price` or calculate the number of shares to purchase based on
`percentage_of_cash`.  Exchange/trading fees will be taken into account based on the `Exchange` object
(eg: `Coinbase()`).  `percentage_of_cash` should be between `1` and `100` (not `0` and `1`).

##### `Portfolio#sell(ticker, date, price, quantity=None, percentage_of_shares=None)`

Sell either `quantity` shares or calculte the number of shares to sell based on `percentage_of_shares`.  Exchange/trading
fees will be taken into account based on the `Exchange` object.  `percentage_of_shares` should be between `1` and `100`
(not `0` and `1`).

##### `Portfolio#cash()`

Returns the current cash balance of the portfolio based on `initial_cash` and trade history.

##### `Portfolio#quantity_owned(ticker)`

Returns the number of shares currently owned of the given `ticker`.

##### `Portfolio.positions`

A property that returns a DataFrame that represents a chronological log of buys and sells.

### `backtester`

Exposes a function intended for use in backtesting trading strategies.

#### `run_backtest(prices, initial_cash, start_at, end_at=now(), *, on_tick)`

Accepts a multi-asset `prices` (multi-indexed on `time` and `ticker`), an initial cash amount, and an `on_tick` callback.
The `on_tick` method should accept the current `time`, the `Portfolio` object, and the `prices_for_date` for ALL assets
on the given date.  Note that the tick frequency is currently hardcoded to be days.

https://github.com/davebenvenuti/mega-money-millions/blob/main/tests/test_backtester.py gives a good example of how one
might backtest a strategy to move 100% of a portfolio's cash into `BTC` when the `SMA45` crosses the `SMA90`, and sell
the entire position then the `SMA90` once again tops the `SMA45`.


## Development

### Install a dependency

```bash
pipenv install [package]
```

Might also have to add it to pyproject.toml manually.  lol.

### Install a dev dependency

### Setup

```bash
bin/shell
```

Which actually does this:

```bash
pipenv shell # vscode might do this automatically? maybe?
```

### Lint

```bash
bin/lint
bin/lint-autocorrect
```

Linter and formatter are separate and both configured in `pyproject.toml`.

## Misc links

- https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
- https://packaging.python.org/en/latest/tutorials/packaging-projects/
- https://dev.to/vorsprung/vscode-pipenv-python-34pf used to get pipenv and vscode working together
- https://pipenv.pypa.io/en/latest/
