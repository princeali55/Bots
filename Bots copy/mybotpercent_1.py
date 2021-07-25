# to understand how this bot works refer to MainRSIbot.py
import talib
import websocket
import numpy
import binance
import json
import pprint
import config
from binance.client import Client
from binance.enums import *
import smtplib
from email.message import EmailMessage

SOCKET = "wss://stream.binance.us:9443/ws/maticusd@kline_1m"

TRADE_SYMBOL = "MATICUSD"
TRADE_QUANTITY = 60


closes = []

currentPrice = 1.1602

bought = 0
thirteenUp = 0
# change currentPrice to the price of the coin on binance exchange
# change TRADE_QUANTITY to the amount of coins you want to buy and sell



in_position = False

file1 = open("data2.txt", "w")

client = Client(config.API_KEY, config.API_SECRET, tld='us')


def order(side, quantity, symbol,  order_type=ORDER_TYPE_MARKET):
    global file1
    try:
        print("sending order")
        file1.write("sending order")
        order = client.create_order(
            symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
        file1.write(str(order))

    except Exception as e:
        print("order failed")
        file1.write("order failed")
        return False

    return True


def email_alert(subject, body, to):
    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to

    user = "" # input your email here
    msg['from'] = user
    password = "" # input your password here
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)

    server.quit()


def on_open(ws):
    global file1
    print('opened connection')
    file1.write('opened connection')


def on_close(ws):
    global file1
    print('closed connection')
    file1.write('\nclosed connection')


def on_message(ws, message):
    global bought
    global random
    global closes
    global in_position
    global TRADE_SYMBOL
    global TRADE_QUANTITY
    global file1
    global currentPrice
    global thirteenUp

    print('recieved message')
    json_message = json.loads(message)
    pprint.pprint(json_message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']

    if is_candle_closed:

        print("candle closed at {}".format(close))
        file1.write("\ncandle closed at {}".format(close))
        closes.append(float(close))
        print("closes")
        file1.write("\ncloses\n")
        print(closes)
        file1.write(str(closes))
        # change the 1.13 or the .13 to change the percentage change
        # right now its at 13 percent
        down_percent = currentPrice * 0.13
        thirteenDown = currentPrice - down_percent

        if float(close) <= thirteenDown:
            if in_position:
                print("it is oversold, but you already own it, nothing to do.")
                file1.write(
                    "\nit is oversold, but you already own it, nothing to do.")
            else:
                print("Oversold! BUY! BUY! BUY!")
                file1.write("\nOversold! BUY! BUY! BUY!")
                # put binance order logic here
                order_succeeded = order(
                    SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                if order_succeeded:
                    email_alert("Bought", "Bought", "4127086542@txt.att.net")
                    file1.write("we bought")
                    in_position = True
                    bought = float(close)
                    thirteenUp = bought * 1.13

        if float(close) >= thirteenUp:
            if in_position:
                print("Overbought! SELL! SELL! SELL!")
                file1.write("\nOVERBOUGHT! SELL SELL SELL")
                # put binance sell logic here
                order_suceeded = order(
                    SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                if order_suceeded:
                    email_alert("Sold", "Sold", "4127086542@txt.att.net")
                    file1.write("we sold")
                    in_position = False
                    currentPrice = float(close)

ws = websocket.WebSocketApp(SOCKET, on_open=on_open,
                            on_close=on_close, on_message=on_message)
ws.run_forever()
