import talib
import websocket
import numpy
import binance
import json
import pprint
from binance.client import Client
from binance.enums import *
# you need to create a file named config.py file that includes your Binance API KEY & Secret
# then import that file here
# name them API_KEY and API_SECRET then pass them a string with your key & secret to use

SOCKET = "wss://stream.binance.us:9443/ws/dogeusd@kline_1m"
# this socket connects us to the binance api to get price data
# to change the coin pice change the name above from doge usd
# you can also change the 1m(1 minute) candle stick to 5m, 15, 30m etc.

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
# RSI is one of the simpler indicators to use for trading
# visit https://en.wikipedia.org/wiki/Relative_strength_index
# to understand how the RSI indicator works
TRADE_SYMBOL = "DOGEUSD"
TRADE_QUANTITY = 8000
# Change the name of coin you want to trade and quantity you want to buy & sell

closes = []
buy_points = []
in_position = False
# we will need the empty arrays and boolean value in the on_message function
file_object = open("data.txt", "w")
# create a file called data.txt to write your data into

client = Client(config.API_KEY, config.API_SECRET, tld='us')
# this connects us to our binance account


def order(side, quantity, symbol,  order_type=ORDER_TYPE_MARKET):
    # this function is designed to place a buy or sell order on the binance exchange
    # the binance library requires these arguments to complete the orders
    # we will fill these arguments in the on_message function
    global file_object

    try:
        print("sending order")
        file_object.write("sending order")
        order = client.create_order(
            symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
        file_object.write(str(order))

    except Exception as e:
        return False

    return True

# websockets requires open and close arguments and we print verifying the state of the bot


def on_open(ws):
    print('opened connection')
    file_object.write("opened conncetion")


def on_close(ws):
    print('closed connection')
    file_object.write("closed connection")


def on_message(ws, message):
    # in this function we will write and tell the bot exactly what we need it to do
    global buy_points
    global closes
    global in_position
    global RSI_PERIOD
    global RSI_OVERBOUGHT
    global RSI_OVERSOLD
    global TRADE_SYMBOL
    global TRADE_QUANTITY

    print('recieved message')
    file_object.write("recieved message")
    json_message = json.loads(message)
    pprint.pprint(json_message)
    # dont need to write this data into data.txt

    candle = json_message['k']
    is_candle_closed = candle['x']
    close = candle['c']
    # getting price and boolean values from candles

    if is_candle_closed:

        print("candle closed at {}".format(close))
        file_object.write("candle closed at {}".format(close))

        closes.append(float(close))
        print("closes")
        file_object.write("closes")
        print(closes)
        file_object.write(closes)
        # after collecting price data we will finally use the rsi indicator
        # indicator needs 14 total price data

        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            print("all rsis calculated so far")
            file_object.write("all rsis calculated so far")

            print(rsi)
            file_object.write(rsi)

            last_rsi = rsi[-1]
            print("the current rsi is {}".format(last_rsi))
            file_object.write("the current rsi is {}" .format(last_rsi))
            # if RSI is less than 30 we buy
            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    print("it is oversold, but you already own it, nothing to do.")
                    file_object.write(
                        "it is oversold, but you already own it, nothing to do.")

                else:
                    print("Oversold! BUY! BUY! BUY!")
                    file_object.write("Oversold! BUY! BUY! BUY!")
                    # put binance order logic here
                    order_succeeded = order(
                        SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        buy_points.append(float(close))
                        in_position = True
                        print("we bought!")
                        file_object.write("we bought!")
            # if RSI is more than 70 we sell
            if last_rsi > RSI_OVERBOUGHT:
                if float(close) > buy_points[-1]:
                    if in_position:
                        print("Overbought! SELL! SELL! SELL!")
                        # put binance sell logic here
                        order_suceeded = order(
                            SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                        if order_suceeded:
                            in_position = False
                            print("we sold")
                            file_object.write("we sold")

                    else:
                        print(
                            "it is overbought, but we don't own any, nothing to do.")
                        file_object.write(
                            "it is overbought, but we don't own any, nothing to do.")

                else:
                    print('current price is higher than what we bought at. do nothing ')
                file_object.write(
                    "current price is higher than what we bought at. do nothing")


ws = websocket.WebSocketApp(SOCKET, on_open=on_open,
                            on_close=on_close, on_message=on_message)
# here we get the socket we're connecting to and run the bot forever(until we end it)
# you can also create a function to end bot until it makes a certain amount of profit
ws.run_forever()
