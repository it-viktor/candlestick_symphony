import dateparser
import pytz
from math import floor
from datetime import datetime, timedelta
from binance.client import Client
from binance.enums import *
import time
import os
import requests
from threading import Thread
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


api_key = "you_api_binance_futures"
api_secret = "you_api_secret_binance_futures"    
symbol_hold = 'USDT'
symbol_trade = 'CELR'
doji_difference = float(0.0001)
trade_pair = symbol_trade + symbol_hold
leverage_trade = 10
client.futures_change_leverage(symbol = trade_pair, leverage = leverage_trade)
time.sleep(0.5)
client = Client(api_key, api_secret)
time.sleep(0.5)

telegram_notification = False
api_tg = 'you_api_telegram'


def tg_get_update():
    url = f'https://api.telegram.org/bot{api_tg}/getUpdates'
    r = requests.get(url)
    r = r.json()
    chat_id = r['result'][-1]['message']['chat']['id']
    return chat_id

chat_it_tg = tg_get_update()


def tg_send_m(api_tg, chat_it_tg, text_m_tg):
    tmp_tg_m = requests.get(f'https://api.telegram.org/bot{api_tg}/sendmessage?chat_id={chat_id_tg}&text={text_m_tg}')

#  Convert milliseconds to date
def datetime_from_millis(millis, epoch=datetime(1970, 1, 1)):
    """Return UTC time that corresponds to milliseconds since Epoch."""
    return epoch + timedelta(milliseconds=millis)


def check_hold_balance():
    try:
        balance = client.futures_account_balance()
        time.sleep(0.5)
        balance_hold_symbol = float(0)
        for i in range(len(balance)):
            if balance[i]['asset'] != symbol_hold:
                continue
            balance_hold_symbol = balance[i]['balance']
        balance_hold_symbol = float(balance_hold_symbol)
        return balance_hold_symbol
    except Exception:
        print(bcolors.FAIL + f"ERROR!!!! 'check_hold_balance'" + bcolors.ENDC)
        res_long = float(client.futures_position_information(symbol = trade_pair)[1]['positionAmt'])
        time.sleep(0.5)
        res_short = float(client.futures_position_information(symbol = trade_pair)[2]['positionAmt'])
        if res_long > 0.0:
            time.sleep(0.5)
            client.futures_create_order(symbol=trade_pair, side='SELL', type='MARKET', positionSide='LONG', quantity=int(res_long))
            res_long = float(0)
        if res_short < 0.0:
            time.sleep(0.5)
            tmp_short_b = str(client.futures_position_information(symbol = trade_pair)[2]['positionAmt'])[1:]
            res_short = float(tmp_short_b)
            client.futures_create_order(symbol=trade_pair, side='BUY', type='MARKET', positionSide='SHORT', quantity=int(res_short))
            res_short = float(0)
        if res_long == 0.0 and res_short == 0.0:
            time.sleep(0.5)
            client.futures_cancel_all_open_orders(symbol = trade_pair)
        if telegram_notification == True:
            tg_send_m(api_tg, chat_it_tg, 'ERROR!!!! check_hold_balance')
        raise

print(f'Balance: {int(check_hold_balance())} USDT')
print(f'Symbol trade: {trade_pair}')
print(f'Leverage: {leverage_trade}')
print(f'Doji diff: {doji_difference}')

def calculate_summ_order_in():
    try:
        symbol_trade_price = float(client.get_avg_price(symbol=trade_pair)['price'])
        time.sleep(0.5)
        balance = client.futures_account_balance()
        time.sleep(0.5)
        balance_hold_symbol = float(0)
        for i in range(len(balance)):
            if balance[i]['asset'] != symbol_hold:
                continue
            balance_hold_symbol = balance[i]['balance']
        balance_max = (float(balance_hold_symbol) * leverage_trade) / symbol_trade_price
        long = float(client.futures_position_information(symbol = trade_pair)[1]['positionAmt'])
        time.sleep(0.5)
        short = float(client.futures_position_information(symbol = trade_pair)[2]['positionAmt'])
        time.sleep(0.5)
        if short < 0.0:
            short = str(short)[1:]
            short = float(short)
        market_position_summ = float(balance_max / 2)
        market_position_summ -= market_position_summ / 10
        limit_average_position_summ = str(int(market_position_summ / 4))
        market_position_summ = str(int(market_position_summ / 2))
        return market_position_summ, limit_average_position_summ
    except Exception:
        print(bcolors.FAIL + f"ERROR!!!! 'calculate_summ_order_in'" + bcolors.ENDC)
        res_long = float(client.futures_position_information(symbol = trade_pair)[1]['positionAmt'])
        time.sleep(0.5)
        res_short = float(client.futures_position_information(symbol = trade_pair)[2]['positionAmt'])
        if res_long > 0.0:
            time.sleep(0.5)
            client.futures_create_order(symbol=trade_pair, side='SELL', type='MARKET', positionSide='LONG', quantity=int(res_long))
            res_long = float(0)
        if res_short < 0.0:
            time.sleep(0.5)
            tmp_short_b = str(client.futures_position_information(symbol = trade_pair)[2]['positionAmt'])[1:]
            res_short = float(tmp_short_b)
            client.futures_create_order(symbol=trade_pair, side='BUY', type='MARKET', positionSide='SHORT', quantity=int(res_short))
            res_short = float(0)
        if res_long == 0.0 and res_short == 0.0:
            time.sleep(0.5)
            client.futures_cancel_all_open_orders(symbol = trade_pair)
        if telegram_notification == True:
            tg_send_m(api_tg, chat_it_tg, 'ERROR!!!! calculate_summ_order_in')
        raise

flag_long = False
flag_short = False
count_main = 0
def search_doji():
    try:
        global flag_long
        global flag_short
        global count_main
        Open = 0
        Close = 0
        High = 0
        Low = 0
        flag = True
        time_m_tmp = '-15'
        print()
        print(trade_pair, 'System  time:', time.strftime('%Y-%m-%d %H:%M', time.localtime()), 'Start the bot in search of the doji star...')
        if telegram_notification == True:
        	tg_send_m(api_tg, chat_it_tg, 'Start the bot in search of the doji star...')
        while flag == True:
            time.sleep(1)
            tmp_localtime_m = str(time.strftime('%M', time.localtime(time.time()))[-2:])
            not_continue_time = ['59', '00', '14', '15', '29', '30', '44', '45']
            if tmp_localtime_m not in not_continue_time:
                continue
            time_m = str(datetime_from_millis(client.get_server_time()['serverTime']))[14:16]
            time.sleep(0.5)
            if time_m_tmp != time_m:
                if time_m == '00' or time_m == '15' or time_m == '30' or time_m == '45':
                    klines = client.get_historical_klines(trade_pair, Client.KLINE_INTERVAL_15MINUTE, "75 minute ago UTC", klines_type = HistoricalKlinesType.FUTURES)
                    time.sleep(0.5)
                    check_bar = klines[-2]
                    convert_date = str(datetime_from_millis(check_bar[0]))
                    convert_date = convert_date[-5:-3]
                    if convert_date != time.strftime('%M', time.localtime(time.time() - 900))[-2:]:
                        time.sleep(1)
                        continue
                    Open = float(check_bar[1])
                    Close = float(check_bar[4])
                    High = float(check_bar[2])
                    Low = float(check_bar[3])
                    if time_m_tmp == '-15':
                        time_m_tmp = time_m
                        Open, Close, High, Low = 0, 0, 0, 0
                        continue
                    else:
                        if Open <= Close and Close < Open + doji_difference or Open >= Close and Close > Open - doji_difference:
                            print(trade_pair, 'System  time:', time.strftime('%Y-%m-%d %H:%M', time.localtime()), 'Open:', Open, 'Close:', Close, 'doji !!!SUCCESS!!')
                            check_bar2 = klines[-3]
                            Open2 = float(check_bar2[1])
                            Close2 = float(check_bar2[4])
                            High2 = float(check_bar2[2])
                            Low2 = float(check_bar2[3])
                            check_bar3 = klines[-4]
                            Open3 = float(check_bar3[1])
                            Close3 = float(check_bar3[4])
                            High3 = float(check_bar3[2])
                            Low3 = float(check_bar3[3])
                            if Open2 < Close2 and Open3 < Close3 and High > High2 and High2 > High3:
                                print()
                                print(bcolors.FAIL + trade_pair, 'System  time:', time.strftime('%Y-%m-%d %H:%M', time.localtime()), 'Short signal' + bcolors.ENDC)
                                if telegram_notification == True:
                                    tg_send_m(api_tg, chat_it_tg, 'Short signal in')
                                    balance_tg = f'Balance {int(check_hold_balance())} USDT'
                                    tg_send_m(api_tg, chat_it_tg, balance_tg)
                                    int(check_hold_balance())
                                if flag_short == False:
                                    flag_short = True
                                    count_main -= 1
                                    place_doji_short(High, Open, Close, Low)
                                    flag_short = False
                                    break
                                count_main -= 1
                                break
                            elif Open2 > Close2 and Open3 > Close3 and Low < Low2 and Low2 < Low3:
                                print()
                                print(bcolors.OKGREEN + trade_pair, 'System  time:', time.strftime('%Y-%m-%d %H:%M', time.localtime()), 'Long signal' + bcolors.ENDC)
                                if telegram_notification == True:
                                    tg_send_m(api_tg, chat_it_tg, 'Long signal in')
                                    balance_tg = f'Balance {int(check_hold_balance())} USDT'
                                    tg_send_m(api_tg, chat_it_tg, balance_tg)
                                if flag_long == False:
                                    flag_long = True
                                    count_main -= 1
                                    place_doji_long(High, Open, Close, Low)
                                    flag_long = False
                                    break
                                print('flag_long == True')
                                count_main -= 1
                                break
                            print(trade_pair, 'System  time:', time.strftime('%Y-%m-%d %H:%M', time.localtime()), 'Doji appeared in the wrong conditions, we are waiting for the next one ...')
                            time_m_tmp = time_m
                            Open, Close, High, Low = 0, 0, 0, 0
                            continue
                        else:
                            print(trade_pair, 'System  time:', time.strftime('%Y-%m-%d %H:%M', time.localtime()), 'Open:', Open, 'Close:', Close, 'Candle not recognized')
                            time_m_tmp = time_m
                            Open, Close, High, Low = 0, 0, 0, 0
            else:
                time_m_tmp = time_m
                Open, Close, High, Low = 0, 0, 0, 0
    except Exception:
        print(bcolors.FAIL + f"ERROR!!!! 'search_doji'" + bcolors.ENDC)
        res_long = float(client.futures_position_information(symbol = trade_pair)[1]['positionAmt'])
        time.sleep(0.5)
        res_short = float(client.futures_position_information(symbol = trade_pair)[2]['positionAmt'])
        if res_long > 0.0:
            time.sleep(0.5)
            client.futures_create_order(symbol=trade_pair, side='SELL', type='MARKET', positionSide='LONG', quantity=int(res_long))
            res_long = float(0)
        if res_short < 0.0:
            time.sleep(0.5)
            tmp_short_b = str(client.futures_position_information(symbol = trade_pair)[2]['positionAmt'])[1:]
            res_short = float(tmp_short_b)
            client.futures_create_order(symbol=trade_pair, side='BUY', type='MARKET', positionSide='SHORT', quantity=int(res_short))
            res_short = float(0)
        if res_long == 0.0 and res_short == 0.0:
            time.sleep(0.5)
            client.futures_cancel_all_open_orders(symbol = trade_pair)
        if telegram_notification == True:
            tg_send_m(api_tg, chat_it_tg, 'ERROR!!!! search_doji')
        raise

average_order_long1 = 0
average_order_long2 = 0
average_order_short1 = 0
average_order_short2 = 0

def place_doji_long(High, Open, Close, Low):
    try:
        global average_order_long1
        global average_order_long2
        market_position_summ, limit_average_position_summ = calculate_summ_order_in()
        symbol_trade_price = float(client.get_avg_price(symbol=trade_pair)['price'])
        time.sleep(0.5)
        limit_position_price = float()
        limit_position2_price = float()
        price_sl = float(Low - ((Low / 100) * 0.2))
        if Open >= Close:
            limit_position_price = ((Close - Low) / 2) + Low
            limit_position2_price = (((Close - Low) / 2) / 3) + Low
        elif Close >= Open:
            limit_position_price = ((Open - Low) / 2) + Low
            limit_position2_price = (((Open - Low) / 2) / 3) + Low
        if len(str(Open)) != len(str(limit_position_price)):
            limit_position_price = float(str(limit_position_price)[0:len(str(Open))])
        if len(str(Open)) != len(str(limit_position2_price)):
            limit_position2_price = float(str(limit_position2_price)[0:len(str(Open))])
        if len(str(Open)) != len(str(price_sl)):
            price_sl = float(str(price_sl)[0:len(str(Open))])
        print('Calc summ for market order:', market_position_summ)
        print('Calc summ for limit orders:', limit_average_position_summ)
        print()
        print('Calc price for limit1 order:', limit_position_price)
        print('Calc price for limit2 order:', limit_position2_price)
        print('Calc price for SL:', price_sl)
        # PLACE_ORDER
        # buy_market
        info_order_market = client.futures_create_order(symbol = trade_pair, side = 'BUY', type = 'MARKET', positionSide = 'LONG', quantity = int(market_position_summ))
        time.sleep(0.5)
        # sl
        info_order_sl = client.futures_create_order(symbol=trade_pair, side = 'SELL', type = 'STOP_MARKET', positionSide='LONG', stopPrice = price_sl, closePosition = 'true', timeInForce='GTC')
        time.sleep(0.5)
        # buy_limit
        info_order_limit1 = client.futures_create_order(symbol = trade_pair, side = 'BUY', type = 'LIMIT', price = limit_position_price, positionSide = 'LONG', quantity = int(limit_average_position_summ), timeInForce='GTC')
        time.sleep(0.5)
        # buy_limit
        info_order_limit2 = client.futures_create_order(symbol = trade_pair, side = 'BUY', type = 'LIMIT', price = limit_position2_price, positionSide = 'LONG', quantity = int(limit_average_position_summ), timeInForce='GTC')
        time.sleep(0.5)
        info_order_market_price = client.futures_get_order(symbol = trade_pair, orderId = info_order_market['orderId'])['avgPrice']
        time.sleep(0.5)
        print()
        print(f"Binance time: {str(datetime_from_millis(info_order_market['updateTime']))[0:19]} {info_order_market['symbol']} {info_order_market['positionSide']} orderId:{info_order_market['orderId']} price:{info_order_market_price} size:{info_order_market['origQty']} {info_order_market['type']} {info_order_market['side']}")
        print(f"Binance time: {str(datetime_from_millis(info_order_sl['updateTime']))[0:19]} {info_order_sl['symbol']} {info_order_sl['positionSide']} orderId:{info_order_sl['orderId']} price:{info_order_sl['price']} size:{info_order_sl['origQty']} {info_order_sl['type']} {info_order_sl['side']}")
        print(f"Binance time: {str(datetime_from_millis(info_order_limit1['updateTime']))[0:19]} {info_order_limit1['symbol']} {info_order_limit1['positionSide']} orderId:{info_order_limit1['orderId']} price:{info_order_limit1['price']} size:{info_order_limit1['origQty']} {info_order_limit1['type']} {info_order_limit1['side']}")
        print(f"Binance time: {str(datetime_from_millis(info_order_limit2['updateTime']))[0:19]} {info_order_limit2['symbol']} {info_order_limit2['positionSide']} orderId:{info_order_limit2['orderId']} price:{info_order_limit2['price']} size:{info_order_limit2['origQty']} {info_order_limit2['type']} {info_order_limit2['side']}")
        print()
        # CALCULATION_POSITION
        check_position_volume = float(client.futures_position_information(symbol = trade_pair)[1]['positionAmt'])
        time.sleep(0.5)
        check_position_volume_price = client.futures_position_information(symbol = trade_pair)[1]['entryPrice']
        time.sleep(0.5)
        print()
        print('Check position volume', check_position_volume)
        print('Check position volume price(average)', check_position_volume_price)
        half_position = check_position_volume / 2
        limit_average_position_summ = half_position / 5
        if len(str(check_position_volume_price)) != len(str(Open)):
            check_position_volume_price = str(check_position_volume_price)[0:len(str(Open))]
        side_tp = ''
        position_in_usdt = float(check_position_volume_price) * float(check_position_volume)
        tp_usdt = position_in_usdt + (position_in_usdt / 100) * 7
        side_tp = tp_usdt / float(check_position_volume)
        if len(str(side_tp)) != len(str(Open)):
            side_tp = str(side_tp)[0:len(str(Open))]
        side_tp = float(side_tp)
        basic_position_vol_price = float(check_position_volume_price) + ((float(check_position_volume_price) / 100) * 0.58)
        if len(str(basic_position_vol_price)) != len(str(Open)):
            basic_position_vol_price = str(basic_position_vol_price)[0:len(str(Open))]
        basic_position_vol_price = float(basic_position_vol_price)
        limit_position_vol_price = float(check_position_volume_price) + (float(check_position_volume_price) / 100) * 2
        if len(str(limit_position_vol_price)) != len(str(Open)):
            limit_position_vol_price = str(limit_position_vol_price)[0:len(str(Open))]
        limit_position_vol_price = float(limit_position_vol_price)
        limit_position_vol_price2 = float(check_position_volume_price) + (float(check_position_volume_price) / 100) * 3
        if len(str(limit_position_vol_price2)) != len(str(Open)):
            limit_position_vol_price2 = str(limit_position_vol_price2)[0:len(str(Open))]
        limit_position_vol_price2 = float(limit_position_vol_price2)
        limit_position_vol_price3 = float(check_position_volume_price) + (float(check_position_volume_price) / 100) * 5
        if len(str(limit_position_vol_price3)) != len(str(Open)):
            limit_position_vol_price3 = str(limit_position_vol_price3)[0:len(str(Open))]
        limit_position_vol_price3 = float(limit_position_vol_price3)
        limit_position_vol_price4 = float(check_position_volume_price) + (float(check_position_volume_price) / 100) * 6
        if len(str(limit_position_vol_price4)) != len(str(Open)):
            limit_position_vol_price4 = str(limit_position_vol_price4)[0:len(str(Open))]
        limit_position_vol_price4 = float(limit_position_vol_price4)
        print()
        print('Calc summ for basic order:', half_position)
        print('Calc summ for limit orders:', limit_average_position_summ)
        print()
        print('Calc price for basic order:', basic_position_vol_price)
        print('Calc price for limit TP 1', limit_position_vol_price)
        print('Calc price for limit TP 2', limit_position_vol_price2)
        print('Calc price for limit TP 3', limit_position_vol_price3)
        print('Calc price for limit TP 4', limit_position_vol_price4)
        print('Calc price for TP', side_tp)
        # PLACE_PROFIT_ORDER
        # half_position_limit_order
        info_order_half = client.futures_create_order(symbol = trade_pair, side = 'SELL', type = 'LIMIT', price = basic_position_vol_price, positionSide = 'LONG', quantity = int(half_position), timeInForce='GTC')
        time.sleep(0.5)
        # tp_ limit_order1
        info_order_limit_tp = client.futures_create_order(symbol = trade_pair, side = 'SELL', type = 'LIMIT', price = limit_position_vol_price, positionSide = 'LONG', quantity = int(limit_average_position_summ), timeInForce='GTC')
        time.sleep(0.5)
        # tp_ limit_order2
        info_order_limit_tp2 = client.futures_create_order(symbol = trade_pair, side = 'SELL', type = 'LIMIT', price = limit_position_vol_price2, positionSide = 'LONG', quantity = int(limit_average_position_summ), timeInForce='GTC')
        time.sleep(0.5)
        # tp_ limit_order3
        info_order_limit_tp3 = client.futures_create_order(symbol = trade_pair, side = 'SELL', type = 'LIMIT', price = limit_position_vol_price3, positionSide = 'LONG', quantity = int(limit_average_position_summ), timeInForce='GTC')
        time.sleep(0.5)
        # tp_ limit_order4
        info_order_limit_tp4 = client.futures_create_order(symbol = trade_pair, side = 'SELL', type = 'LIMIT', price = limit_position_vol_price4, positionSide = 'LONG', quantity = int(limit_average_position_summ), timeInForce='GTC')
        time.sleep(0.5)
        # TAKE_PROFIT
        info_order_tp = client.futures_create_order(symbol=trade_pair, side = 'SELL', type = 'TAKE_PROFIT_MARKET', positionSide='LONG', stopPrice = side_tp, closePosition = 'true', timeInForce='GTC')
        time.sleep(0.5)
        print()
        print(f"Binance time: {str(datetime_from_millis(info_order_half['updateTime']))[0:19]} {info_order_half['symbol']} {info_order_half['positionSide']} orderId:{info_order_half['orderId']} price:{info_order_half['price']} size:{info_order_half['origQty']} {info_order_half['type']} {info_order_half['side']}")
        print(f"Binance time: {str(datetime_from_millis(info_order_limit_tp['updateTime']))[0:19]} {info_order_limit_tp['symbol']} {info_order_limit_tp['positionSide']} orderId:{info_order_limit_tp['orderId']} price:{info_order_limit_tp['price']} size:{info_order_limit_tp['origQty']} {info_order_limit_tp['type']} {info_order_limit_tp['side']}")
        print(f"Binance time: {str(datetime_from_millis(info_order_limit_tp2['updateTime']))[0:19]} {info_order_limit_tp2['symbol']} {info_order_limit_tp2['positionSide']} orderId:{info_order_limit_tp2['orderId']} price:{info_order_limit_tp2['price']} size:{info_order_limit_tp2['origQty']} {info_order_limit_tp2['type']} {info_order_limit_tp2['side']}")
        print(f"Binance time: {str(datetime_from_millis(info_order_limit_tp3['updateTime']))[0:19]} {info_order_limit_tp3['symbol']} {info_order_limit_tp3['positionSide']} orderId:{info_order_limit_tp3['orderId']} price:{info_order_limit_tp3['price']} size:{info_order_limit_tp3['origQty']} {info_order_limit_tp3['type']} {info_order_limit_tp3['side']}")
        print(f"Binance time: {str(datetime_from_millis(info_order_limit_tp4['updateTime']))[0:19]} {info_order_limit_tp4['symbol']} {info_order_limit_tp4['positionSide']} orderId:{info_order_limit_tp4['orderId']} price:{info_order_limit_tp4['price']} size:{info_order_limit_tp4['origQty']} {info_order_limit_tp4['type']} {info_order_limit_tp4['side']}")
        print(f"Binance time: {str(datetime_from_millis(info_order_tp['updateTime']))[0:19]} {info_order_tp['symbol']} {info_order_tp['positionSide']} orderId:{info_order_tp['orderId']} price:{info_order_tp['price']} size:{info_order_tp['origQty']} {info_order_tp['type']} {info_order_tp['side']}")
        print()
        base_id_orders = client.futures_get_open_orders()
        time.sleep(0.5)
        volume_id_orders = len(base_id_orders)
        tmp_id_order = 0
        for i in range(volume_id_orders):
            if base_id_orders[i]['positionSide'] == 'LONG':
                tmp_id_order += 1
        succes_place_volume_orders = tmp_id_order + 1
        print(bcolors.OKGREEN + trade_pair, 'System  time:', time.strftime('%Y-%m-%d %H:%M', time.localtime()), 'LONG Success Place', succes_place_volume_orders, 'Orders. Await results....' + bcolors.ENDC + bcolors.ENDC)
        print()
        flag = True
        while flag == True:
            time.sleep(10)
            check_position_volume_for_zero = int(client.futures_position_information(symbol = trade_pair)[1]['positionAmt'])
            time.sleep(0.5)
            if check_position_volume_for_zero == 0:
                print(bcolors.OKGREEN + trade_pair, 'System  time:', time.strftime('%Y-%m-%d %H:%M', time.localtime()), 'LONG Position balance 0!!! Close all open', trade_pair, 'oders...' + bcolors.ENDC)
                base_id_orders = client.futures_get_open_orders()
                time.sleep(0.5)
                volume_id_orders = len(base_id_orders)
                for i in range(volume_id_orders):
                    time.sleep(1)
                    tmp2_id_order = ''
                    if base_id_orders[i]['positionSide'] == 'LONG':
                        tmp2_id_order = base_id_orders[i]['orderId']
                        client.futures_cancel_order(symbol = trade_pair, orderId = tmp2_id_order)
                        time.sleep(0.5)
                        print(f'Close order id:{tmp2_id_order}')
                average_order_long1, average_order_long2 = 0, 0
                break
            average_long(info_order_limit1, info_order_limit2, limit_position_vol_price, limit_position_vol_price2, limit_position_vol_price3, limit_position_vol_price4)
        print()
        if telegram_notification == True:
            balance_tg = f'Balance {int(check_hold_balance())} USDT'
            tg_send_m(api_tg, chat_it_tg, balance_tg)
        print(balance_tg)
        print(f'Symbol trade: {trade_pair}')
        print('Check results in exchange,  GOOD LUCK!!')
        print()
        print()
        print(f'\n         --future_trade_bot--')
        print(bcolors.WARNING + f'         candlestick_symphony' + bcolors.ENDC)
        print(f'         -Let the Game Begin-\n         -------- + ---------')
        print()
        print(f'         ----If Your Like:---')
        print(bcolors.WARNING + f'-Donate for the development of the bot-' + bcolors.ENDC)
        print(f'         And wait for Update...\n-------------USDT TRC20----------------\n--THNh5f5MBBVpP7MvzCZdSeNCMzzadG6Ld4---\n' + bcolors.ENDC)
    except Exception:
        print(bcolors.FAIL + f"ERROR!!!! 'place_doji_long'" + bcolors.ENDC)
        res_long = float(client.futures_position_information(symbol = trade_pair)[1]['positionAmt'])
        time.sleep(0.5)
        res_short = float(client.futures_position_information(symbol = trade_pair)[2]['positionAmt'])
        if res_long > 0.0:
            time.sleep(0.5)
            client.futures_create_order(symbol=trade_pair, side='SELL', type='MARKET', positionSide='LONG', quantity=int(res_long))
            res_long = float(0)
        if res_short < 0.0:
            time.sleep(0.5)
            tmp_short_b = str(client.futures_position_information(symbol = trade_pair)[2]['positionAmt'])[1:]
            res_short = float(tmp_short_b)
            client.futures_create_order(symbol=trade_pair, side='BUY', type='MARKET', positionSide='SHORT', quantity=int(res_short))
            res_short = float(0)
        if res_long == 0.0 and res_short == 0.0:
            time.sleep(0.5)
            client.futures_cancel_all_open_orders(symbol = trade_pair)
        if telegram_notification == True:
            tg_send_m(api_tg, chat_it_tg, 'ERROR!!!! place_doji_long')
        raise

def place_doji_short(High, Open, Close, Low):
    try:
        global average_order_short1
        global average_order_short2
        market_position_summ, limit_average_position_summ = calculate_summ_order_in()
        symbol_trade_price = float(client.get_avg_price(symbol=trade_pair)['price'])
        time.sleep(0.5)
        limit_position_price = float()
        limit_position2_price = float()
        price_sl = float(High + ((High / 100) * 0.2))
        if Open >= Close:
            limit_position_price = High - ((High - Open) / 2)
            limit_position2_price = High - (((High - Open) / 2) / 3)
        elif Close >= Open:
            limit_position_price = High - ((High - Close) / 2)
            limit_position2_price = High - (((High - Close) / 2) / 3)
        if len(str(Open)) != len(str(limit_position_price)):
            limit_position_price = float(str(limit_position_price)[0:len(str(Open))])
        if len(str(Open)) != len(str(limit_position2_price)):
            limit_position2_price = float(str(limit_position2_price)[0:len(str(Open))])
        if len(str(Open)) != len(str(price_sl)):
            price_sl = float(str(price_sl)[0:len(str(Open))])
        print('Calc summ for market order:', market_position_summ)
        print('Calc summ for limit orders:', limit_average_position_summ)
        print()
        print('Calc price for limit1 order:', limit_position_price)
        print('Calc price for limit2 order:', limit_position2_price)
        print('Calc price for SL:', price_sl)
        # PLACE_ORDER
        # buy_market
        info_order_market = client.futures_create_order(symbol = trade_pair, side = 'SELL', type = 'MARKET', positionSide = 'SHORT', quantity = int(market_position_summ))
        time.sleep(0.5)
        # sl
        info_order_sl = client.futures_create_order(symbol=trade_pair, side = 'BUY', type = 'STOP_MARKET', positionSide='SHORT', stopPrice = price_sl, closePosition = 'true', timeInForce='GTC')
        time.sleep(0.5)
        # buy_limit
        info_order_limit1 = client.futures_create_order(symbol = trade_pair, side = 'SELL', type = 'LIMIT', price = limit_position_price, positionSide = 'SHORT', quantity = int(limit_average_position_summ), timeInForce='GTC')
        time.sleep(0.5)
        # buy_limit
        info_order_limit2 = client.futures_create_order(symbol = trade_pair, side = 'SELL', type = 'LIMIT', price = limit_position2_price, positionSide = 'SHORT', quantity = int(limit_average_position_summ), timeInForce='GTC')
        time.sleep(0.5)
        info_order_market_price = client.futures_get_order(symbol = trade_pair, orderId = info_order_market['orderId'])['avgPrice']
        time.sleep(0.5)
        print()
        print(f"Binance time: {str(datetime_from_millis(info_order_market['updateTime']))[0:19]} {info_order_market['symbol']} {info_order_market['positionSide']} orderId:{info_order_market['orderId']} price:{info_order_market_price} size:{info_order_market['origQty']} {info_order_market['type']} {info_order_market['side']}")
        print(f"Binance time: {str(datetime_from_millis(info_order_sl['updateTime']))[0:19]} {info_order_sl['symbol']} {info_order_sl['positionSide']} orderId:{info_order_sl['orderId']} price:{info_order_sl['price']} size:{info_order_sl['origQty']} {info_order_sl['type']} {info_order_sl['side']}")
        print(f"Binance time: {str(datetime_from_millis(info_order_limit1['updateTime']))[0:19]} {info_order_limit1['symbol']} {info_order_limit1['positionSide']} orderId:{info_order_limit1['orderId']} price:{info_order_limit1['price']} size:{info_order_limit1['origQty']} {info_order_limit1['type']} {info_order_limit1['side']}")
        print(f"Binance time: {str(datetime_from_millis(info_order_limit2['updateTime']))[0:19]} {info_order_limit2['symbol']} {info_order_limit2['positionSide']} orderId:{info_order_limit2['orderId']} price:{info_order_limit2['price']} size:{info_order_limit2['origQty']} {info_order_limit2['type']} {info_order_limit2['side']}")
        print()
        # CALCULATION_POSITION
        check_position_volume = str(client.futures_position_information(symbol = trade_pair)[2]['positionAmt'])[1:]
        time.sleep(0.5)
        check_position_volume = float(check_position_volume)
        check_position_volume_price = client.futures_position_information(symbol = trade_pair)[2]['entryPrice']
        time.sleep(0.5)
        print()
        print('Check position volume', check_position_volume)
        print('Check position volume price(average)', check_position_volume_price)
        half_position = check_position_volume / 2
        limit_average_position_summ = half_position / 5
        if len(str(check_position_volume_price)) != len(str(Open)):
            check_position_volume_price = str(check_position_volume_price)[0:len(str(Open))]
        side_tp = ''
        position_in_usdt = float(check_position_volume_price) * float(check_position_volume)
        tp_usdt = position_in_usdt - (position_in_usdt / 100) * 7
        side_tp = tp_usdt / float(check_position_volume)
        if len(str(side_tp)) != len(str(Open)):
            side_tp = str(side_tp)[0:len(str(Open))]
        side_tp = float(side_tp)
        basic_position_vol_price = float(check_position_volume_price) - ((float(check_position_volume_price) / 100) * 0.58)
        if len(str(basic_position_vol_price)) != len(str(Open)):
            basic_position_vol_price = str(basic_position_vol_price)[0:len(str(Open))]
        basic_position_vol_price = float(basic_position_vol_price)
        limit_position_vol_price = float(check_position_volume_price) - (float(check_position_volume_price) / 100) * 2
        if len(str(limit_position_vol_price)) != len(str(Open)):
            limit_position_vol_price = str(limit_position_vol_price)[0:len(str(Open))]
        limit_position_vol_price = float(limit_position_vol_price)
        limit_position_vol_price2 = float(check_position_volume_price) - (float(check_position_volume_price) / 100) * 3
        if len(str(limit_position_vol_price2)) != len(str(Open)):
            limit_position_vol_price2 = str(limit_position_vol_price2)[0:len(str(Open))]
        limit_position_vol_price2 = float(limit_position_vol_price2)
        limit_position_vol_price3 = float(check_position_volume_price) - (float(check_position_volume_price) / 100) * 5
        if len(str(limit_position_vol_price3)) != len(str(Open)):
            limit_position_vol_price3 = str(limit_position_vol_price3)[0:len(str(Open))]
        limit_position_vol_price3 = float(limit_position_vol_price3)
        limit_position_vol_price4 = float(check_position_volume_price) - (float(check_position_volume_price) / 100) * 6
        if len(str(limit_position_vol_price4)) != len(str(Open)):
            limit_position_vol_price4 = str(limit_position_vol_price4)[0:len(str(Open))]
        limit_position_vol_price4 = float(limit_position_vol_price4)
        print()
        print('Calc summ for basic order:', half_position)
        print('Calc summ for limit orders:', limit_average_position_summ)
        print()
        print('Calc price for basic order:', basic_position_vol_price)
        print('Calc price for limit TP 1', limit_position_vol_price)
        print('Calc price for limit TP 2', limit_position_vol_price2)
        print('Calc price for limit TP 3', limit_position_vol_price3)
        print('Calc price for limit TP 4', limit_position_vol_price4)
        print('Calc price for TP', side_tp)
        # PLACE_PROFIT_ORDER
        # half_position_limit_order
        info_order_half = client.futures_create_order(symbol = trade_pair, side = 'BUY', type = 'LIMIT', price = basic_position_vol_price, positionSide = 'SHORT', quantity = int(half_position), timeInForce='GTC')
        time.sleep(0.5)
        # tp_ limit_order1
        info_order_limit_tp = client.futures_create_order(symbol = trade_pair, side = 'BUY', type = 'LIMIT', price = limit_position_vol_price, positionSide = 'SHORT', quantity = int(limit_average_position_summ), timeInForce='GTC')
        time.sleep(0.5)
        # tp_ limit_order2
        info_order_limit_tp2 = client.futures_create_order(symbol = trade_pair, side = 'BUY', type = 'LIMIT', price = limit_position_vol_price2, positionSide = 'SHORT', quantity = int(limit_average_position_summ), timeInForce='GTC')
        time.sleep(0.5)
        # tp_ limit_order3
        info_order_limit_tp3 = client.futures_create_order(symbol = trade_pair, side = 'BUY', type = 'LIMIT', price = limit_position_vol_price3, positionSide = 'SHORT', quantity = int(limit_average_position_summ), timeInForce='GTC')
        time.sleep(0.5)
        # tp_ limit_order4
        info_order_limit_tp4 = client.futures_create_order(symbol = trade_pair, side = 'BUY', type = 'LIMIT', price = limit_position_vol_price4, positionSide = 'SHORT', quantity = int(limit_average_position_summ), timeInForce='GTC')
        time.sleep(0.5)
        # TAKE_PROFIT
        info_order_tp = client.futures_create_order(symbol=trade_pair, side = 'BUY', type = 'TAKE_PROFIT_MARKET', positionSide='SHORT', stopPrice = side_tp, closePosition = 'true', timeInForce='GTC')
        time.sleep(0.5)
        print()
        print(f"Binance time: {str(datetime_from_millis(info_order_half['updateTime']))[0:19]} {info_order_half['symbol']} {info_order_half['positionSide']} orderId:{info_order_half['orderId']} price:{info_order_half['price']} size:{info_order_half['origQty']} {info_order_half['type']} {info_order_half['side']}")
        print(f"Binance time: {str(datetime_from_millis(info_order_limit_tp['updateTime']))[0:19]} {info_order_limit_tp['symbol']} {info_order_limit_tp['positionSide']} orderId:{info_order_limit_tp['orderId']} price:{info_order_limit_tp['price']} size:{info_order_limit_tp['origQty']} {info_order_limit_tp['type']} {info_order_limit_tp['side']}")
        print(f"Binance time: {str(datetime_from_millis(info_order_limit_tp2['updateTime']))[0:19]} {info_order_limit_tp2['symbol']} {info_order_limit_tp2['positionSide']} orderId:{info_order_limit_tp2['orderId']} price:{info_order_limit_tp2['price']} size:{info_order_limit_tp2['origQty']} {info_order_limit_tp2['type']} {info_order_limit_tp2['side']}")
        print(f"Binance time: {str(datetime_from_millis(info_order_limit_tp3['updateTime']))[0:19]} {info_order_limit_tp3['symbol']} {info_order_limit_tp3['positionSide']} orderId:{info_order_limit_tp3['orderId']} price:{info_order_limit_tp3['price']} size:{info_order_limit_tp3['origQty']} {info_order_limit_tp3['type']} {info_order_limit_tp3['side']}")
        print(f"Binance time: {str(datetime_from_millis(info_order_limit_tp4['updateTime']))[0:19]} {info_order_limit_tp4['symbol']} {info_order_limit_tp4['positionSide']} orderId:{info_order_limit_tp4['orderId']} price:{info_order_limit_tp4['price']} size:{info_order_limit_tp4['origQty']} {info_order_limit_tp4['type']} {info_order_limit_tp4['side']}")
        print(f"Binance time: {str(datetime_from_millis(info_order_tp['updateTime']))[0:19]} {info_order_tp['symbol']} {info_order_tp['positionSide']} orderId:{info_order_tp['orderId']} price:{info_order_tp['price']} size:{info_order_tp['origQty']} {info_order_tp['type']} {info_order_tp['side']}")
        print()
        base_id_orders = client.futures_get_open_orders()
        time.sleep(0.5)
        volume_id_orders = len(base_id_orders)
        tmp_id_order = 0
        for i in range(volume_id_orders):
            if base_id_orders[i]['positionSide'] == 'SHORT':
                tmp_id_order += 1
        succes_place_volume_orders = tmp_id_order + 1
        print(bcolors.FAIL + trade_pair, 'System  time:', time.strftime('%Y-%m-%d %H:%M', time.localtime()), 'SHORT Success Place', succes_place_volume_orders, 'Orders. Await results....' + bcolors.ENDC)
        print()
        flag = True
        while flag == True:
            time.sleep(10)
            check_position_volume_for_zero = int(client.futures_position_information(symbol = trade_pair)[2]['positionAmt'])
            time.sleep(0.5)
            if check_position_volume_for_zero == 0:
                print(bcolors.FAIL + trade_pair, 'System  time:', time.strftime('%Y-%m-%d %H:%M', time.localtime()), 'SHORT Position balance 0!!! Close all open', trade_pair, 'oders...' + bcolors.ENDC)
                base_id_orders = client.futures_get_open_orders()
                time.sleep(0.5)
                volume_id_orders = len(base_id_orders)
                for i in range(volume_id_orders):
                    time.sleep(1)
                    tmp2_id_order = ''
                    if base_id_orders[i]['positionSide'] == 'SHORT':
                        tmp2_id_order = base_id_orders[i]['orderId']
                        client.futures_cancel_order(symbol = trade_pair, orderId = tmp2_id_order)
                        time.sleep(0.5)
                        print(f'Close order id:{tmp2_id_order}')
                average_order_short1, average_order_short2 = 0, 0
                break
            average_short(info_order_limit1, info_order_limit2, limit_position_vol_price, limit_position_vol_price2, limit_position_vol_price3, limit_position_vol_price4)
        print()
        if telegram_notification == True:
            balance_tg = f'Balance {int(check_hold_balance())} USDT'
            tg_send_m(api_tg, chat_it_tg, balance_tg)
        print(balance_tg)
        print(f'Symbol trade: {trade_pair}')
        print('Check results in exchange,  GOOD LUCK!!')
        print()
        print()
        print(f'\n         --future_trade_bot--')
        print(bcolors.WARNING + f'         candlestick_symphony')
        print(f'         -Let the Game Begin-\n         -------- + ---------')
        print()
        print(f'         ----If Your Like:---')
        print(bcolors.WARNING + f'-Donate for the development of the bot-' + bcolors.ENDC)
        print(f'         And wait for Update...\n-------------USDT TRC20----------------\n--THNh5f5MBBVpP7MvzCZdSeNCMzzadG6Ld4---\n' + bcolors.ENDC)
    except Exception:
        print(bcolors.FAIL + f"ERROR!!!! 'place_doji_short'" + bcolors.ENDC)
        res_long = float(client.futures_position_information(symbol = trade_pair)[1]['positionAmt'])
        time.sleep(0.5)
        res_short = float(client.futures_position_information(symbol = trade_pair)[2]['positionAmt'])
        if res_long > 0.0:
            time.sleep(0.5)
            client.futures_create_order(symbol=trade_pair, side='SELL', type='MARKET', positionSide='LONG', quantity=int(res_long))
            res_long = float(0)
        if res_short < 0.0:
            time.sleep(0.5)
            tmp_short_b = str(client.futures_position_information(symbol = trade_pair)[2]['positionAmt'])[1:]
            res_short = float(tmp_short_b)
            client.futures_create_order(symbol=trade_pair, side='BUY', type='MARKET', positionSide='SHORT', quantity=int(res_short))
            res_short = float(0)
        if res_long == 0.0 and res_short == 0.0:
            time.sleep(0.5)
            client.futures_cancel_all_open_orders(symbol = trade_pair)
        if telegram_notification == True:
            tg_send_m(api_tg, chat_it_tg, 'ERROR!!!! place_doji_short')
        raise

def average_long(info_order_limit1, info_order_limit2, limit_position_vol_price, limit_position_vol_price2, limit_position_vol_price3, limit_position_vol_price4):
    try:
        global average_order_long1
        global average_order_long2
        time.sleep(1)
        order_id = info_order_limit1['orderId']
        if average_order_long1 == 0 and client.futures_get_order(symbol = trade_pair, orderId = order_id)['status'] == 'FILLED':
            time.sleep(0.5)
            average_order_long1 += 1
            print(f'LONG average order {order_id} FILLED')
            order_origQty = int(info_order_limit1['origQty'])
            order_limitQty = order_origQty / 2
            info_order_average1 = client.futures_create_order(symbol = trade_pair, side = 'SELL', type = 'LIMIT', price = limit_position_vol_price2, positionSide = 'LONG', quantity = int(order_limitQty), timeInForce='GTC')
            time.sleep(0.5)
            info_order_average1_2 = client.futures_create_order(symbol = trade_pair, side = 'SELL', type = 'LIMIT', price = limit_position_vol_price3, positionSide = 'LONG', quantity = int(order_limitQty), timeInForce='GTC')
            time.sleep(0.5)
            print(f"Binance time: {str(datetime_from_millis(info_order_average1['updateTime']))[0:19]} {info_order_average1['symbol']} {info_order_average1['positionSide']} orderId:{info_order_average1['orderId']} price:{info_order_average1['price']} size:{info_order_average1['origQty']} {info_order_average1['type']} {info_order_average1['side']}")
            print(f"Binance time: {str(datetime_from_millis(info_order_average1_2['updateTime']))[0:19]} {info_order_average1_2['symbol']} {info_order_average1_2['positionSide']} orderId:{info_order_average1_2['orderId']} price:{info_order_average1_2['price']} size:{info_order_average1_2['origQty']} {info_order_average1_2['type']} {info_order_average1_2['side']}")
        time.sleep(1)
        order_id = info_order_limit2['orderId']
        if average_order_long2 == 0 and client.futures_get_order(symbol = trade_pair, orderId = order_id)['status'] == 'FILLED':
            time.sleep(0.5)
            average_order_long2 += 1
            print(f'LONG average order {order_id} FILLED')
            order_origQty = int(info_order_limit2['origQty'])
            order_limitQty = order_origQty / 2
            info_order_average1 = client.futures_create_order(symbol = trade_pair, side = 'SELL', type = 'LIMIT', price = limit_position_vol_price, positionSide = 'LONG', quantity = int(order_limitQty), timeInForce='GTC')
            time.sleep(0.5)
            info_order_average1_2 = client.futures_create_order(symbol = trade_pair, side = 'SELL', type = 'LIMIT', price = limit_position_vol_price4, positionSide = 'LONG', quantity = int(order_limitQty), timeInForce='GTC')
            time.sleep(0.5)
            print(f"Binance time: {str(datetime_from_millis(info_order_average1['updateTime']))[0:19]} {info_order_average1['symbol']} {info_order_average1['positionSide']} orderId:{info_order_average1['orderId']} price:{info_order_average1['price']} size:{info_order_average1['origQty']} {info_order_average1['type']} {info_order_average1['side']}")
            print(f"Binance time: {str(datetime_from_millis(info_order_average1_2['updateTime']))[0:19]} {info_order_average1_2['symbol']} {info_order_average1_2['positionSide']} orderId:{info_order_average1_2['orderId']} price:{info_order_average1_2['price']} size:{info_order_average1_2['origQty']} {info_order_average1_2['type']} {info_order_average1_2['side']}")
    except Exception:
        print(bcolors.FAIL + f'ERROR!!!! average_long' + bcolors.ENDC)
        res_long = float(client.futures_position_information(symbol = trade_pair)[1]['positionAmt'])
        time.sleep(0.5)
        res_short = float(client.futures_position_information(symbol = trade_pair)[2]['positionAmt'])
        if res_long > 0.0:
            time.sleep(0.5)
            client.futures_create_order(symbol=trade_pair, side='SELL', type='MARKET', positionSide='LONG', quantity=int(res_long))
            res_long = float(0)
        if res_short < 0.0:
            time.sleep(0.5)
            tmp_short_b = str(client.futures_position_information(symbol = trade_pair)[2]['positionAmt'])[1:]
            res_short = float(tmp_short_b)
            client.futures_create_order(symbol=trade_pair, side='BUY', type='MARKET', positionSide='SHORT', quantity=int(res_short))
            res_short = float(0)
        if res_long == 0.0 and res_short == 0.0:
            time.sleep(0.5)
            client.futures_cancel_all_open_orders(symbol = trade_pair)
        if telegram_notification == True:
            tg_send_m(api_tg, chat_it_tg, 'ERROR!!!! average_long')
        raise

def average_short(info_order_limit1, info_order_limit2, limit_position_vol_price, limit_position_vol_price2, limit_position_vol_price3, limit_position_vol_price4):
    try:
        global average_order_short1
        global average_order_short2
        time.sleep(1)
        order_id = info_order_limit1['orderId']
        if average_order_short1 == 0 and client.futures_get_order(symbol = trade_pair, orderId = order_id)['status'] == 'FILLED':
            time.sleep(0.5)
            average_order_short1 += 1
            print(f'SHORT average order {order_id} FILLED')
            order_origQty = int(info_order_limit1['origQty'])
            order_limitQty = order_origQty / 2
            info_order_average1 = client.futures_create_order(symbol = trade_pair, side = 'BUY', type = 'LIMIT', price = limit_position_vol_price2, positionSide = 'SHORT', quantity = int(order_limitQty), timeInForce='GTC')
            time.sleep(0.5)
            info_order_average1_2 = client.futures_create_order(symbol = trade_pair, side = 'BUY', type = 'LIMIT', price = limit_position_vol_price3, positionSide = 'SHORT', quantity = int(order_limitQty), timeInForce='GTC')
            time.sleep(0.5)
            print(f"Binance time: {str(datetime_from_millis(info_order_average1['updateTime']))[0:19]} {info_order_average1['symbol']} {info_order_average1['positionSide']} orderId:{info_order_average1['orderId']} price:{info_order_average1['price']} size:{info_order_average1['origQty']} {info_order_average1['type']} {info_order_average1['side']}")
            print(f"Binance time: {str(datetime_from_millis(info_order_average1_2['updateTime']))[0:19]} {info_order_average1_2['symbol']} {info_order_average1_2['positionSide']} orderId:{info_order_average1_2['orderId']} price:{info_order_average1_2['price']} size:{info_order_average1_2['origQty']} {info_order_average1_2['type']} {info_order_average1_2['side']}")
        time.sleep(1)
        order_id = info_order_limit2['orderId']
        if average_order_short2 == 0 and client.futures_get_order(symbol = trade_pair, orderId = order_id)['status'] == 'FILLED':
            time.sleep(0.5)
            average_order_short2 += 1
            print(f'SHORT average order {order_id} FILLED')
            order_origQty = int(info_order_limit2['origQty'])
            order_limitQty = order_origQty / 2
            info_order_average1 = client.futures_create_order(symbol = trade_pair, side = 'BUY', type = 'LIMIT', price = limit_position_vol_price, positionSide = 'SHORT', quantity = int(order_limitQty), timeInForce='GTC')
            time.sleep(0.5)
            info_order_average1_2 = client.futures_create_order(symbol = trade_pair, side = 'BUY', type = 'LIMIT', price = limit_position_vol_price4, positionSide = 'SHORT', quantity = int(order_limitQty), timeInForce='GTC')
            time.sleep(0.5)
            print(f"Binance time: {str(datetime_from_millis(info_order_average1['updateTime']))[0:19]} {info_order_average1['symbol']} {info_order_average1['positionSide']} orderId:{info_order_average1['orderId']} price:{info_order_average1['price']} size:{info_order_average1['origQty']} {info_order_average1['type']} {info_order_average1['side']}")
            print(f"Binance time: {str(datetime_from_millis(info_order_average1_2['updateTime']))[0:19]} {info_order_average1_2['symbol']} {info_order_average1_2['positionSide']} orderId:{info_order_average1_2['orderId']} price:{info_order_average1_2['price']} size:{info_order_average1_2['origQty']} {info_order_average1_2['type']} {info_order_average1_2['side']}")
    except Exception:
        print(bcolors.FAIL + f'ERROR!!!! average_short' + bcolors.ENDC)
        res_long = float(client.futures_position_information(symbol = trade_pair)[1]['positionAmt'])
        time.sleep(0.5)
        res_short = float(client.futures_position_information(symbol = trade_pair)[2]['positionAmt'])
        if res_long > 0.0:
            time.sleep(0.5)
            client.futures_create_order(symbol=trade_pair, side='SELL', type='MARKET', positionSide='LONG', quantity=int(res_long))
            res_long = float(0)
        if res_short < 0.0:
            time.sleep(0.5)
            tmp_short_b = str(client.futures_position_information(symbol = trade_pair)[2]['positionAmt'])[1:]
            res_short = float(tmp_short_b)
            client.futures_create_order(symbol=trade_pair, side='BUY', type='MARKET', positionSide='SHORT', quantity=int(res_short))
            res_short = float(0)
        if res_long == 0.0 and res_short == 0.0:
            time.sleep(0.5)
            client.futures_cancel_all_open_orders(symbol = trade_pair)
        if telegram_notification == True:
            tg_send_m(api_tg, chat_it_tg, 'ERROR!!!! average_short')
        raise

def main_trade():
    global count_main
    flag_main = True
    while flag_main == True:
        time.sleep(10)
        if count_main == 0:
            if flag_long == False and flag_short == False:
                Thread(target = search_doji).start()
                count_main += 1
            if flag_long == True and flag_short == False:
                Thread(target = search_doji).start()
                count_main += 1
            if flag_long == False and flag_short == True:
                Thread(target = search_doji).start()
                count_main += 1
            if flag_long == True and flag_short == True:
                continue

main_trade()
