import math
import os
import random
import re
import sys
import pandas as pd
from collections import deque
import datetime

def average(lst):
    return sum(lst) / len(lst)

class TradingStrategy:
    def __init__(self):
        self.small_window = deque()
        self.large_window = deque()
        self.long_signal = False
        self.position = 0
        self.cash = 10000
        self.total = 0
        self.holdings = 0

    def onPriceUpdate(self, price_update):
        self.small_window.appendleft(float(price_update['close']))
        self.large_window.appendleft(float(price_update['close']))
        if len(self.small_window) > 50:
            self.small_window.pop()
        if len(self.large_window) > 100:
            self.large_window.pop()
        if average(self.small_window) > average(self.large_window):
            self.long_signal = True
        else:
            self.long_signal = False
        self.checkSignal(price_update)

    def checkSignal(self, price_update):
        n_order = 10
        if self.long_signal and not self.position:
            print(price_update['date'] + " send buy order for 10 shares price=" + str(price_update['adjprice']))
            self.position += n_order
            self.cash -= n_order*float(price_update['adjprice'])

        if not self.long_signal and self.position:
            print(price_update['date'] + " send sell order for 10 shares price=" + str(price_update['adjprice']))
            self.position -= n_order
            self.cash += n_order*float(price_update['adjprice'])

        self.holdings = self.position * float(price_update['adjprice'])
        self.total = self.holdings + self.cash
        if pd.to_datetime(price_update['date']) >= datetime.datetime(2001, 3, 14):
            print('%s total=%d, holding=%d, cash=%d' % (price_update['date'], self.total, self.holdings, self.cash))


if __name__ == '__main__':
    ts = TradingStrategy()
    with open('input.txt') as f:
        nb_of_rows = int(f.readline().strip())
    f.close()
    df = pd.read_csv('input.txt', parse_dates=True, skiprows=1)

    count = 0
    for index, row in df.iterrows():
        count += 1
        ts.onPriceUpdate({'date': row[0],
                          'close': float(row[4]),
                          'adjprice': float(row[6])})
        if count == nb_of_rows:
            break