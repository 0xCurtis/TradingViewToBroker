from .Brokers import BrokerBase

class Account():

    # Singleton pattern
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Account, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self, broker : BrokerBase):
        self._broker = broker()

    def open_position(self, symbol, side):
        return self._broker.open_position(symbol, side)
    