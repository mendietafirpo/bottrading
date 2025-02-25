from manager import add_reg, load_reg, save_reg, save_data
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


# Suponiendo que get_data es una función definida en otro lugar que devuelve un DataFrame



data = get_data('BTCUSDT', 60, limit=1000)[:-1]
data = data[-100:]
# Suponiendo que deseas ajustar el polinomio a la columna 'Close'
x = np.arange(len(data))
y = data['Close']  # Cambia 'Close' por la columna que desees ajustar
coeffs = np.polyfit(x, y, 1)
line = np.polyval(coeffs, x)

# Calcular las desviaciones estándar del residuo (diferencias entre la línea y los datos)
residuals = y - line
std_dev = np.std(residuals)

# Generar las líneas externas
upper_line = line + std_dev * 1.75
lower_line = line - std_dev * 1.75

# Agregar las líneas al DataFrame
data['line'] = line
data['upper_line'] = upper_line
data['lower_line'] = lower_line



dictionario = {}

dictionario['line'] = 'una linea'
dictionario['upper_line'] = 'una linea superior'
dictionario['lower_line'] = 'una linea inferior'
dictionario['residuals'] = 'residuos'

print(dictionario)

save_data('data.json', dictionario)


