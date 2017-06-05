import time
from abc import ABCMeta, abstractmethod
from mixins import ConfigMixin
from collections import defaultdict



def _makehash():
    """
    Helper function to construct multidimensional dictionaries

    e.g myhash = _makehash()
        myhash[1][2] = 4
        myhash[2][5][8] = 17

    :return:
        recursive default dictionary
    """
    return defaultdict(_makehash)

class Parser(ConfigMixin):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.config = self._get_config()['exchanges'][self.__class__.__name__]['parser']

    def convert_headers(self, tickers):
        """
        Convert headers of fetched tickers to same format for convenient data storage in Database.

        This method assumes that parser's headers are configured properly(headers_dict),
        if one of the headers is missing in config file - exception raised

        :param tickers: {'PAIR_NAME':{header: value},...}
            data imported from exchange

        :return:
            same data with converted headers
        """

        result = _makehash()
        for pair_name, fetched_values_dict in tickers.items():
            for header, value  in fetched_values_dict.items():
                result[pair_name][self.config['headers'][header]] = value
        return result

    @abstractmethod
    def parse_tickers(self,tickers):
        raise NotImplemented


