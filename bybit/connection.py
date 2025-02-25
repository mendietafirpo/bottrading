# bybit_connection.py
import pandas as pd
import numpy as np
from datetime import datetime
import time
import warnings
warnings.filterwarnings('ignore')
from pybit.unified_trading import HTTP


def create_session(api_key, api_secret):
    return HTTP(api_key=api_key, api_secret=api_secret, recv_window=10000)
# Credenciales y configuración inicial

api = 'GFBuHdMDIyAQc8PesV'
secret = 'GiwsjINJt14Twmp3g8WxjklR6HqFTEbodUI9'

get_session = create_session(api, secret)


def get_klines(symbol, interval, limit):
    try:
        resp = get_session.get_kline(category='linear', symbol=symbol, interval=interval, limit=limit)['result']['list']
        resp = pd.DataFrame(resp, columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Turnover'])
        resp['Time'] = pd.to_datetime(resp['Time'], unit='ms')
        resp[['Open', 'High', 'Low', 'Close']] = resp[['Open', 'High', 'Low', 'Close']].apply(pd.to_numeric, errors='coerce')
        resp = resp.iloc[::-1].reset_index(drop=True)
        return resp
    except Exception as e:
        print("Error getting data:", e)
        return None


def get_data(symbol, interval, limit):
    try:
        resp = get_klines(symbol, interval, limit)
        return resp
    except Exception as e:
        print("Error getting kline data:", e)
        return None

def get_data_range(symbol, interval, start_time, end_time, limit):
    try:
        resp = get_session.get_kline(category='linear', symbol=symbol, interval=interval, start_time=start_time, end_time=end_time, limit=limit)['result']['list']
        resp = pd.DataFrame(resp, columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Turnover'])
        resp['Time'] = pd.to_datetime(resp['Time'], unit='ms')
        resp[['Open', 'High', 'Low', 'Close']] = resp[['Open', 'High', 'Low', 'Close']].apply(pd.to_numeric, errors='coerce')
        resp = resp.iloc[::-1].reset_index(drop=True)
        return resp
    except Exception as e:
        print("Error getting kline data:", e)
        return None


#symbol = 'BTCUSDT'
#interval = 5
#limit = 1000

#print(get_data(symbol, interval, limit))
#symbol = 'BTCUSDT'
# interval = 5
# start_time = int(datetime(2024, 1, 1).timestamp() * 1000)
# end_time = int(datetime(2024, 1, 5).timestamp() * 1000)
# limit = 1000
# print(start_time, end_time)
# print(get_data_range(symbol, interval, start_time, end_time, limit))

# Obtener el tiempo del servidor
# server_response = get_session.get_server_time()
# server_time = int(server_response['time'])  # Extraer el timestamp del JSON

# local_time = int(time.time() * 1000)  # Tiempo local en milisegundos

# print(f"Tiempo local: {local_time}")
# print(f"Tiempo del servidor: {server_time}")

# # Calcular diferencia
# time_difference = abs(local_time - server_time)
# print(f"Diferencia de tiempo: {time_difference} ms")

# if time_difference > 1000:
#     print("¡El tiempo está desincronizado! Considera actualizarlo en tu sistema.")