from . import Client
import requests
from requests.compat import urljoin


class Bit2c(Client):
    """
    Bit2C exchange client
    """
    def __init__(self, api_key=None, api_secret=None, **kwargs):
        super(Bit2c, self).__init__(api_key, api_secret, **kwargs)

    def get_ticker(self, pair_name='BTN_NIS'):
        url = urljoin(
            self.config['base_url'],
            '{}/{}/Ticker.json'.format(
                self.config['url_paths']['exchanges'],
                self.config['relevant_pairs'][pair_name]))
        resp = requests.get(url)
        return resp.json()

    def get_tickers(self):
        tickers = {}
        for pair_name in self.config['relevant_pairs']:
            tickers[pair_name] = self.get_ticker(pair_name=pair_name)
        return tickers





