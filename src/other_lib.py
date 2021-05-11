import pandas as pd
import numpy as np
import config
import ccxt
import requests
import json
import csv
import decimal
import datetime
 

# This function returns position
def get_position():
    exchange = ccxt.binance({
        'apiKey' : config.BINANCE_API_KEY,
        'secret' : config.BINANCE_SECRET_KEY,
        'enableRateLimit': True, 
        # 'options': {'defaultType': 'future'}
    })
    balance = exchange.fetch_balance()
    
    doge = balance.get('DOGE')
    btc = balance.get('BTC')
    eth = balance.get('ETH')
    ada = balance.get('ADA')
    fil = balance.get('FIL')
    fund = balance.get('GBP')
    return fund, btc, eth, ada, doge, fil, 
 
def round_down(value, decimals):
    with decimal.localcontext() as ctx:
        d = decimal.Decimal(value)
        ctx.rounding = decimal.ROUND_DOWN
        return round(d, decimals)

 
def time_check():
    cond = ((9<(datetime.datetime.now().hour)<=9) 
        or (15<(datetime.datetime.now().hour)<=17) 
        or (1<(datetime.datetime.now().hour)<=2 ))
    if cond:
        return True
    else:
        print('Not checking time now....go back to sleep')
