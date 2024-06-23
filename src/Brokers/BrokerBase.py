class BrokerBase():
    def __init__(self, brokerConfig):
        self.brokerConfig = brokerConfig

    def open_position(self, symbol, side):
        pass

    def close_position(self, symbol, side):
        pass

    def get_open_positions(self):
        pass

    def get_account(self):
        pass

    def get_account_equity(self):
        pass

    def get_account_cash(self):
        pass

    def get_account_buying_power(self):
        pass

    def get_account_value(self):
        pass