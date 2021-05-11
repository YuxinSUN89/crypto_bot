# from binance.client import Client
# import websocket
import pandas as pd
import numpy
import config
import ccxt
import datetime
import time
import schedule
import logging
from other_lib import round_down
from math import ceil, floor
# import ta
# from ta.volatility import BollingerBands
pd.set_option('display.max_rows', None)
print('All installed. Ready to go !')


exchange = ccxt.binance({
    'apiKey' : config.BINANCE_API_KEY,
    'secret' : config.BINANCE_SECRET_KEY,
    'enableRateLimit': True, 
    # 'options': {'defaultType': 'future'}
})


basket = [['DOGE', 'DOGE/USDT'], ['ETH', 'ETH/USDT'], ['BNB', 'BNB/USDT']]

markets = exchange.load_markets()

def get_data(basket, limit=10, timeframe='1m'):
    appended_data = []
    fr_list = []
    for i, name in basket:
        i = exchange.fetch_ohlcv(name, limit=limit, timeframe=timeframe)
        i = pd.DataFrame(i, columns=[['_', name, name, name, name,name], ['timestamp', 'open', 'high', 'low', 'close', 'volume']])
        appended_data.append(i)
        df = pd.concat(appended_data, axis=1, ignore_index=True)


    df = df.drop([6, 12], axis=1)
    df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'open', 'high', 'low', 'close', 'volume', 'open', 'high', 'low', 'close', 'volume'] 
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    new_columns = pd.MultiIndex.from_product([
        ["DOGE", "ETH", "BNB"], 
        ["open", "high", "low", "close", "volume"]
    ])
    df = df.set_index(["timestamp"]).set_axis(new_columns, axis=1)

    df = df.drop(['open', 'high', 'low'],  axis = 1, level = 1)

    for x, _ in basket:
        df.loc[:, (x, 'ema_1m')] = df[x]['close'].rolling(window=1).mean()
    return df

 
df = get_data(basket)
print(df.head(5))

def run_bot():
    df = get_data(basket)
    print(df.tail(3))
    logging.basicConfig(filename='log/{}.log'.format(time.strftime("%Y%m%d")))
    # check your fund
    # get position information 
    balance = exchange.fetch_balance()
    fund = balance.get('USDT')['free']

    try:
        each_buy = ((fund)/3)
    except ZeroDivisionError as e:
        each_buy = 0

    print(f'_____________ Checking now _____ {datetime.datetime.now().isoformat()}')
    try:
        for x, pair in basket:
            print('position for %s is %.3f' %(x, balance.get(x)['free']))
            print(' %s with %.4f coins each batch' %(x, (each_buy/df[x].iloc[-1]['close'])))

            if (df[x].iloc[-1]['close'] > df[x].iloc[-1]['ema_1m']):   # <-- set minimum qty for each buy
                qty = round_down((each_buy/df[x].iloc[-1]['close']), 4)
                print('Just bought %.4f shares of %s at %s . Total fund: %.3f USDT'  %(qty, pair, df[x].iloc[-1]['close'], fund))
                order = exchange.create_market_buy_order(pair, qty)
                logging.warning('{} trading.... '.format(datetime.datetime.now().strftime("%x %X"))) 
                logging.warning('Just bought %.6f shares of %s at %s. Total fund: %.3f USDT' %(qty, pair, df[x].iloc[-1]['close'], fund))

            elif (df[x].iloc[-1]['close'] < df[x].iloc[-1]['ema_1m']):
                print('Just sold %.4f shares of %s at %s. Total fund: %.3f USDT' %(balance.get(x)['free'], x, df[x].iloc[-1]['close'], fund))
                order = exchange.create_market_sell_order(pair, round_down(balance.get(x)['free'], 3))
                logging.warning('{} trading.... '.format(datetime.datetime.now().strftime("%x %X")))
                logging.warning('Just sold %.6f shares of %s at %s. Total fund: %.3f USDT' %(balance.get(x)['free'], x, df[x].iloc[-1]['close'], fund))

            else:
                print('____________ Total fund: %.3f USDT' %(fund))

    except Exception as e:
        print(e)

schedule.every(59).seconds.do(run_bot)

while True:
    schedule.run_pending()
    time.sleep(1)