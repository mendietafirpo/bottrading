
import pandas as pd
import yfinance as yf

symbol = 'TSLA'
start_date = '2023-02-15'
end_date = '2025-01-15'
stock = yf.Ticker(symbol)
daily_data = stock.history(start=start_date, end=end_date, interval='60m')

print(daily_data)