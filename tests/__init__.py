import os
import sys
from os.path import join
import pandas as pd

PROJECT_PATH = os.getcwd()
SOURCE_PATH = os.path.join(
    PROJECT_PATH, "src"
)
sys.path.append(SOURCE_PATH)

BTC_PICKLE_PATH = join(PROJECT_PATH, 'tests/BTC.pickle')
ETH_PICKLE_PATH = join(PROJECT_PATH, 'tests/ETH.pickle')
XRP_PICKLE_PATH = join(PROJECT_PATH, 'tests/XRP.pickle')
SHIB_PICKLE_PATH = join(PROJECT_PATH, 'tests/SHIB.pickle')


def load_btc_pickle():
  return pd.read_pickle(BTC_PICKLE_PATH)


def load_eth_pickle():
  return pd.read_pickle(ETH_PICKLE_PATH)


BTC_SMA45_CROSSUPS = list(
    map(
        lambda ts: pd.Timestamp(ts),
        ('2018-09-11',
         '2019-09-06',
         '2020-03-23',
         '2020-10-08',
         '2021-05-21',
         '2021-12-21',
         '2022-05-10',
         '2022-09-18',
         '2023-06-07',
         '2023-08-28')))

BTC_SMA45_CROSSDOWNS = list(map(
  lambda ts: pd.Timestamp(ts),
    ('2019-03-15',
     '2020-01-30',
     '2020-05-14',
     '2020-10-28',
     '2021-08-13',
     '2022-03-31',
     '2022-09-01',
     '2023-01-22',
     '2023-07-09',
     '2023-10-25')))
