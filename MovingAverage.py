import math
import os
import random
import re
import sys
import pandas as pd
import numpy as np

pd.set_option('display.max_rows', 10)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

def case1(financial_data):
    print('+++++++++++++ Stock prices and its statistics ++++++++++++++')
    print('\nHead ...')
    print(financial_data.head(5))
    print('\nTail ...')
    print(financial_data.tail(5))
    print('\nStats ...')
    print(financial_data.describe())

def case2(financial_data):
    financial_data['Date'] = pd.to_datetime(financial_data['Date'])
    monthly_mean = financial_data.resample('M', on='Date').mean()
    print('+++++++++++++ Monthly mean prices of the stock ++++++++++++++')
    print(monthly_mean.head(5))
    return(monthly_mean)

def case3(financial_data):
    financial_data.filter(items=['Adj Close'])
    print(financial_data.head(5))
    daily_returns = financial_data['Adj Close'] - financial_data['Adj Close'].shift(1)
    print('+++++++++++++ Daily returns ++++++++++++++')
    print(daily_returns)
    return daily_returns

def case4(financial_data):
    financial_data.filter(items=['Adj Close'])
    print(financial_data.head(5))
    cum_daily_returns = (financial_data['Adj Close'] - financial_data['Adj Close'].shift(1)).cumsum()
    print('+++++++++++++ Cumulative daily returns ++++++++++++++')
    print(cum_daily_returns)
    return cum_daily_returns

def case5(financial_data):
    financial_data['Date'] = pd.to_datetime(financial_data['Date'])
    financial_data['Daily_Returns'] = financial_data['Adj Close'] - financial_data['Adj Close'].shift(1)
    daily_returns = financial_data.resample('M', on='Date').mean()['Daily_Returns']
    print('+++++++++++++ Monthly mean of daily returns ++++++++++++++')
    print(daily_returns)
    return daily_returns

def case6(financial_data):
    rolling = financial_data['Adj Close'].rolling(window=20).mean()
    print('+++++++++++++ Last 20 daily moving averages ++++++++++++++')
    print(rolling.tail(20))
    return rolling

def case7(financial_data):
    daily_volatility = financial_data['Adj Close'].pct_change().rolling(window=100).std()*(100**0.5)
    print('+++++++++++++ Daily volatility ++++++++++++++')
    print(daily_volatility)
    return(daily_volatility)

def case8(financial_data):
    short_rolling = financial_data.rolling(window=50).mean()
    long_rolling = financial_data.rolling(window=100).mean()
    signals = pd.DataFrame()
    signals['Signal'] = short_rolling['Adj Close'] - long_rolling['Adj Close']
    signals.loc[signals['Signal'] > 0, 'Signal'] = 1
    signals.loc[signals['Signal'] <= 0, 'Signal'] = 0
    print(signals.describe())
    signals['Signal'] = signals['Signal'].fillna(0)
    signals['Signal'] = signals['Signal'].astype(int)
    signals['Order'] = signals['Signal'].diff()
    signals['Order'] = signals['Order'].fillna(0)
    signals['Order'] = signals['Order'].astype(int)
    print('+++++++++++++ Signals ++++++++++++++')
    print(signals.to_string())
    return(signals)

def case9(financial_data):
    f = financial_data
    positions = pd.DataFrame(columns=['MSFT'])
    portfolio = pd.DataFrame(columns=['Stock', 'Holdings', 'Cash', 'Total', 'Returns'])
    initial_capital = 10000
    n_order = 10
    signals = case8(financial_data)
    for index, row in financial_data.iterrows():
        if index == 0:
            positions.loc[0] = [0]
        else:
            positions = pd.concat([positions, positions.iloc[index-1, positions.columns.get_loc('MSFT')] +
                                       pd.DataFrame([n_order*signals.iloc[index, signals.columns.get_loc('Order')]],
                                                    columns=['MSFT'])], ignore_index=True)
        a = f.iloc[index, f.columns.get_loc('Adj Close')] * positions.iloc[index, positions.columns.get_loc('MSFT')]
        if index == 0:
            b = initial_capital - a
        else:
            b = portfolio.iloc[index-1, portfolio.columns.get_loc('Cash')] - \
                n_order*f.iloc[index, f.columns.get_loc('Close')]*signals.iloc[index, signals.columns.get_loc('Order')]
        p_list = [a, a, b, a+b, (a+b-initial_capital)/initial_capital]
        portfolio.loc[index] = p_list
    print('\n++++++++++++++ POSITIONS ++++++++++++++++')
    print(positions.to_string())
    print('\n++++++++++++++ PORTFOLIO ++++++++++++++++')
    print(portfolio.to_string())
    return portfolio

if __name__ == '__main__':
    case_number = input().strip()
    df = pd.read_csv('MSFT.csv', parse_dates=True)
    globals()['case' + case_number](df)

