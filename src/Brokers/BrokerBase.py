from abc import ABC, abstractmethod

class BrokerBase(ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        abstract_methods = {
            name for name, value in self.__class__.__dict__.items()
            if getattr(value, "__isabstractmethod__", False)
        }
        implemented_methods = {
            name for name in dir(self)
            if callable(getattr(self, name))
        }
        missing_methods = abstract_methods - implemented_methods
        if missing_methods:
            raise TypeError(
                f"Can't instantiate abstract class {self.__class__.__name__} with abstract methods: " +
                ", ".join(missing_methods)
            )

    @abstractmethod
    def open_position(self, symbol, side):
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def close_position(self, symbol, side):
        raise NotImplementedError("Method not implemented")
    
    @abstractmethod
    def get_open_positions(self):
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def get_account(self):
        raise NotImplementedError("Method not implemented")

    def get_account_equity(self):
        raise NotImplementedError("Method not implemented")

    def get_account_cash(self):
        raise NotImplementedError("Method not implemented")

    def get_account_buying_power(self):
        raise NotImplementedError("Method not implemented")

    def get_account_value(self):
        raise NotImplementedError("Method not implemented")

class IncompleteBroker(BrokerBase):
    
    def open_position(self):
        print("Opening position")

if __name__ == "__main__":
    broker = IncompleteBroker()