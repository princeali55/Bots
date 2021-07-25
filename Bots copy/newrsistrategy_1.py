# checkout the MainRSIbot (RSI bot) before using this
# this is the same as the RSI bot but i designed it to buy and sell multiple times
# i used the RSI strategy combined with a strategy that i made up of buying up to three times
# and selling once or twice depending on how many times we bought
import talib
import websocket
import numpy
import binance
import json
import pprint
import config
from binance.client import Client
from binance.enums import *

SOCKET = "wss://stream.binance.us:9443/ws/maticusd@kline_1m"

RSI_PERIOD = 14
RSI_OVERBOUGHT = 72
RSI_OVERSOLD = 35
TRADE_SYMBOL = "MATICUSD"
TRADE_QUANTITY1 = 125
TRADE_QUANTITY2 = 85
TRADE_QUANTITY3 = 125
TRADE_QUANTITY4 = 333
TRADE_QUANTITY5 = 208

closes = []
buy_points = []
buy_points2 = []
buy_points3 = []
sell_points = []
in_position = False
in_position2 = True
in_position3 = True
logic1 = False
logic2 = False
logic3 = False

client = Client(config.API_KEY, config.API_SECRET, tld='us')


def order(side, quantity, symbol,  order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_order(
            symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)

    except Exception as e:
        return False

    return True


def on_open(ws):
    print('opened connection')


def on_close(ws):
    print('closed connection')


def on_message(ws, message):
    global buy_points
    global buy_points2
    global buy_points3
    global closes
    global in_position3
    global in_position2
    global in_position
    global RSI_PERIOD
    global RSI_OVERBOUGHT
    global RSI_OVERSOLD
    global TRADE_SYMBOL
    global TRADE_QUANTITY2
    global TRADE_QUANTITY3
    global TRADE_QUANTITY4
    global logic1
    global logic2
    global logic3

    print('recieved message')
    json_message = json.loads(message)
    pprint.pprint(json_message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']

    if is_candle_closed:

        print("candle closed at {}".format(close))
        closes.append(float(close))
        print("closes")
        print(closes)

        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            print("all rsis calculated so far")
            print(rsi)
            last_rsi = rsi[-1]
            print("the current rsi is {}".format(last_rsi))
            if last_rsi < RSI_OVERSOLD:

                if in_position:
                    print("it is oversold, but you already own it, nothing to do.")
                else:
                    print("Oversold! BUY! BUY! BUY!")
                    # put binance order logic here
                    order_succeeded = order(
                        SIDE_BUY, TRADE_QUANTITY1, TRADE_SYMBOL)
                    if order_succeeded:
                        buy_points.append(float(close))
                        in_position = True

            if last_rsi < RSI_OVERSOLD:
                if in_position2:
                    u = buy_points[-1]*.1
                    new = buy_points[-1]-u
                    if float(close) <= new:
                        print("Oversold! BUY! BUY! BUY!")
                        # put binance order logic here
                        order_succeeded = order(
                            SIDE_BUY, TRADE_QUANTITY2, TRADE_SYMBOL)
                        if order_succeeded:
                            buy_points2.append(float(close))
                            logic1 = True

            if last_rsi < RSI_OVERSOLD:
                if in_position3:
                    u_u = buy_points2[-1]*.1
                    new_new = buy_points2[-1]-u_u
                    if float(close) <= new_new:
                        print("Oversold! BUY! BUY! BUY!")
                        # put binance order logic here
                        order_succeeded = order(
                            SIDE_BUY, TRADE_QUANTITY3, TRADE_SYMBOL)
                        if order_succeeded:
                            buy_points3.append(float(close))
                            logic2 = True

            if last_rsi > RSI_OVERBOUGHT:
                if float(close) > buy_points[-1]:
                    if in_position:
                        if logic1:
                            if logic2:

                                print("Overbought! SELL! SELL! SELL!")
                                # put binance sell logic here
                                order_suceeded = order(
                                    SIDE_SELL, TRADE_QUANTITY4, TRADE_SYMBOL)
                                if order_suceeded:
                                    sell_points.append(float(close))
                                    in_position = False

                    elif in_position:
                        if logic1:
                            print("Overbought! SELL! SELL! SELL!")
                            # put binance sell logic here
                            order_suceeded = order(
                                SIDE_SELL, TRADE_QUANTITY5, TRADE_SYMBOL)
                            if order_suceeded:
                                sell_points.append(float(close))
                                in_position = False
                    elif in_position:
                        if logic1 == False:
                            if logic2 == False:
                                print("Overbought! SELL! SELL! SELL!")
                                # put binance sell logic here
                                order_suceeded = order(
                                    SIDE_SELL, TRADE_QUANTITY1, TRADE_SYMBOL)
                                if order_suceeded:
                                    sell_points.append(float(close))
                                    in_position = False

                else:
                    print('current price is higher than what we bought at. do nothing ')


ws = websocket.WebSocketApp(SOCKET, on_open=on_open,
                            on_close=on_close, on_message=on_message)
ws.run_forever()
