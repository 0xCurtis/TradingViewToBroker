from flask import Flask, Response, request, json
from functools import wraps
import dotenv
import os
# Alapaca imports
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoLatestQuoteRequest

import sqlite3

dotenv.load_dotenv()
app = Flask(__name__)
DEBUG = True

def decorator_ip_restrictor(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not DEBUG:
            print(request.remote_addr)
            if request.remote_addr not in authorized_ip:
                return Response('Unauthorized', status=401)
        return func(*args, **kwargs)
    return wrapper

def open_alpaca_position(symbol, equity, side):
    request_params = CryptoLatestQuoteRequest(symbol_or_symbols=symbol)

    latest_quote = crypto_client.get_crypto_latest_quote(request_params)

    last_quote = latest_quote[symbol].ask_price
    qty = equity / last_quote
    market_order_data = MarketOrderRequest(
                    symbol=symbol,
                    qty=qty,
                    side=side,
                    time_in_force=TimeInForce.GTC
                    )
    return(trading_client.submit_order(
                order_data=market_order_data
               ))

def close_alpaca_position(symbol, side):
    positions = get_open_positions()
    for position in positions:
        if position.symbol == symbol:
            qty = position.qty
            market_order_data = MarketOrderRequest(
                    symbol=symbol,
                    qty=qty,
                    side=side,
                    time_in_force=TimeInForce.GTC
                    )
            return(trading_client.submit_order(
                order_data=market_order_data
               ))
    return None

@app.route('/')
def index():
    return Response('Hello, World!', mimetype='text/plain', status=200)

@app.route('/close_position', methods=["POST"])
@decorator_ip_restrictor
def close_position():
    body = request.json

    symbol = body['symbol']
    if body['side'] == "BUY":
        order_side = OrderSide.SELL
    elif body['side'] == "SELL":
        order_side = OrderSide.BUY
    else:
        return Response('Invalid side', status=400)
    order = close_alpaca_position(symbol, order_side)
    data = {"Order ID": order.id, "Quantity": order.qty, "Symbol": order.symbol, "Side": order.side}

    response = app.response_class(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )
    # add the trade to the database
    db = connect_database()
    cursor = db.cursor()
    # update the trade to closed
    cursor.execute('''UPDATE trades SET closed = 1 WHERE symbol = ? AND closed = 0''', (symbol,))
    db.commit()
    return response

@app.route('/open_position', methods=["POST"])
@decorator_ip_restrictor
def open_position():
    body = request.json

    symbol = body['symbol']
    # for equity take the amount of money available in the account and take 5%
    equity = float(trading_client.get_account().equity) * 0.05
    
    if body['side'] == "BUY":
        order_side = OrderSide.BUY
    elif body['side'] == "SELL":
        order_side = OrderSide.SELL
    else:
        return Response('Invalid side', status=400)
    order = open_alpaca_position(symbol, equity, order_side)
    data = {"Order ID": order.id, "Quantity": order.qty, "Symbol": order.symbol, "Side": order.side}

    response = app.response_class(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )
    # add the trade to the database
    db = connect_database()
    cursor = db.cursor()
    cursor.execute('''INSERT INTO trades (symbol, quantity, side, price, date) VALUES (?, ?, ?, ?, ?)''', (symbol, order.qty, order.side, order.filled_avg_price, order.created_at))
    db.commit()
    return response

@app.route('/get_positions', methods=["GET"])
def get_positions():
    positions = get_open_positions()
    data = []
    for position in positions:
        data.append({"Symbol": position.symbol, "Quantity": position.qty, "Market Value": position.market_value})
    response = app.response_class(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )
    return response

def init_database():
    # create if not exist a table trades with columns id, symbol, quantity, side, price, date
    conn = sqlite3.connect('trades.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS trades (id INTEGER PRIMARY KEY, symbol TEXT, quantity REAL, side TEXT, price REAL, date TEXT, bool closed DEFAULT 0)''')
    conn.commit()
    return conn

def get_open_positions():
    return trading_client.get_all_positions()

def connect_database():
    return sqlite3.connect('trades.db')

if __name__ == '__main__':
    # get api keys from environment variables
    db = init_database()
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("SECRET_KEY")
    trading_client = TradingClient(api_key, api_secret, paper=True)
    crypto_client = CryptoHistoricalDataClient()
    # TradingView IP addresses
    authorized_ip = ["52.89.214.238", "34.212.75.30", "54.218.53.128", "52.32.178.7"]

    app.run(port=5000, debug=DEBUG)