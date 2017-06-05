import time
from abc import ABCMeta, abstractmethod
from mixins import ConfigMixin

class Client(ConfigMixin):
    __metaclass__ = ABCMeta

    def __init__(self, api_key, api_secret, **kwargs):
        self.api_key = api_key
        self.api_secret = api_secret
        self.nonce = int(time.time())
        self.kwargs = kwargs
        self.config = self._get_config()['exchanges'][self.__class__.__name__]['client']

    @abstractmethod
    def get_ticker(self):
        """
        A stock ticker is a report of the price for 'Bitcoin',
        updated continuously throughout the trading session by the stock exchanges.

        A "tick" is any change in price,
        whether that movement is up or down.

        client must implement this function to get the latest tick's
        from the exchange

        :return:
        """
        raise NotImplemented

    @abstractmethod
    def get_tickers(self):
        """
        Get group of tickers , user get_ticket helper function
        to implement this function
        :return:
        """
        raise NotImplemented

    def get_tickers_async(self):
        client_thread = Thread(target=self.get_tickers)
        client_thread.start()

