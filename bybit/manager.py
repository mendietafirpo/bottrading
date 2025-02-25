import pandas as pd
import numpy as np
import json
from connection import get_session

def save_reg(file, name, value):
    try:

        with open(file, 'r') as file_:
            try:
                data = json.load(file_)
            except json.JSONDecodeError:
                print(f"file {file} is corrupt. Will be overwritten.")
                data = {} 
    except FileNotFoundError:
        print(f"file {file} not found {file}. a new file Will be created")
        data = {}

    data[name] = value

    try:
        with open(file, 'w') as file_:
            json.dump(data, file_, indent=4) 
    except Exception as e:
        print(f"Error salving {file}:", e)


def save_data(file, data):
    try:
        # Intentar leer el archivo existente
        try:
            with open(file, 'r') as file_:
                existing_data = json.load(file_)
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"El archivo {file} no existe o está corrupto. Se creará uno nuevo.")
            existing_data = {}

        # Combinar los datos existentes con los nuevos
        existing_data.update(data)

        # Guardar los datos en el archivo
        with open(file, 'w') as file_:
            json.dump(existing_data, file_, indent=4)

        print(f"Datos guardados correctamente en {file}.")

    except Exception as e:
        print(f"Error al guardar {file}: {e}")


def del_reg(file):
    try:

        with open(file, 'r') as file_:
            try:
                data = json.load(file_)
            except json.JSONDecodeError:
                print(f"file {file} is corrupt. Will be overwritten.")
                data = {} 
    except FileNotFoundError:
        print(f"file {file} not found {file}. a new file Will be created")
        data = {}

    data = {}

    try:
        with open(file, 'w') as file_:
            json.dump(data, file_, indent=4) 
    except Exception as e:
        print(f"Error salving {file}:", e)


#append new data in file json
def add_reg(file_path, key, value):

    try:
        # Leer el archivo JSON
        try:
            with open(file_path, 'r') as file_:
                data = json.load(file_)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}  # Si el archivo no existe o está vacío, inicializamos un diccionario

        # Verificar si la clave existe y es una lista
        if key in data:
            if isinstance(data[key], list):
                data[key].append(value)
            else:
                print(f"La clave '{key}' existe pero no es una lista.")
        else:
            # Crear una nueva lista con el valor si la clave no existe
            data[key] = [value]

        # Guardar los cambios en el archivo JSON
        with open(file_path, 'w') as file_:
            json.dump(data, file_, indent=4)

        print(f"Valor agregado correctamente a la clave '{key}'.")

    except Exception as e:
        print(f"Error al procesar el archivo {file_path}: {e}")


#load info json
def load_reg(file):
    try:
        with open(file, 'r') as file_:
            return json.load(file_)
    except FileNotFoundError:
        return {} 
    except json.JSONDecodeError as e:
        print(f"Error to reading {file}", e)
        return {}

session = get_session
def get_precisions(symbol):
    try:
        info = session.get_instruments_info(category='linear', symbol=symbol)['result']['list'][0]
        price_precision = len(info['priceFilter']['tickSize'].split('.')[1]) if '.' in info['priceFilter']['tickSize'] else 0
        qty_precision = len(info['lotSizeFilter']['qtyStep'].split('.')[1]) if '.' in info['lotSizeFilter']['qtyStep'] else 0
        return price_precision, qty_precision
    except Exception as e:
        print("Error getting precisions:", e)
        return None, None

def conteiner_manager(symbol):
        try:
            conteiner = {}

            val = get_precisions(symbol)
            conteiner['price_precision'] = val[0]
            conteiner['qty_precision'] = val[1]

            return conteiner

        except Exception as e:
            print(f"Error construct manager conteiner: {e}")


def open_unreal_order(k, timeformat, method, symbol, side, qty, pentry, sloss, tprofit, lprice):
    try:

        save_reg('backtesting.json', 'status_' + symbol, 'open_order')
        save_reg('backtesting.json', 'in_position_' + symbol, True)
        save_reg('backtesting.json', 'side_' + symbol, side)
        save_reg('backtesting.json', 'qty_' + symbol, qty)
        save_reg('backtesting.json', 'pentry_' + symbol, pentry)
        save_reg('backtesting.json', 'lprice_' + symbol, lprice)
        save_reg('backtesting.json', 'sloss_' + symbol, sloss)
        save_reg('backtesting.json', 'tprofit_' + symbol, tprofit)
        save_reg('trade_report.json', 'opening_order:' + str(k) + '_side:' + str(side) + '_symb:' + symbol + '_date:' + str(timeformat) + '_method:' + method, 'pentry: ' + str(pentry) + '; sloss: ' + str(sloss) + '; tprofit: ' + str(tprofit) + '; lprice: ' + str(lprice))
        print(f"opened ORDER => {symbol} k: {k} side: {side} date: {timeformat} qty:{qty} pentry: {pentry} sloss: {sloss} tprofit: {tprofit}") 
        return

    except Exception as e:
        print(e)

def open_unreal_position(k, now, symbol, side):
    try:
        save_reg('backtesting.json', 'status_' + symbol, 'open_position')
        save_reg('trade_report.json', 'opening_position:' + str(k) + '_side:' + str(side) + '_symb:' + symbol + '_date:' + str(now), 'order position opened')
        print(f"opened POSITION => {symbol} k: {k} side: {side} date: {now}")
        return

    except Exception as e:
        print(e)


def close_unreal_order(k, now_, symbol, side):
    try:
        save_reg('backtesting.json', 'status_' + symbol, 'close')
        save_reg('backtesting.json', 'in_position_' + symbol, False)
        save_reg('trade_report.json', 'closing_order:' + str(k) + '_side:' + str(side) + '_symb:' + symbol + '_date:' + str(now_), 'order is expired')
        return print(f"closed order=> {symbol} k: {k} side: {side} date: {now_}")

    except Exception as e:
        print (e)

def close_unreal_position(k, now_, cause, symbol, side, qty, pentry, pout, high_, low_, wallet,  xpl, leverage):
    try:
        wallet = load_reg('backtesting.json').get('real_wallet')
        new_wallet = wallet + float(xpl)
        save_reg('backtesting.json', 'status_' + symbol, 'close')
        save_reg('backtesting.json', 'in_position_' + symbol, False)
        save_reg('backtesting.json', 'price_min_' + symbol, 0)
        save_reg('backtesting.json', 'price_max_' + symbol, 0)
        save_reg('backtesting.json', 'lprice_' + symbol, 0)
        save_reg('backtesting.json', 'real_wallet', new_wallet)
        save_reg('trade_report.json', 'k:' + str(k) + ' _ ' + str(now_) + ' => ' + symbol + ' closing_cause: ' + cause + '_side: ' + str(side),  'pentry: ' + str(pentry) + '; pout: ' + str(pout) + '; high: ' + str(high_) + '; low: ' + str(low_))
        save_reg('report.json', 'k:' + str(k) + ' side: ' + str(side) + ' ( '+ str(leverage) + ') symb:' + symbol + ' date:' + str(now_), 'high: ' + str(high_) + '; pentry: ' + str(pentry) + '; qty: ' + str(qty) + '; pout ' + str(pout) + '; wallet: ' + str(new_wallet) + '; xlp: ' + str(xpl))
        return print(f"closed order => {symbol} k: {k} side: {side} date: {now_}")

    except Exception as e:
        print (e)


