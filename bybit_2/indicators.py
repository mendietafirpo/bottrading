import warnings 
import numpy as np
import pandas as pd


warnings.filterwarnings('ignore')

# Función Ichimoku con intervalo como parámetro
def ichimoku(data):
    try:
        high9 = data['High'].rolling(9).max()
        high26 = data['High'].rolling(26).max()
        low9 = data['Low'].rolling(9).min()
        low26 = data['Low'].rolling(26).min()
        high52 = data['High'].rolling(52).max()
        low52 = data['Low'].rolling(52).min()
        tenkan_sen = (high9 + low9) / 2
        kijun_sen = (high26 + low26) / 2
        senkou_A = ((tenkan_sen + kijun_sen) / 2).shift(26)
        senkou_B = ((high52 + low52) / 2).shift(26)
        return tenkan_sen, kijun_sen, senkou_A, senkou_B
    except Exception as err:
        print(err)


def get_rsi(data, period=14):
    try:
        delta = data['Close'].diff(1)
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        return data['RSI']
    except Exception as err:
        print(err)


def get_bollinger_bands(data, period, num_std_dev):
    try:
        middleband = data['Close'].rolling(window=period).mean()
        stddev = data['Close'].rolling(window=period).std()
        upperband = middleband + stddev * num_std_dev
        lowerband = middleband - stddev * num_std_dev
        return upperband, middleband, lowerband
    except Exception as err:
        print(err)


def get_macd_ema(data, slow, fast, signal):
    try:
        EMA_slow = data['Close'].ewm(span=slow, adjust=False).mean()
        EMA_fast = data['Close'].ewm(span=fast, adjust=False).mean()
        MACD_ema = EMA_fast - EMA_slow
        MACD_signal_ema = MACD_ema.ewm(span=signal, adjust=False).mean()
        return MACD_ema, MACD_signal_ema
    except Exception as err:
        print(err)


def get_macd_sma(data, slow, fast, signal):
    try:
        SMA_fast = data['Close'].rolling(window=fast).mean()
        SMA_slow = data['Close'].rolling(window=slow).mean()
        MACD_sma = SMA_fast - SMA_slow
        MACD_signal_sma = MACD_sma.rolling(window=signal).mean()
        return MACD_sma, MACD_signal_sma
    except Exception as err:
        print(err)


#def get_macd_ta(data, signal):
#    try:
#        macd_object = MACD(data['Close'])
#        macd_ta = macd_object.macd()
#        signal_ta = macd_ta.rolling(window=signal).mean()
#        return macd_ta, signal_ta
#    except Exception as err:
#        print(err)



def get_atr(data, period):
    try:
        high_low = data['High'] - data['Low']
        high_close = (data['High'] - data['Close'].shift()).abs()
        low_close = (data['Low'] - data['Close'].shift()).abs()
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        
        atr = true_range.rolling(window=period, min_periods=1).mean()
        return atr
    except Exception as err:
        print(err)


def get_ema(data, span):
    try:
        return data['Close'].ewm(span=span, adjust=False).mean()
    except Exception as err:
        print(err)

def get_sma(data, rolling):
    try:
        return data['Close'].rolling().mean()
    except Exception as err:
        print(err)

def get_regression_lines(data, line, param):
    x = np.arange(len(data))
    coeffs = np.polyfit(x, data[param], 1)
    line = np.polyval(coeffs, x)
    return line

def calculate_slope(series):
    x = np.arange(len(series))
    y = series.values
    # Normalizar los valores dividiendo por el precio inicial
    y_normalized = y / y[0]
    slope, intercept = np.polyfit(x, y_normalized, 1)
    return slope


def calculate_slope_abs(series):
    x = np.arange(len(series))
    y = series.values
    slope, intercept = np.polyfit(x, y, 1)
    return slope
    

