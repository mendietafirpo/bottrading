## Backtesting for Bybit Trading Bot

This directory contains the implementation of a backtesting framework for a trading bot on the Bybit exchange. The backtesting framework allows you to simulate trading strategies using historical data to evaluate their performance before deploying them in a live trading environment.

### Files Overview

- **bot.py**: This is the main script for running the backtesting simulation. It includes the `run_bot` function, which simulates the trading strategy by opening and closing positions based on predefined conditions and indicators. The script uses multiprocessing to run multiple simulations in parallel.

- **algorithmic.py**: Contains the core trading algorithms, including the `entry_point` and `get_sl_tp` functions, which determine the entry points and stop-loss/take-profit levels for trades.

- **manager.py**: Manages the state of the trading bot, including functions for saving and loading the bot's state, opening and closing unreal orders and positions, and handling the wallet balance.

- **connection.py**: Handles data retrieval from the data source. It includes the `get_data` function, which fetches historical market data for the specified symbol and interval.

### How to Use

1. **Install Dependencies**:
   Ensure you have all the required Python packages installed. You can install them using pip:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure the Bot**:
   Update the parameters in the `params` list in bot.py to match your desired trading pairs, intervals, leverage, and other settings.

3. **Run the Backtesting**:
   Execute the bot.py script to start the backtesting simulation:
   ```bash
   python bot.py
   ```

4. **Review Results**:
   The results of the backtesting, including the performance of the trading strategy, will be saved in JSON files (`backtesting.json`, `trade_report.json`, `report.json`). Review these files to analyze the performance of your strategy.

### Example Parameters

Here is an example of the parameters used in the bot.py script:
```python
params = [
    {"symbol": "BTCUSDT", "interval": 60, "leverage": '20', "multi_atr": 2.2, "ema_fast": 10, "ema_slow":  50},
    {"symbol": "ETHUSDT", "interval": 60, "leverage": '20', "multi_atr": 2.2, "ema_fast": 10, "ema_slow": 50},
    {"symbol": "SOLUSDT", "interval": 60, "leverage": '20', "multi_atr": 2.2, "ema_fast": 10, "ema_slow":  50},
    {"symbol": "BNBUSDT", "interval": 60, "leverage": '20', "multi_atr": 2.2, "ema_fast": 10, "ema_slow":  50},
    {"symbol": "XRPUSDT", "interval": 60, "leverage": '20', "multi_atr": 2.2, "ema_fast": 10, "ema_slow":  50},
]
```

### Notes

- Ensure your system time is synchronized to avoid issues with timestamp mismatches.
- The backtesting framework uses historical data to simulate trades. Ensure you have access to accurate and comprehensive historical data for the best results.

---

Feel free to modify the summary as needed to better fit your project's specifics.
