import pandas as pd
import numpy as np
import warnings 
warnings.filterwarnings('ignore')
import time

from strategy_ema_macd import get_patterns
from indicators import(
    get_atr, 
    get_macd_ema,
)
from manager import(
    load_reg,
    save_reg,
    close_unreal_position
)
import datetime
from connection import get_data
#from data_source import get_data_tiingo as get_data

def entry_point(k, symbol, interval, ema_fast, ema_slow, multi_atr):
    try:
        
        # pattern
        print(f"\n call patterns {k}, {symbol}, {interval}, {multi_atr})")
        
        patternLoad = get_patterns(k, symbol, interval, ema_fast, ema_slow, multi_atr)
        
        pattern = patternLoad[0]
        listPattern = patternLoad[1]


        entryPoint = {}
        

        n = len(listPattern)
        if n > 0:
            for i in range(0, n):
                pattern_ = listPattern[i]
                side_ = pattern.get(pattern_ + '_side')
                if pattern.get(listPattern[i]) == 1:
                    entryPoint.update({
                            'pattern': pattern_,
                            'side':  side_,
                            'plimit': pattern.get(pattern_ + '_plimit'),
                            'lprice': pattern.get(pattern_ + '_lprice'),
                            'sloss': pattern.get(pattern_ + '_sloss'),
                            'tprofit': pattern.get(pattern_ + '_tprofit'),
                            'timenow': pattern.get(pattern_ + '_timenow'),
                            'timeformat': pattern.get(pattern_ + '_timeformat'),
                            'method': pattern.get(pattern_ + '_method')
                        })
                print(f" {symbol} => {listPattern[i]}: {pattern.get(listPattern[i])}")
                if pattern.get(listPattern[i]) == 1:
                    plimit =  pattern.get(pattern_ + '_plimit')
                    sloss =  pattern.get(pattern_ + '_sloss')
                    tprofit = pattern.get(pattern_ + '_tprofit')
                    time_ = pattern.get('timenow')
                    time_f = pattern.get('timeformat')
                    method_ = pattern.get(pattern_ + '_method')

                    # send data
                    entryPoint.update({
                        'side': side_,
                        'pattern': pattern_,
                        'sloss': sloss,
                        'tprofit': tprofit,
                        'timenow': time_,
                        'timeformat': time_f,
                        'method': method_
                    })
                                
                    print(f"{time_f} {symbol} send order {side_} => {pattern_} plimit:{plimit} => sl:{sloss} => tp:{tprofit}")
                    return entryPoint
                else: pass
  
        #print(f" {symbol} no opportunity found")
        entryPoint = {}
        return entryPoint

    except Exception as err:
         print(f"exception into algorithmic: {err}")



# function for Stop Loss and dinamic Take Profit based on ATR
def get_sl_tp(k, symbol, interval, side, leverage, multi_atr, wallet_avai, pentry, qty):

    try:
        
            #createdTime = int(get_position_myVar_current(symbol, settleCoin='USDT', myVar='updatedTime'))
            #data_l = get_data(symbol, interval_l, limit=1000)
            data_s = get_data(symbol, interval, limit=1000)
            data_s['atr'] = get_atr(data_s, period=14).rolling(window=48).mean()
            atr_s = data_s['atr']
            atr_s = atr_s.iloc[k]
            
            # variables dataframe
            open = data_s['Open']
            close = data_s['Close']
            high = data_s['High']
            low = data_s['Low']
            now= data_s['Time'].iloc[k]
            close_ = close.iloc[k]
            high_ = high.iloc[k]
            low_ = low.iloc[k]
            close_1 = close.iloc[k-1]
            open_1 = open.iloc[k-1]
            # fibonacci indices
            fib_tolerances = [0.236, 0.382, 0.441, 0.50, 0.618, 0.618, 0.618, 0.702, 0.702, 0.786, 0.786, 0.84, 0.893, 1]
            # multiplier atr for tp and sl calc
            atr_multipliers = [2.3, 2.4, 2.5, 2.6, 2.5, 2.4, 2.3, 2.2, 2.1, 2, 1.9, 1.8, 1.7, 1.6, 1.5, 1.4, 1.3, 1.2, 1, 0.9, 0.8]
            atr_multipliers_sl = [2.3, 2.4, 2.5, 2.6, 2.5, 2.4, 2.3, 2.2, 2.1, 2, 1.9, 1.8, 1.7, 1.6, 1.5, 1.4, 1.3, 1.2, 1, 0.9, 0.8]
            atr_leverage = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1.9, 1.8, 1.7, 1.6, 1.5, 1.4, 1.3, 1.2, 1.1, 1]
            leverage = int(leverage)
            if 10 <= leverage <= 20:
                atr_multi_lev = atr_leverage[leverage]
            else:
                atr_multi_lev = 0.8


            if load_reg('backtesting.json').get('sloss_' + symbol) != None:
                last_stop = load_reg('backtesting.json').get('sloss_' + symbol)
            else: last_stop = 0
            # level price
            if load_reg('backtesting.json').get('lprice_' + symbol) != None:
                level_price = load_reg('backtesting.json').get('lprice_' + symbol)
            else: level_price = 0

            
            if load_reg('backtesting.json').get('time_order_' + symbol) != None:
                time_start = load_reg('backtesting.json').get('time_order_' + symbol)
            else: time_start = 0
            
            # if time start then the variable loading begins
            if time_start > 0 and level_price > 0:
                # time current

                time_ = data_s['Time'].shift(1).astype('int64') // 10**9
                time_current = time_.iloc[k]

                print(f"time start: {time_start} k: {k}")
                max_price, min_price, turn = 0, 0, 0
                if side == 'Buy':
                    if load_reg('backtesting.json').get('price_max_' + symbol) != None:
                        max_price = load_reg('backtesting.json').get('price_max_' + symbol)
                    # save new max price
                    if max_price == 0:
                        if close_1 > open_1 and close_1 > level_price:
                            max_price = close_1
                            save_reg('backtesting.json', 'price_max_' + symbol, max_price)
                            
                    else:
                        if (close_1 - max_price) > atr_s:
                            save_reg('backtesting.json', 'price_max_' + symbol, close_1)
                            max_price = close_1
                    # determination of turn
                    if level_price > 0 and max_price > 0:
                        turn_ = (max_price - level_price) // (atr_s * multi_atr * atr_multi_lev)
                        turn = int(turn_) if turn_ > 0 else turn
                elif side == "Sell":
                    if load_reg('backtesting.json').get('price_min_' + symbol) != None:
                        min_price = load_reg('backtesting.json').get('price_min_' + symbol)
                    # save new min price
                    if min_price == 0:
                        if close_1 < open_1 and close_1 < level_price:
                            min_price = close_1
                            save_reg('backtesting.json', 'price_min_' + symbol, min_price)
                    else:
                        if (min_price - close_1) > atr_s:
                            save_reg('backtesting.json', 'price_min_' + symbol, close_1)
                            min_price = close_1
                    #determination of turn
                    if level_price > 0 and min_price > 0:
                        turn_ = (level_price - min_price) // (atr_s * multi_atr * atr_multi_lev)
                        turn = int(turn_) if turn_ > 0 else turn


                time_spent = int(time_current) - int(time_start)
                # if turn then loop stars

                if turn > 0:
                    n = len(atr_multipliers)
                    block = min(turn, n)
                    atrx =  atr_multipliers[block - 1]
                    atrx_sl= atr_multipliers_sl[block - 1]
   
                    sendChangeSl = False
                    if side == 'Buy':
                        new_sloss = close_1 - atr_s * atrx_sl * atr_multi_lev * multi_atr
                        new_tprofit = close_1 + atr_s * atrx * atr_multi_lev * multi_atr
                        if new_sloss > 1.001 * last_stop:
                            sendChangeSl = True
                            print(f"\n {now} long -> turn: {turn} sl: {new_sloss}, tp: {new_tprofit} close_1: {close_1} calc:{atr_s * atrx_sl * atr_multi_lev * multi_atr} atr: {atr_s} atrx: {atrx} atr_lev: {atr_multi_lev} multi_atr: {multi_atr} lev: {leverage}")

                    elif side == 'Sell':
                        new_sloss = close_1 + atr_s * atrx_sl * atr_multi_lev * multi_atr
                        new_tprofit = close_1 - atr_s * atrx * atr_multi_lev * multi_atr

                        if new_sloss < 0.999 * last_stop:
                            print(f"\n {now} short -> turn: {turn} sl: {new_sloss}, tp: {new_tprofit} close_1: {close_1} calc:{atr_s * atrx_sl * atr_multi_lev * multi_atr} atr: {atr_s} atrx: {atrx} atr_lev: {atr_multi_lev} multi_atr: {multi_atr} lev: {leverage}")
                            sendChangeSl = True
                    # first post 
                    if sendChangeSl == True:
                        save_reg('backtesting.json', 'sloss_' + symbol, new_sloss)
                        save_reg('backtesting.json', 'tprofit_' + symbol, new_tprofit)
                        save_reg('trade_report.json', 'changed_sl_tp:' + str(side) + ' ' + str(k) + ')' + symbol + '_' + str(now) + 'sloss:' + str(new_sloss) + 'tprofit:' + str(new_tprofit), 'high:' + str(high_) + 'low:' + str(low_))
                        return print(f"{now} {symbol} sent sl, tp => {side}, {time_spent/60} min ({int(time.time())} - {time_start} = {time_spent})")

                    # updated sl and tp when right price differential
                    if level_price != 0 and turn > 3:
                        sendFibClose = False
                        n = len(fib_tolerances)
                        block = min(turn, n)
                        tolerance = fib_tolerances[block - 1]
                        if max_price > 0 and side == 'Buy':
                            # closing order if price break level Finobacci
                            last_low = low_
                            price_fb = level_price + (max_price - level_price) * tolerance
                            if last_low <= price_fb:
                                pout = price_fb
                                xpl = (pout - pentry) * qty * (1 - 0.00075) # loss
                                sendFibClose = True
                        elif min_price > 0 and side == 'Sell':
                            last_high = high_
                            price_fb = level_price - (level_price - min_price) * tolerance
                            if last_high >= price_fb:
                                pout = price_fb
                                xpl = (pentry - pout) * qty * (1 + 0.00075) # loss
                                sendFibClose = True
                            pass
                        # second post
                        if sendFibClose == True:
                            print(f"\n k:{k} {now} =>({turn}) {symbol} tolerance: {tolerance} send close {side} fib  => new sl: {new_sloss} new tp: {new_tprofit} high: {high_} low: {low_} price start:{level_price} price max: {max_price} price min: {min_price} price current: {close_}")
                            cause = 'fib_tolerance: ' + str(tolerance)
                            new_wallet_avai = wallet_avai + qty * pentry / float(leverage) + xpl
                            save_reg('backtesting.json', 'wallet_avai', new_wallet_avai)
                            close_unreal_position(k, now, cause, symbol, side, qty, pentry, pout, high_, low_, new_wallet_avai, xpl, leverage)
                            sendFibClose == False
                            pass
                    print(f"{now} k: {k} {symbol} ({turn}) => time spent:{time_spent}")

                    return
                return
            return
    except Exception as err: 
        print(f"Error en get_sl_tp: {err}")
