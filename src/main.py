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


@app.route('/')
def index():
    return Response('Hello, World!', mimetype='text/plain', status=200)

@app.route('/open_position', methods=["POST"])
@decorator_ip_restrictor
def open_position():
    body = request.json

    symbol = body['symbol']
    equity = body['equity']

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
    return response



if __name__ == '__main__':
    # get api keys from environment variables
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("SECRET_KEY")
    trading_client = TradingClient(api_key, api_secret, paper=True)
    crypto_client = CryptoHistoricalDataClient()
    account = trading_client.get_account()
    # TradingView IP addresses
    authorized_ip = ["52.89.214.238", "34.212.75.30", "54.218.53.128", "52.32.178.7"]

    app.run(port=5000, debug=DEBUG)