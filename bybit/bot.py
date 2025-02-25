from algorithmic import (
    entry_point,
    get_sl_tp

    )
from manager import (
    conteiner_manager,
    save_reg, 
    load_reg,
    del_reg,
    open_unreal_order,
    close_unreal_order,
    open_unreal_position,
    close_unreal_position

)
from connection import get_data
#from data_source import get_data_tiingo as get_data


import numpy as np
import time
import datetime
from multiprocessing import Process



def run_bot(symbol, interval, leverage, multi_atr, ema_fast, ema_slow):
        try:
           
            resul = conteiner_manager(symbol)
            price_precision = resul.get('price_precision')
            qty_precision = resul.get('qty_precision')

            del_reg('backtesting.json')
            del_reg('trade_report.json')
            del_reg('report.json')

            in_position = False
            status = 'close'
            save_reg('backtesting.json', 'in_position_' + symbol, False)
            wallet_avai = 2500
            save_reg('backtesting.json', 'wallet_avai', wallet_avai)
            save_reg('backtesting.json', 'real_wallet', wallet_avai)
            data = get_data(symbol, interval, limit=1000)

            is_k = 101
            k = is_k
            for k in range(is_k, 1000):
                    try:
                        # checking exits position
                        if load_reg('backtesting.json').get('is_k' + symbol) != None:
                            is_k = load_reg('backtesting.json').get('in_k_' + symbol)
                        if load_reg('backtesting.json').get('in_position_' + symbol) != None:
                            in_position = load_reg('backtesting.json').get('in_position_' + symbol)
                        if load_reg('backtesting.json').get('real_wallet') != None:
                            wallet = load_reg('backtesting.json').get('real_wallet')
                        if load_reg('backtesting.json').get('wallet_avai') != None:
                            wallet_avai = load_reg('backtesting.json').get('wallet_avai')
                        #wallet available
                    
                        # logic opens, closes orders and change takes profit and stop loss

                        if load_reg('backtesting.json').get('status_' + symbol) != None:
                            status = load_reg('backtesting.json').get('status_' + symbol)
                        else:
                            status = 'close'

                        if in_position == False:
                                high_ = data['High'].iloc[k]
                                #print(f"call entrypoint {k}, {symbol}, high: {high_} interval_s={temp_short}, interval_l={temp_long}, multi_atr={multi_atr}")
                                entryPoint = entry_point(k, symbol, interval, ema_fast, ema_slow, multi_atr)
  
                                if len(entryPoint) > 0 and status == 'close' and k > is_k:
                                    #news orders                              
                                    pentry = round(entryPoint.get('plimit'), price_precision) # get_ticker_info(symbol)['list'][0]['markPrice']
                                    side = entryPoint.get('side')
                                    time_order = entryPoint.get('timenow')

                                    #orderType = 'Limit'
                                    # send unreal order
                                    if wallet_avai > 0:
                                        timeformat = entryPoint.get('timeformat')
                                        qty = round((wallet_avai * 0.5) / float(pentry) * float(leverage), qty_precision)                          
                                        sloss = round(entryPoint.get('sloss'), price_precision)
                                        tprofit = round(entryPoint.get('tprofit'), price_precision)
                                        lprice = round(entryPoint.get('lprice'), price_precision)
                                        method = entryPoint.get('method')
                                        save_reg('backtesting.json', 'time_order_' + symbol, int(time_order))
                                        save_reg('backtesting.json', 'is_k_' + symbol, k)
                                        print(f" call open unreal order {k}, {time_order}, {symbol}, {side}, {qty}, {pentry}, {sloss}, {tprofit}")
                                        new_wallet_avai = wallet_avai - round(qty * pentry / float(leverage), price_precision)
                                        save_reg('backtesting.json', 'wallet_avai', new_wallet_avai)
                                        open_unreal_order(k, timeformat, method, symbol, side, qty, pentry, sloss, tprofit, lprice)
                                        k += 3
                                        pass
                                else:
                                    k += 1
                                    pass 
                        elif in_position == True:
                                side_position = load_reg('backtesting.json').get('side_' + symbol)
                                wallet_avai = load_reg('backtesting.json').get('wallet_avai')
                                wallet = load_reg('backtesting.json').get('real_wallet')
                                pentry = load_reg('backtesting.json').get('pentry_' + symbol)
                                qty = load_reg('backtesting.json').get('qty_'+ symbol)
                                tprofit = round(load_reg('backtesting.json').get('tprofit_' + symbol), price_precision)
                                sloss = round(load_reg('backtesting.json').get('sloss_' + symbol), price_precision)
                                time_order = load_reg('backtesting.json').get('time_order_' + symbol)
                                high_ = data['High'].iloc[k]
                                low_ = data['Low'].iloc[k]
                                now_ = data['Time'].iloc[k]
                                time_ = data['Time'].shift(1).astype('int64') // 10**9
                                print(f"\n {now_} ({k}) elif: in_position? {in_position} status? {status} high {high_} low {low_} pentry {pentry}")
                                if status == 'open_order':
                                    sendPosition = False
                                    if side == 'Buy' and low_ <= pentry:
                                        sendPosition = True
                                    elif side == 'Sell' and high_ >= pentry:
                                        sendPosition = True

                                    if sendPosition == True:
                                        open_unreal_position(k, now_, symbol, side)
                                        k + 1
                                        pass
                                    else:
                                        time_current = time_.iloc[k]
                                        time_limit = 3000
                                        diff_time_order = int(time_current) - int(time_order)
                                        #print(time_current, time_order, diff_time_order)
                                        print(f"{k} order => {symbol}: countdown:{round((time_limit -diff_time_order)/60, 0)} min ")
                                        if diff_time_order > time_limit:
                                            #open unreal position
                                            new_wallet_avai = wallet_avai + round(qty * pentry / float(leverage), price_precision)
                                            save_reg('backtesting.json', 'wallet_avai', new_wallet_avai)
                                            close_unreal_order(k, now_, symbol, side)
                                            k += 1
                                            pass
                                        else:
                                            k += 1
                                            pass
                                # closing position for take profit or stop los
                                if status == 'open_position':
                                    xpl = 0
                                    if high_ >= tprofit and side_position == 'Buy':
                                        xpl = (tprofit - pentry) * qty * (1 - 0.00075) # profit
                                        pout = tprofit
                                        cause = 'break tp long'
                                    elif low_ <= sloss and side_position == 'Buy':
                                        xpl = (sloss - pentry) * qty * (1 + 0.00075) # loss
                                        pout = sloss
                                        cause = 'break sl long'
                                    elif low_ <= tprofit and side_position == 'Sell':
                                        xpl = (pentry - tprofit) * qty * (1 - 0.00075) #profit
                                        pout = tprofit
                                        cause = 'break tp short'
                                    elif high_ >= sloss and side_position == 'Sell':
                                        xpl = (pentry - sloss) * qty * (1 + 0.00075) # loss
                                        pout = sloss
                                        cause = 'break sl short'
                                    if xpl == 0:
                                        print(f"\n call get_sl_ => {k}, {now_}, {symbol}, {interval}, {side_position}, {leverage}, {wallet_avai}, {pentry}, {qty}")
                                        get_sl_tp(k, symbol, interval, side=side_position, leverage=leverage, multi_atr=multi_atr, wallet_avai=wallet_avai, pentry=pentry, qty=qty)
                                        k += 1
                                        pass                                        
                                    else: 
                                        k += 1
                                        pass
                                    if xpl != 0 and k > is_k + 1:
                                        print(f"\n call closing order => {k}, {now_}, {symbol}, {side}, {qty}, {pentry}, {pout}, {high_}, {low_}, {wallet_avai}, {xpl}, {leverage}")
                                        xpl = round(xpl, price_precision)
                                        new_wallet_avai = wallet_avai + round(qty * pentry / float(leverage) + xpl, price_precision)
                                        save_reg('backtesting.json', 'wallet_avai', new_wallet_avai)
                                        close_unreal_position(k, now_, cause, symbol, side, qty, pentry, pout, high_, low_, wallet, xpl, leverage)
                                        k += 3
                                        xpl = 0
                                        pass
                        else:
                            k += 1
                            pass


                    except Exception as e:
                        print(f"error inside main loop {e}")
        except KeyboardInterrupt:
            print("bot stopped manually")
        

# run_bot(symbol, temp_short, temp_long, wallet_perc, leverage)

if __name__ == "__main__":
    params = [
        {"symbol": "BTCUSDT", "interval": 60, "leverage": '20', "multi_atr": 2.2, "ema_fast": 10, "ema_slow":  50},
        {"symbol": "ETHUSDT", "interval": 60, "leverage": '20', "multi_atr": 2.2, "ema_fast": 10, "ema_slow": 50},
        #{"symbol": "WLDUSDT", "interval": 60, "leverage": '20', "multi_atr": 2.2, "ema_fast": 10, "ema_slow":  100},
        {"symbol": "SOLUSDT", "interval": 60, "leverage": '20', "multi_atr": 2.2, "ema_fast": 10, "ema_slow":  50},
        {"symbol": "BNBUSDT", "interval": 60, "leverage": '20', "multi_atr": 2.2, "ema_fast": 10, "ema_slow":  50},
        #{"symbol": "RENDERUSDT", "interval": 60, "leverage": '20', "multi_atr": 2.2, "ema_fast": 10, "ema_slow":  50},
        #{"symbol": "ARBUSDT", "interval": 60, "leverage": '20', "multi_atr": 2.2, "ema_fast": 10, "ema_slow":  50},
        #{"symbol": "LINKUSDT", "interval": 60, "leverage": '30', "multi_atr": 2.2, "ema_fast": 10, "ema_slow":  50},
        #{"symbol": "GRTUSDT", "interval": 5, "leverage": '20', "multi_atr": 2.2, "ema_fast": 10, "ema_slow":  100},
        {"symbol": "XRPUSDT", "interval": 60, "leverage": '20', "multi_atr": 2.2, "ema_fast": 10, "ema_slow":  50},
        #{"symbol": "ADAUSDT", "interval": 5, "leverage": '20', "multi_atr": 2.2, "ema_fast": 10, "ema_slow":  100},
        #{"symbol": "AVAXUSDT", "interval": 5, "leverage": '20', "multi_atr": 2.2, "ema_fast": 10, "ema_slow":  100},
        #{"symbol": "TRXUSDT", "interval": 5, "leverage": '20', "multi_atr":  1.85, "ema_fast": 10, "ema_slow":  100}
    ]

    processes = []

    for param in params:
        p = Process(target=run_bot, args=(param["symbol"], param["interval"], param["leverage"], param["multi_atr"], param["ema_fast"], param["ema_slow"]))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    print("alls bots finalized")
