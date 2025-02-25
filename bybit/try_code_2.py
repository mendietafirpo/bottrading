
from connection import get_data
from indicators import (
    get_atr,
    get_ema, 
    get_macd_ema,
    get_regression_lines,
    calculate_slope,
    )
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def get_mask(k, symbol, interval_s):
    try:
        masks = [
                {1:0.95, 2:0.85, 3:0.8, 4:0.9, 5:0.9, 6:0.9, 7:0.9, 8:0.93, 9:0.93, 10:0.95, 11:0, 12:0, 13:1.0, 14:0, 15:0}, # + macd signal
                {1:1.05, 2:1, 3:1.05, 4:1.15, 5:1.2, 6:1.2, 7:1.35, 8:1.4, 9:1.5, 10:2, 11:1, 12:0, 13:0, 14:0, 15:0 },
                {1:1.03, 2:1.02, 3:1.05, 4:1.15, 5:1.15, 6:1, 7:1, 8:1, 9:1.15, 10:1.2, 11:0, 12:0, 13:0, 14:0, 15:0 },
                {1:1.05, 2:1.02, 3:0.95, 4:1.15, 5:1.2, 6:1.3, 7:2, 8:3.3, 9:3.3, 10:0, 11:0, 12:0, 13:0, 14:0, 15:0 },
                #{1:1, 2:0.95, 3:0.95, 4:1, 5:1, 6:1.2, 7:0, 8:1.3, 9:1.3, 10:1.5, 11:0, 12:1.5, 13:0, 14:0, 15:0 },
                #{1:1, 2:1.035, 3:1.065, 4:1.025, 5:1.04, 6:1.04, 7:0, 8:1.2, 9:1.3, 10:2, 11:5, 12:0, 13:0, 14:0, 15:0 },
                #{1:1, 2:1.05, 3:0.98, 4:1, 5:1, 6:1, 7:1.4, 8:1.75, 9:2, 10:3, 11:7, 12:2, 13:0, 14:0, 15:0 },
                #{1:1, 2:0.95, 3:0.95, 4:0.95, 5:1, 6:1.1, 7:1.1, 8:1.1, 9:1.1, 10:1.1, 11:1.1, 12:1.1, 13:1.1, 14:2, 15:5 }
                ]
        
        data_s = get_data(symbol, interval_s, limit=1000)
        getmacd = get_macd_ema(data_s, 26, 12, 9)
        data_s['macd'] = getmacd[0]
        data_s['signal'] = getmacd[1]
        macd = data_s['macd']
        timenow = data_s['Time']
        high =  data_s['High']


        for mask_index, mask in enumerate(masks):
            count_m0, count_p0, count_mask = 0, 0, sum(1 for value in mask.values() if value != 0)
            for i in range(1, 16):
                macd_k_i, macd_k_i_1 = macd.iloc[k-i], macd.iloc[k-i-1]
                high_k_i, time_k_i = high.iloc[k-i], timenow.iloc[k-i]
                for direction in ['long', 'short']:
                    if direction == 'long':
                        strat = 'long_macd'
                        # macd minus zero: macd_m0, macd plus zero: macd_p0
                        if i == 1 and macd_k_i < 0 and macd_k_i_1 < 0 and macd_k_i_1 / macd_k_i > mask[i]:
                            count_m0 = 1
                            #print(f"LONG:{i} {time_k_i} (mask {mask_index}) ({count_m0}=={count_mask}) => high: {high_k_i}, macd[{k-i-1}]={macd_k_i_1:.2f}, macd[{k-i}]={macd_k_i:.3f}, ratio={macd_k_i_1/macd_k_i:.3f} > {mask[i]:.4f}")
                        if i > 1 and macd_k_i < 0 and masks[mask_index][i] != 0 and macd_k_i_1 < 0 and macd_k_i / macd_k_i_1:# > mask[i]:
                            count_m0 += 1
                            #print(f"LONG:{i} {time_k_i} (mask {mask_index}) ({count_m0}=={count_mask}) => high: {high_k_i}, macd[{k-i}]={macd_k_i:.2f}, macd[{k-i-1}]={macd_k_i_1:.3f}, ratio={macd_k_i/macd_k_i_1:.3f} > {mask[i]:.4f}")

                    if direction == 'short':
                        strat = 'short_macd'
                        if i == 1 and macd_k_i > 0 and macd_k_i_1 > 0 and macd_k_i_1 / macd_k_i > mask[i]:
                            count_p0
                        #    print(f"SHORT:{i} {time_k_i} (mask {mask_index}) ({count_p0}=={count_mask}) => high: {high_k_i}, macd[{k-i-1}]={macd_k_i_1:.2f}, macd[{k-i}]={macd_k_i:.3f}, ratio={macd_k_i_1/macd_k_i:.3f} > {mask[i]:.4f}")
                        if i > 1 and macd_k_i > 0 and masks[mask_index][i] != 0 and macd_k_i_1 > 0 and macd_k_i / macd_k_i_1 > mask[i]:
                            count_p0 += 1
                            #print(f"SHORT:{i} {time_k_i} (mask {mask_index}) ({count_p0}=={count_mask}) => high: {high_k_i}, macd[{k-i}]={macd_k_i:.2f}, macd[{k-i-1}]={macd_k_i_1:.3f}, ratio={macd_k_i/macd_k_i_1:.3f} > {mask[i]:.4f}")

    except Exception as e:
        print(e)

def trying():
    ## STRATEGIES DISIGNS
    symbol = 'BTCUSDT'
    interval_s = 5
    fastEma = 21
    slowEma = 180
    end = 1000
    start = 101
    plusEma = []
    minusEma = []
    k = 101
    for k in range(start, end, 10):
        data_s = get_data(symbol, interval_s, limit=1000)
        data_s['ema_L'] = get_ema(data_s, span=slowEma)
        data_s['ema_l'] = get_ema(data_s, span=fastEma)
        getmacd = get_macd_ema(data_s, 26, 12, 9)
        data_s['macd'] = getmacd[0]
        data_s['signal'] = getmacd[1]

        data_100 = data_s[k-100:k]
        data_100['ema_L_100'] = get_ema(data_100, span=slowEma)
        data_100['regre_ema_L_100'] = get_regression_lines(data_100, 'ema_L_100', 'ema_L_100' )

        data_50 = data_s[k-50:k]
        data_50['ema_L_50'] = get_ema(data_50, span=slowEma)
        data_50['regre_ema_L_50'] = get_regression_lines(data_50, 'ema_L_50', 'ema_L_50' )
        #slope_ema_L_50 = calculate_slope(data_50['regre_ema_L_50'])


        #slope_ema_L_50 = calculate_slope(data_50['regre_ema_L_50'])
        #slope_ema_L_100 = calculate_slope(data_100['regre_ema_L_100'])



        #angle_direct = np.degrees(np.arctan(slope))
        #print(f"Ángulo sin normalizar: {angle_direct:.2f} grados")

        #data_30 = data_s[k-30:k]
        #data_30['Volume'] = pd.to_numeric(data_30['Volume'], errors='coerce')
        #data_30.dropna(subset=['Volume'], inplace=True)
        #data_30['volumen_30'] = data_30['Volume']
        #data_30['vol_regre_30'] = get_regression_lines(data_30, 'volume_30','volumen_30')

        #print(data_s[540:600])

        plt.plot(data_50['regre_ema_L_50'])
        plt.plot(data_100['regre_ema_L_100'])
        plt.plot(data_s['ema_L'])
        plt.plot(data_s['ema_l'])
        #plt.plot(data_30['volumen_30'])
        #plt.plot(data_30['vol_regre_30'])
        #plt.plot(data_s['High'])
        #plt.plot(data_s['Low'])
        #plt.plot(data_s['macd'])
        #plt.plot(data_s['macd'])
        #plt.plot(data_s['signal'])
        plt.ylabel('line regression')
        plt.show()


# trying()
