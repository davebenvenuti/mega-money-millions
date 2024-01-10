import plotly.graph_objects as go

sma_colors = ('orange', 'red', 'green', 'cyan', 'violet')


def plot_candlesticks(ticker, prices):
  data = [
    go.Candlestick(
      x=prices.index.values,
      open=prices['open'],
      close=prices['close'],
      high=prices['high'],
      low=prices['low'],
      name=ticker
    ),
  ]

  for i, sma in enumerate([column for column in prices.columns if column.startswith("SMA")]):
    data.append(
      go.Scatter(
        name=sma,
        x=prices.index.values,
        y=prices[sma],
        line=dict(
          color=sma_colors[i % len(sma_colors)],
          width=1,
        )
      )
    )

  fig = go.Figure(data=data)

  fig.update_layout(title=ticker)

  fig.show()
