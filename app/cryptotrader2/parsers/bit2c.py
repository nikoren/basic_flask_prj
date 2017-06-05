from . import Parser

class Bit2c(Parser):
    def __init__(self):
        super(Bit2c, self).__init__()

    def parse_tickers(self, tickers):
        print self.convert_headers(tickers)