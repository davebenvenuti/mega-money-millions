import os
import sys
from os.path import join

PROJECT_PATH = os.getcwd()
SOURCE_PATH = os.path.join(
    PROJECT_PATH, "src"
)
sys.path.append(SOURCE_PATH)

BTC_PICKLE_PATH = join(PROJECT_PATH, 'tests/BTC.pickle')
ETH_PICKLE_PATH = join(PROJECT_PATH, 'tests/ETH.pickle')
