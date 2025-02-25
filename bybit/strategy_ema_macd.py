from connection import get_data
#from data_source import get_data_tiingo as get_data
from manager import add_reg, load_reg, save_reg
from indicators import (
    get_atr,
    get_ema, 
    get_macd_ema,
    get_regression_lines,
    calculate_slope,
    )
import pandas as pd
import numpy as np

import warnings 
warnings.filterwarnings('ignore')
import time

import matplotlib.pyplot as plt


def get_patterns(k, symbol, interval, ema_fast, ema_slow, multi_atr):

    try: 
        # emas period
        ema_fast = ema_fast * 60 / interval
        ema_slow = ema_slow * 60 / interval

        # data period
        data_s = get_data(symbol, interval, limit=1000)
        getmacd = get_macd_ema(data_s, 26, 12, 9)
        data_s['macd'] = getmacd[0]
        data_s['signal'] = getmacd[1]
        data_s['atr'] = get_atr(data_s, period=14)
        data_s['ema_l'] = get_ema(data_s, span=ema_fast)
        data_s['ema_L'] = get_ema(data_s, span=ema_slow)

    
        time_ = data_s['Time'].shift(1).astype('int64') // 10**9
        time_ = time_.iloc[k-1]
        

        #conteiner for send data
        patterns = {}
        listPattern = []

        # ema L 100 - 240 min
        slope_ema_slow = data_s['ema_L'].iloc[k]/data_s['ema_L'].iloc[k-7]
        slope_ema_fast = data_s['ema_l'].iloc[k]/data_s['ema_l'].iloc[k-7]


        # indicators
        ema_l = data_s['ema_l']
        ema_L = data_s['ema_L']
        atr_s = data_s['atr']
        atr_ = atr_s.iloc[k-1]
        macd = data_s['macd']
        signal = data_s['signal']
        timenow = data_s['Time']
        close_ =  data_s['Close'].iloc[k]
        open_ =  data_s['Open'].iloc[k]
        high =  data_s['High']
        vol = data_s['Volume']
        vol_mean_slow = vol.rolling(window=48).mean()
        vol_mean_fast = vol.rolling(window=4).mean()

        pentry_ = close_

        # load main indicators
        sendOrder = {}

        # strategy 001: crosin ema L and ema l
        emaCrossLong, emaCrossShort, slopeLong = 0, 0, 0
        macdCrossLong, macdCrossShort, slopeShort = 0, 0, 0

        if ema_L.iloc[k-3] > ema_l.iloc[k-3] and ema_l.iloc[k] > ema_L.iloc[k]:
            emaCrossLong += 1
            print(f"\n {timenow.iloc[k]} {symbol} cross emas long =>  ema_L-3 {ema_L.iloc[k-3]} ema_l-3 {ema_l.iloc[k-3]} long ema_L {ema_L.iloc[k]} ema_l {ema_l.iloc[k]} ema_fast{ema_fast} ema_slow {ema_slow}")

        if ema_l.iloc[k-3] > ema_L.iloc[k-3] and ema_L.iloc[k] > ema_l.iloc[k]:
            emaCrossShort += 1
            print(f"\n {timenow.iloc[k]} {symbol} cross emas short  =>  ema_L-3 {ema_L.iloc[k-3]} ema_l-3 {ema_l.iloc[k-3]} long ema_L {ema_L.iloc[k]} ema_l {ema_l.iloc[k]} ema_fast{ema_fast} ema_slow {ema_slow}")
        
        # slope emas
        if slope_ema_fast > 1 and slope_ema_slow > 1:
            emaCrossLong += 1
            macdCrossLong += 1
            print(f"\n {timenow.iloc[k]} {symbol} slope ema 100 > 1 {slope_ema_slow:.10f} %")

        if slope_ema_fast < 1 and slope_ema_slow < 1:
            emaCrossShort += 1
            macdCrossShort += 1
            print(f"\n {timenow.iloc[k]} {symbol} slope ema 100 < 1 {slope_ema_slow:.10f} %")           
        
        # slope volume
        if vol_mean_fast.iloc[k] > 2.5 * vol_mean_slow.iloc[k]:
            print(f"\n {timenow.iloc[k]} {symbol} (vol-2+vol-3)x0.5 > vol_mean.iloc[-2] => {vol_mean_fast.iloc[k]} > {vol_mean_slow.iloc[k]}")
            emaCrossLong += 1
            macdCrossLong += 1


        # LONG
        #crossing macd signal and position zero:
        if signal[k-3] > macd[k-3] and macd[k] > signal[k] and macd[k-13] < 0:
            print(f"\n {timenow.iloc[k]} {symbol} -> LONG => high: {high.iloc[k]} ({k}) => \
            signal[k-3] > macd[k-3] {signal[k-3] > macd[k-3]} macd[k] > signal[k] {macd[k] > signal[k]} macd[k-13] < 0 {macd[k-13]}")
            macdCrossLong += 0
            slopeLong += 1
                
        # SHORT
        #crossing macd signal and position zero:
        if macd[k-3] > signal[k-3] and signal[k] > macd[k] and macd[k-13] > 0:
            print(f"\n {timenow.iloc[k]} {symbol} -> SHORT => high: {high.iloc[k]} ({k}) => \
                  macd[k-3] > signal[k-3] {macd[k-3] > signal[k-3]} signal[k] > macd[k] {signal[k] > macd[k]} macd[k-13] > 0 {macd[k-13]}")
            macdCrossShort += 1
            slopeShort += 1

        # print slopes macd
        if slopeLong == 1 or slopeShort ==1:
            print(f"\n {timenow.iloc[k]} {symbol} -> slope macd => high: {high.iloc[k]} ({k}) => \
            macd[k] {macd[k]} macd[k-3] {macd[k-3]} macd[k-5] { macd[k-5]} macd[k-7] {macd[k-7]} \
            macd[k-5]/signal[k-5] > 1.1 {macd[k-5]/signal[k-5] > 1.1} \
            signal[k]/macd[k] > 1 {signal[k]/macd[k] > 1} \
            macd[k-3]/macd[k] > 1.05 {macd[k-3]/macd[k] > 1.05} \
            macd[k]/macd[k-7] > 0.8 {macd[k-3]/macd[k-5] > 0.8} \
            macd[k-3]/macd[k-5] 0.9 {macd[k-3]/macd[k-12] > 0.9}")

        # slope macd
        if  macd[k-5]/signal[k-5] > 1.1 and \
            signal[k]/macd[k] > 1 and \
            macd[k-3]/macd[k] > 1.05 and \
            macd[k-3]/macd[k-5] > 0.8 and \
            macd[k-3]/macd[k-12] > 0.9:
            #print('SEND ORDER LONG')
            macdCrossLong += 0
            macdCrossShort += 0
                

        # crossing emas
        method, strat = '', ''
        if emaCrossLong == 3: # cross ema + slope ema + slope vol
            strat = 'long_macd'
            sendOrder = 'Long'
            method = 'crosin emas, long'
            pentry_ = close_
        if emaCrossShort == 2: # cross ema + slope ema
            strat = 'short_macd'
            sendOrder = 'Short'
            method = 'crosin emas, short'
            pentry_ = close_
        if macdCrossLong == 3 + 3:  # cross macd + slope macd + slope vol + slope emas
            strat = 'long_macd'
            sendOrder = 'Long'
            method = 'crosin macd, long'
            pentry_ = close_

        if macdCrossShort == 2 + 2: # cross macd + slope macd + slope emas
            strat = 'short_macd'
            sendOrder = 'Short'
            method = 'crosin macd, short'
            pentry_ = close_

        patterns.update({
            'timenow': time_,
            'timeformat': timenow.iloc[k],
            f"{strat}_plimit": pentry_,
            f"{strat}_lprice": close_,
            f"{strat}_method": method,
            f"{strat}": 1

        })

        if sendOrder == 'Long':
            patterns.update({
                f"{strat}_sloss": pentry_ - atr_ * multi_atr * 1.5,
                f"{strat}_tprofit": pentry_ + atr_ * multi_atr * 3,
                f"{strat}_side": 'Buy',
                f"{strat}": 1
            })
            listPattern.append('long_macd')
        elif sendOrder == 'Short':
            patterns.update({
                f"{strat}_sloss": pentry_ + atr_ * multi_atr * 1.5,
                f"{strat}_tprofit": pentry_ - atr_ * multi_atr * 3,
                f"{strat}_side": 'Sell',
                f"{strat}": 1
            })
            listPattern.append('short_macd')

        #print(f"patterns: {patterns}, listPattern: {listPattern}")
        if sendOrder == "Long" or sendOrder == "Short":
            print(f"{timenow.iloc[k]} {symbol} k:{k} {sendOrder} => send order: price limit: {close_}, sloss: {patterns.get(strat + '_sloss')}, tprofit: {patterns.get(strat +'_tprofit')}")
            return [patterns, listPattern]
        
        return [patterns, listPattern]
            
    except Exception as err:
        print(f"Error in get_patterns: {err}")

