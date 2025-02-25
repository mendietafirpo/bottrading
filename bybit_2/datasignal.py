from connection import get_data
from indicators import (
    get_atr,
    get_ema, 
    get_macd_ema,
    get_regression_lines,
    calculate_slope,
    )
import numpy as np
import pandas as pd

def datasignal(symbol, interval, ema_fast, ema_slow):
    ema_fast = ema_fast * 60 // interval
    ema_slow = ema_slow * 60 // interval
    data = get_data(symbol, interval, limit=1000)
    getmacd = get_macd_ema(data, 26, 12, 9)
    data['macd'] = getmacd[0]
    data['signal'] = getmacd[1]
    data['ema_l'] = get_ema(data, span=ema_fast)
    data['ema_L'] = get_ema(data, span=ema_slow)
    ema_slow = data['ema_L']
    ema_fast = data['ema_l']
    macd = data['macd']
    signal = data['signal']
    data['Volume'] = pd.to_numeric(data['Volume'], errors='coerce')
    data.dropna(subset=['Volume'], inplace=True)
    volume = data['Volume']
    volume_mean = volume.rolling(window=14).mean()


    atr = get_atr(data, period=14)
    atr_mean = atr.rolling(window=12).mean()
    atr_mean = float(atr_mean.iloc[-2])

    # volume slope long
    data['volume_slope'] = np.where(
         (volume/ volume_mean) > 1.1,
         1, 0
    )

    # 🚀 LONG Crossover (EMA crosses up from negative)
    data['cross_ema_long'] = np.where(
        (ema_slow.shift(3) > ema_fast.shift(3)) & (ema_fast > ema_slow),
        1, 0
    )

    # 🔻 SHORT Crossover (EMA crosses down from positive)
    data['cross_ema_short'] = np.where(
        (ema_fast.shift(3) > ema_slow.shift(3)) & (ema_slow > ema_fast),
        1, 0
    )



    # 🚀 LONG Crossover (MACD crosses up from negative)
    data['cross_macd_long'] = np.where(
        (signal.shift(3) > macd.shift(3)) & (macd > signal) & (macd < 0)  & (macd.shift(5) < 0),
        1, 0
    )


    # 🔻 SHORT Crossover (MACD crosses down from positive)
    data['cross_macd_short'] = np.where(
        (macd.shift(3) > signal.shift(3)) & (signal > macd) & (macd > 0) & (macd.shift(5) > 0),
        1, 0
    )

    data['macd-3'] = macd.shift(3)

    # 🚀 Pending validation macd
    data['macd_slope'] = np.where(
        (macd.shift(5) / signal.shift(5) > 1.1) & 
         (signal / macd > 1) &
         (macd.shift(3) / macd > 1.05) &
         (macd / macd.shift(7) > 0.7) &
         (macd.shift(3) / macd.shift(5) > 0.9),
        1, 0
    )

    #data['macd-5-signal-5'] = macd.shift(-5) / signal.shift(-5)

    # 🚀 Pending validation emas
    data['ema_slope_long'] = np.where(
        (ema_slow.shift(2) / ema_slow.shift(7) > 1.1) &
        (ema_fast.shift(2) / ema_fast.shift(7) > 1.1),
        1, 0
    )

    data['ema_slope_short'] = np.where(
        (ema_slow.shift(2) / ema_slow.shift(7) < 0.9) &
        (ema_fast.shift(2) / ema_fast.shift(7) < 0.9),
        1, 0
    )
    
    datasignal = data
    return datasignal


    #signals = data.loc[
    #        (data['volume_slope'])#data['cross_macd_long'] == 1) & (data['slope_macd'] == 1)
    #     ]
    

    #print(signals[['Time', 'Close', 'macd', 'signal', 'cross_macd_long', 'cross_macd_short', 'macd_slope']])

data = datasignal('BTCUSDT', 15, 10, 50)[800:837]
filtered_data = data.loc[
     (data['cross_macd_long'] == 1)
]


#print(filtered_data[['Time', 'High', 'macd', 'signal', 'cross_macd_long', 'cross_macd_short', 'macd_slope']])
print(data[['Time', 'Close', 'macd', 'signal', 'cross_macd_long', 'macd-3', 'macd_slope']])


