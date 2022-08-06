import enum
import pandas as pd
import numpy as np
from colorama import init, Fore, Back, Style
init(autoreset=True)

class OrderType(enum.Enum):
    LIMIT = 1
    MARKET = 2


class OrderSide(enum.Enum):
    BUY = 1
    SELL = 2


class UndefinedOrderErr(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)
        self.err_message = message
        self.action()
    def action(self):
        print(Back.LIGHTGREEN_EX + Fore.BLACK + f"INPUT ERROR: {self.err_message}")


class MatchingEngine():
    """A class used to model a bid matching engine
    Attributes:
        "order" is modeled as a list containing three elements:
        order = [int: OrderType (LIMIT=1, MARKET=2, IOC=3), int: OrderSide (BUY=1, SELL=2), float: Price, int: Volume,
                int: Order ID]

        "ask_book" is modeled as a list of 3-element lists:
        ask_book = [[Float: Price, Int: Volume, Int: Ask Order ID, Int: OrderType], [Price, Volume, Ask Order ID, Order Type],
                    [Price, Volume, Ask Order ID, Order Type], ..... ]

        "bid_book" is modeled as a list of 3-element lists:
        bid_book = [[Float: Price, Int: Volume, Int: Bid Order ID, Int: OrderType], [Price, Volume, Bid Order ID, Order Type],
                    [Price, Volume, Bid Order ID, Order Type], ..... ]

        "filled_orders" is modeled as a list of 6-element lists:
        filled_orders = [[Float: Price, Int: Volume, Int: Bid Order ID, Str: FILL/PART, Int: Ask Order ID, Str: FILL/PART],
                        [Price, Volume, Bid Order ID, FILL/PART, Ask Order ID, FILL/PART], ... ]
    Methods:
        handle_order: Takes an order and calls the handling function based on OrderType

    """
    def __init__(self):
        self.bid_book = []
        self.ask_book = []
        self.filled_orders = []

    def handle_order(self, order):
        print('\n\n')
        print(Back.LIGHTYELLOW_EX + Fore.BLACK + f'********************* HANDLING ORDER ID {order[4]} .......................')
        print(f'Order Type: {order[0]}  |  Order Side: {order[1]}  |  Price: {order[2]}  |  Volume: {order[3]} \n\n')
        try:
            if order[0] == OrderType.LIMIT.value:
                self.handle_limit_order(order)
            elif order[0] == OrderType.MARKET.value:
                self.handle_market_order(order)
            else:
                raise self.UndefinedOrderErr("Undefined Order Type")
        except UndefinedOrderErr as err:
            print(err, Back.LIGHTYELLOW_EX_EX + Fore.RED + f'\nOrder ID {order[4]} is ambiguous, retry --> {OrderType.LIMIT.name}: {OrderType.LIMIT.value}, '
                  f'{OrderType.MARKET.name}: {OrderType.MARKET.value}, {OrderType.IOC.name}: {OrderType.IOC.value}')

    def execute_buy(self, order):
        cnt = 0
        price = 0
        while True:
            if self.ask_book[cnt][3] != OrderType.MARKET.value:
                if order[0] == OrderType.LIMIT.value:
                    price = min(order[2], self.ask_book[cnt][0])
                elif order[0] == OrderType.MARKET.value:
                    price = self.ask_book[cnt][0]
                break
            cnt += 1
        if order[3] < self.ask_book[0][1]:
            print(f'Buy order filled at {price}.')
            print(f'Ask book lowest listing partially filled at {price}.  Sale volume = {order[3]}.')
            self.filled_orders.append([price, order[3], order[4], 'FILL', self.ask_book[0][2], 'PART'])
            self.ask_book[0][1] -= order[3]
            order[3] = 0
            return 0
        elif order[3] == self.ask_book[0][1]:
            print(f'Buy order filled at {price}.')
            print(f'Ask book lowest listing filled at {price}.')
            self.filled_orders.append([price, order[3], order[4], 'FILL', self.ask_book[0][2], 'FILL'])
            self.ask_book.pop(0)
            if not self.ask_book:
                print(Back.LIGHTYELLOW_EX + Fore.BLACK + 'Ask book empty!')
            order[3] = 0
            return 0
        elif order[3] > self.ask_book[0][1]:
            print(f'Buy order partially filled at {price}.  Sale volume = {self.ask_book[0][1]}.')
            print(f'Ask book lowest listing filled at {price}.')
            self.filled_orders.append([price, self.ask_book[0][1], order[4], 'PART', self.ask_book[0][2], 'FILL'])
            order[3] -= self.ask_book[0][1]
            self.ask_book.pop(0)
            if not self.ask_book:
                print(Back.LIGHTYELLOW_EX + Fore.BLACK + 'Ask book empty!')
            return 1

    def execute_sell(self, order):
        cnt = 0
        price = 0
        while True:
            if self.bid_book[cnt][3] != OrderType.MARKET.value:
                price = self.bid_book[cnt][0]
                break
            cnt += 1
        if order[3] < self.bid_book[0][1]:
            print(f'Sell order filled at {price}.')
            print(f'Bid book highest listing partially filled at {price}.  Sale volume = {order[3]}.')
            self.filled_orders.append([price, order[3], order[4], 'FILL', self.bid_book[0][2], 'PART'])
            self.bid_book[0][1] -= order[3]
            order[3] = 0
            return 0
        elif order[3] == self.bid_book[0][1]:
            print(f'Sell order filled at {price}.')
            print(f'Bid book highest listing filled at {price}.')
            self.filled_orders.append([price, order[3], order[4], 'FILL', self.bid_book[0][2], 'FILL'])
            self.bid_book.pop(0)
            if not self.bid_book:
                print(Back.LIGHTYELLOW_EX + Fore.BLACK + 'Bid book empty!')
            order[3] = 0
            return 0
        elif order[3] > self.bid_book[0][1]:
            print(f'Sell order partially filled at {price}.  Sale volume = {self.bid_book[0][1]}.')
            print(f'Bid book highest listing filled at {price}.')
            self.filled_orders.append([price, self.bid_book[0][1], order[4], 'PART', self.bid_book[0][2], 'FILL'])
            order[3] -= self.bid_book[0][1]
            self.bid_book.pop(0)
            if not self.bid_book:
                print(Back.LIGHTYELLOW_EX + Fore.BLACK + 'Bid book empty!')
            return 1

    def handle_limit_order(self, order):
        try:
            if order[1] == OrderSide.BUY.value:
                if not self.ask_book:
                    # ask_book is empty
                    self.bid_book.insert(0, [order[2], order[3], order[4], order[0]])
                    self.bid_book = sorted(self.bid_book, key=lambda x: (-x[3], -x[0], x[2]))
                else:
                    while order[2] >= self.ask_book[0][0]:
                        flag = self.execute_buy(order)
                        if not flag:
                            break
                    if order[3]:
                        self.bid_book.insert(0, [order[2], order[3], order[4], order[0]])
                        self.bid_book = sorted(self.bid_book, key=lambda x: (-x[3], -x[0], x[2]))
            elif order[1] == OrderSide.SELL.value:
                if not self.bid_book:
                    # bid_book is empty
                    self.ask_book.insert(0, [order[2], order[3], order[4], order[0]])
                    self.ask_book = sorted(self.ask_book, key=lambda x: (-x[3], x[0], x[2]))
                else:
                    while order[2] <= self.bid_book[0][0]:
                        flag = self.execute_sell(order)
                        if not flag:
                            break
                    if order[3]:
                        self.ask_book.insert(0, [order[2], order[3], order[4], order[0]])
                        self.ask_book = sorted(self.ask_book, key=lambda x: (-x[3], x[0], x[2]))
            else:
                raise UndefinedOrderErr("Undefined Order Side!")
        except UndefinedOrderErr as err:
            print(err, Back.LIGHTYELLOW_EX + Fore.RED + f'\nOrder ID {order[4]} is ambiguous, retry --> ')
        self.print_books()

    def handle_market_order(self, order):
        order[2] = 0
        try:
            if order[1] == OrderSide.BUY.value:
                while order[3]:
                    if not self.ask_book:
                        # ask_book is empty
                        self.bid_book.insert(0, [order[2], order[3], order[4], order[0]])
                        self.bid_book = sorted(self.bid_book, key=lambda x: (-x[3], -x[0], x[2]))
                        break
                    else:
                        flag = self.execute_buy(order)
                        if not flag:
                            break
            elif order[1] == OrderSide.SELL.value:
                while order[3]:
                    if not self.bid_book:
                        # bid_book is empty
                        self.ask_book.insert(0, [order[2], order[3], order[4], order[0]])
                        self.ask_book = sorted(self.ask_book, key=lambda x: (-x[3], x[0], x[2]))
                        break
                    else:
                        flag = self.execute_sell(order)
                        if not flag:
                            break
            else:
                raise UndefinedOrderErr("Undefined Order Side!")
        except UndefinedOrderErr as err:
            print(err, Back.LIGHTYELLOW_EX + Fore.RED + f'\nOrder ID {order[4]} is ambiguous, retry --> ')
        self.print_books()

    def print_books(self):
        bid_df = pd.DataFrame(self.bid_book, columns=['Bid Price', 'Bid Vol', 'Bid Order ID', 'Order Type'])
        ask_df = pd.DataFrame(self.ask_book, columns=['Ask Price', 'Ask Vol', 'Ask Order ID', 'Order Type'])
        bid_ask_df_list = [bid_df, ask_df]
        bid_ask_df = pd.concat(bid_ask_df_list, axis=1)
        bid_ask_df = bid_ask_df.replace(np.nan, '--', regex=True)
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        filled_orders_df = pd.DataFrame(self.filled_orders, columns=['Price', 'Volume', 'Bid Order ID', 'PART/FILL', 'Ask Order ID', 'PART/FILL'])
        print(filled_orders_df.to_string())
        print('-----------------------------')
        print(bid_ask_df.to_string())


df = pd.read_csv('orders.txt', skiprows=0)
print(df)
my_matching_engine = MatchingEngine()
for index, row in df.iterrows():
    order = [int(row['OrderType']), int(row['OrderSide']), float(row['Price']), int(row['Volume']), int(row['OrderID'])]
    my_matching_engine.handle_order(order)

