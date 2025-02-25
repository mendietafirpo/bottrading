from connection import get_data_range
import pandas as pd
from sqlalchemy import create_engine, text
import pymysql
from datetime import datetime
import time

symbol = 'BTCUSDT'
interval = 5
start_time = int(datetime(2024, 1, 27).timestamp() * 1000)
end_time = int(datetime(2024, 1, 30).timestamp() * 1000)
limit = 1000

# try:
#     connection = pymysql.connect(
#         host='localhost',  # O usa '127.0.0.1'
#         user='root',
#         password='030704',
#         database='tradebots',
#         port=3306
#     )
#     print("Conexión exitosa")
# except pymysql.MySQLError as e:
#     print(f"Error en la conexión: {e}")

DATABASE_URL = "mysql+pymysql://user:password@localhost/tradebots"

# # Crear la conexión con SQLAlchemy

# Define la conexión a la base de datos (ajusta según tu configuración)
engine = create_engine(DATABASE_URL)

# Establecer conexión
with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM market_data LIMIT 5"))
    
    # Obtener los resultados
    for row in result:
        print(row)


data = get_data_range(symbol, interval, start_time, end_time, limit)
#  Renombrar la columna Interval (si existe) para evitar problemas
if "Interval" in data.columns:
     data.rename(columns={"Interval": "interval_"}, inplace=True)
if 'symbol' not in data.columns:
    data['symbol'] = symbol

data = data.drop(columns=['Turnover'])
# # Guardar los datos en MariaDB
data.to_sql("market_data", con=engine, if_exists="append", index=False)